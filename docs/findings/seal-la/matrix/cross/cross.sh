#!/bin/bash
# cross-machine verification (information): i9-made records verified by xps2 (code 55d99ca, production venv read-only)
export SEAL_LA_CODE=/root/seal-la-matrix/code
PY=/opt/xps-app/venv/bin/python; S=$SEAL_LA_CODE/scripts/seal_la_matrix.py
nice -n 19 $PY $S verify i9_final_records.jsonl cross_i9la_on_xps2.jsonl
nice -n 19 $PY $S verify nonla221_1b.jsonl cross_1bnonla_on_xps2.jsonl
echo CROSSDONE >> run.log
