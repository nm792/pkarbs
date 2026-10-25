#!/bin/bash
# pkarbs rescan-clean: 7 sim passes
set -u
cd /root/pkarbs
PY=/root/nautilus/venv/bin/python3
DATA=/mnt/HC_Volume_107257520/pkarbs/shadow/rescan-data
RUNS=shadow/rescan-clean/runs.jsonl
OUT=reports/sports-mece
mkdir -p "$OUT"
run() {
  local name="$1"; shift
  echo "=== $name start $(date -u +%FT%TZ) ==="
  $PY shadow/shadow_sim.py --data "$DATA" --runs "$RUNS" --one-way 0.0019 --delays 0,1,3,market --max-usd 500 --gap-s 5 "$@" --per-run "$OUT/rescan-clean-2026-10-24-$name.csv" 2>&1
  echo "=== $name done rc=$? $(date -u +%FT%TZ) ==="
}
run usdc-cd10 --min-unit usdc --cooldown-s 10 --taker-rebate 0
run usdc-cd0  --min-unit usdc --cooldown-s 0  --taker-rebate 0
run shares-cd10 --min-unit shares --cooldown-s 10 --taker-rebate 0
run shares-cd0  --min-unit shares --cooldown-s 0  --taker-rebate 0
run usdc-cd10-rb03 --min-unit usdc --cooldown-s 10 --taker-rebate 0.03 --delays market
run usdc-cd10-rb08 --min-unit usdc --cooldown-s 10 --taker-rebate 0.08 --delays market
run usdc-cd10-rb18 --min-unit usdc --cooldown-s 10 --taker-rebate 0.18 --delays market
echo "ALL SIMS DONE $(date -u +%FT%TZ)"
