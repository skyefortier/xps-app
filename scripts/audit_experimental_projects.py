"""Read-only inventory/consistency audit of user-selected Run 5+ projects.

Outputs hashes and metrics, never raw intensity arrays. Keep its output outside
the repository: filenames and derived metrics may be unpublished research.
Saved fits are comparison records, not independent scientific truth.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from autofit.parity import evaluate_model
from autofit.reference import peak_to_backend_spec


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    files=[]; records=[]; shapes=Counter(); backgrounds=Counter(); hashes=Counter()
    for folder in sorted(args.root.glob('Run *')):
        try: run=int(folder.name.split()[1])
        except ValueError: continue
        if run<5: continue
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or not path.name.endswith(('.proj.zip','.proj.json','.spec.json')): continue
            file_record=dict(run=run,path=str(path.relative_to(args.root)))
            try:
                blob=path.read_bytes()
                file_record.update(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
                if path.suffix=='.zip':
                    with zipfile.ZipFile(path) as archive:
                        manifest=json.loads(archive.read('manifest.json'))
                        tabs=[json.loads(archive.read(item['filename'])) for item in manifest.get('spectra',[])]
                else:
                    data=json.loads(blob);tabs=data.get('tabs',[data])
                file_record['readable']=True
                for index,tab in enumerate(tabs):
                    if tab.get('isStack') or not tab.get('rawBE'): continue
                    row=dict(run=run,project=file_record['path'],tab_index=index,name=tab.get('name'),issues=[])
                    x=np.asarray(tab['rawBE'],dtype=float); y=np.asarray(tab.get('rawIntensity',[]),dtype=float)
                    row['points']=len(x)
                    if x.shape!=y.shape or x.ndim!=1 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
                        row['issues'].append('invalid_or_mismatched_raw_arrays');records.append(row);continue
                    digest=hashlib.sha256(x.tobytes()+y.tobytes()).hexdigest()
                    row['raw_array_sha256']=digest;hashes[digest]+=1
                    dx=np.diff(x)
                    if len(dx) and not (np.all(dx>0) or np.all(dx<0)):row['issues'].append('nonmonotonic_or_duplicate_energy')
                    row['uniform_grid']=bool(len(dx) and np.allclose(dx,dx[0],rtol=1e-5,atol=1e-8))
                    row['negative_intensity_points']=int(np.sum(y<0))
                    peaks=tab.get('peaks') or [];fr=tab.get('fitResult') or {}
                    row['peak_count']=len(peaks);row['has_saved_fit']=bool(fr)
                    for p in peaks:shapes[p.get('shape','unknown')]+=1
                    backgrounds[(tab.get('ui') or {}).get('bgType','unspecified')]+=1
                    be=np.asarray(fr.get('be') or [],dtype=float)
                    fy=np.asarray(fr.get('fittedY') or [],dtype=float)
                    bg=np.asarray(fr.get('bgIntensity') or [],dtype=float)
                    row['has_persisted_backend_diagnostics']=bool(fr.get('backendResult'))
                    row['has_peak_parameter_records']=any(bool(p.get('_backendParams')) for p in peaks)
                    if len(fy) and (len(fy)!=len(be) or len(bg)!=len(be)):
                        row['issues'].append('saved_fit_grid_or_background_missing_or_mismatched')
                    if len(be)>1:
                        corrected=x-float(tab.get('ccShift') or 0)
                        # Nearest raw sample in corrected frame: no assumption
                        # that the current ROI still equals the fit-time ROI.
                        distances=np.min(np.abs(be[:,None]-corrected[None,:]),axis=1)
                        row['max_saved_grid_distance_from_current_axis_ev']=float(distances.max())
                    if peaks and len(be)>1 and len(fy)==len(be) and len(bg)==len(be):
                        try:
                            # Mirror explicit frontend alias migration in
                            # memory; the source project is never changed.
                            aliases={'LA':'DSG_LA','DSG':'DS'}
                            migrated=[dict(p,shape=aliases.get(p.get('shape'),p.get('shape'))) for p in peaks]
                            known={'Gaussian','Lorentzian','GL','Voigt','asym-GL','DS','DSG_LA','LACX'}
                            if any(p.get('shape') not in known for p in migrated):
                                raise ValueError('Unknown shape: cannot safely reconstruct')
                            row['migrated_legacy_shape_count']=sum(p.get('shape') in aliases for p in peaks)
                            specs=[peak_to_backend_spec(p,migrated) for p in migrated]
                            prediction=evaluate_model(be,specs)+bg
                            scale=max(float(np.max(np.abs(fy-bg))),1)
                            row['backend_reconstruction_max_peak_fraction_error']=float(np.max(np.abs(prediction-fy))/scale)
                            row['comparison_note']='Current backend/parameter mapping versus saved envelope with saved background; a discrepancy is not proof the experimental fit is wrong.'
                        except Exception as exc:row['reconstruction_error']=type(exc).__name__+': '+str(exc)
                    records.append(row)
            except Exception as exc:file_record.update(readable=False,error=type(exc).__name__+': '+str(exc))
            files.append(file_record)
    compared=[r for r in records if 'backend_reconstruction_max_peak_fraction_error' in r]
    summary=dict(files=len(files),readable_files=sum(f.get('readable',False) for f in files),
                 spectrum_records=len(records),unique_raw_arrays=len(hashes),
                 fitted_records=sum(r.get('has_saved_fit',False) for r in records),
                 reconstructed_records=len(compared),
                 reconstruction_above_one_percent=sum(r['backend_reconstruction_max_peak_fraction_error']>.01 for r in compared),
                 nonuniform_records=sum(not r.get('uniform_grid',True) for r in records),
                 issue_counts=dict(Counter(i for r in records for i in r['issues'])),
                 peak_shapes=dict(shapes),backgrounds=dict(backgrounds))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(summary=summary,files=files,records=records),indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
