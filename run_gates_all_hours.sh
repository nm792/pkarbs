#!/bin/bash
# TASK-gates-all-hours: run gates+sim on the 12 newest complete hours, one at a time.
set -u
export LC_ALL=C
cd /root/pkarbs
DATA=/mnt/HC_Volume_107257520/pkarbs/shadow/data-v2
HOURS="2026102421 2026102422 2026102423 2026102500 2026102501 2026102502 2026102503 2026102504 2026102505 2026102506 2026102507 2026102508"
START=$(date +%s)
for HOUR in $HOURS; do
  NOW=$(date +%s)
  ELAPSED=$(( (NOW - START) / 60 ))
  if [ $ELAPSED -ge 120 ]; then echo "STOP: 2h wall clock reached at $HOUR"; break; fi
  echo "=== $HOUR (elapsed ${ELAPSED}m) ==="
  mkdir -p reports/sports-mece/hours/$HOUR
  systemd-run --scope -p MemoryMax=1500M -p MemorySwapMax=0 \
    /usr/bin/time -v timeout 1800 /usr/bin/python3 shadow/test_gates.py --real-data $DATA \
    --hour $HOUR --save reports/sports-mece/hours/$HOUR/ 2>&1 | tee reports/sports-mece/hours/$HOUR/gates.txt
  RC=${PIPESTATUS[0]}
  # on failed hour, delete per-run CSV
  if [ $RC -ne 0 ] || ! grep -q "gates pass" reports/sports-mece/hours/$HOUR/gates.txt; then
    echo "$HOUR FAILED (rc=$RC)"
    rm -f reports/sports-mece/hours/$HOUR/per-run-*.csv
  else
    echo "$HOUR PASS"
  fi
  # commit after every 4 hours
  N=$(ls reports/sports-mece/hours/ | grep -c '^2026')
  if [ $((N % 4)) -eq 0 ]; then
    git add reports/sports-mece/hours/ 2>/dev/null
    git commit -q -m "gates-all-hours: $HOUR done ($N hours)" 2>/dev/null && echo "committed ($N hours)"
  fi
done
# final commit + index
git add reports/sports-mece/hours/ 2>/dev/null
git commit -q -m "gates-all-hours: loop complete" 2>/dev/null
echo "=== DONE ==="
