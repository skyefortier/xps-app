#!/bin/zsh
# The LA acceptance matrix: the 107 seal-1b LA requests, regenerated and verified in four settings, BEFORE (final 55d99ca; earlier sides 5fad7de,
# np.convolve) and AFTER (1d2b255, the fixed-order convolution). Each code checkout is a clean detached worktree; the
# script is the after checkout's.
M=/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal_la_matrix
SRC=/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/v2/records.jsonl
PY=/Users/skyefortier/xps-app/venv/bin/python
S=$M/code_after/scripts/seal_la_matrix.py
port=5156
for side in final; do
  C=$M/code_$side; O=$M/$side; mkdir -p $O
  echo "$side commit $(git -C $C rev-parse --short HEAD) dirty=$(git -C $C status --porcelain | wc -l) $(date)" >> $M/run.log
  export SEAL_LA_CODE=$C
  $PY $S record $SRC $O/records.jsonl
  $PY $S verify $O/records.jsonl $O/verify_fresh_1.jsonl
  $PY $S verify $O/records.jsonl $O/verify_fresh_2.jsonl
  $PY $S verify $O/records.jsonl $O/verify_shake.jsonl --shake
  (cd $C && /Users/skyefortier/xps-app/venv/bin/gunicorn "app:create_app(upload_folder='$O/gu-uploads')" -w 4 -b 127.0.0.1:$port --timeout 300 > $O/gunicorn.log 2>&1) &
  GPID=$!
  sleep 10
  $PY $S verify $O/records.jsonl $O/verify_gunicorn.jsonl --url http://127.0.0.1:$port
  pkill -f "127.0.0.1:$port" ; wait $GPID 2>/dev/null
  $PY $S provenance $O/records.jsonl $O/provenance.json
  port=$((port+1))
done
echo "DONE $(date)" >> $M/run.log
