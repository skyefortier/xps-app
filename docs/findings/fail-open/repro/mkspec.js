// usage: node mkspec.js <spec.json> -> prints {be, inten, peaks:[specs], ui}
const fs=require('fs'),path=require('path');
const html=fs.readFileSync('/Users/skyefortier/xps-app/templates/index.html','utf8').split('\n');
function extractFn(name){const re=new RegExp('^(async )?function '+name+'\\(');const s=html.findIndex(l=>re.test(l));let d=0,seen=false;for(let i=s;i<html.length;i++){for(const ch of html[i]){if(ch==='{'){d++;seen=true}else if(ch==='}')d--}if(seen&&d===0)return html.slice(s,i+1).join('\n')}}
const state={peaks:[]};
const env=new Function('state',['getPeak','peakToBackendSpec','_bgWindowIndices'].map(extractFn).join('\n')+'\nreturn {peakToBackendSpec,_bgWindowIndices};')(state);
const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
state.peaks=d.peaks;
const shift=d.ccShift||0;
const corr=d.rawBE.map(b=>b-shift);
const lo=parseFloat(d.ui.roiMin), hi=parseFloat(d.ui.roiMax);
const L=isNaN(lo)?-Infinity:lo, H=isNaN(hi)?Infinity:hi;
const be=[],inten=[];
corr.forEach((b,i)=>{if(b>=L&&b<=H){be.push(b);inten.push(d.rawIntensity[i])}});
const w=env._bgWindowIndices(be,d.ui.bgStart,d.ui.bgEnd);
const csv=be.map((e,i)=>e.toFixed(4)+','+inten[i].toFixed(2)).join('\n');
console.log(JSON.stringify({csv, ui:d.ui, peaks:state.peaks.map(env.peakToBackendSpec), bg:{method:d.ui.bgType,start_idx:w.i0,end_idx:w.i1+1,endpoint_avg:parseInt(d.ui.endpointAvg)||1}, rawpeaks:d.peaks.map(p=>({id:p.id,name:p.name,shape:p.shape,linked:p.linked}))}));
