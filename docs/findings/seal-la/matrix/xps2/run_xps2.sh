#!/bin/bash
# The LA acceptance matrix's AFTER side on xps2 (Linux x86_64, 1 vCPU, OpenBLAS; Python 3.12.3 with the pinned
# libraries of /opt/xps-app/venv, used read-only). The 107 seal-1b LA requests re-fitted there, then verified in the
# four settings. The temporary gunicorn has 2 workers (production's count; 961 MB RAM) on 127.0.0.1:5160, its own
# upload folder; everything runs at nice 19 so production is served first.
set -u
D=/root/seal-la-matrix; C=$D/code; O=$D/after
PY=/opt/xps-app/venv/bin/python; GU=/opt/xps-app/venv/bin/gunicorn
S=$C/scripts/seal_la_matrix.py
mkdir -p $O
echo "after commit $(git -C $C rev-parse --short HEAD) dirty=$(git -C $C status --porcelain | wc -l) $(date)" >> $D/run.log
export SEAL_LA_CODE=$C
nice -n 19 $PY $S record $D/la107_1b.jsonl $O/records.jsonl
nice -n 19 $PY $S verify $O/records.jsonl $O/verify_fresh_1.jsonl
nice -n 19 $PY $S verify $O/records.jsonl $O/verify_fresh_2.jsonl
nice -n 19 $PY $S verify $O/records.jsonl $O/verify_shake.jsonl --shake
(cd $C && nice -n 19 $GU "app:create_app(upload_folder='$O/gu-uploads')" -w 2 -b 127.0.0.1:5160 --timeout 300 > $O/gunicorn.log 2>&1) &
GPID=$!
sleep 15
nice -n 19 $PY $S verify $O/records.jsonl $O/verify_gunicorn.jsonl --url http://127.0.0.1:5160
pkill -f "127.0.0.1:5160"; wait $GPID 2>/dev/null
nice -n 19 $PY $S provenance $O/records.jsonl $O/provenance.json
echo "DONE $(date)" >> $D/run.log
