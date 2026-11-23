#!/bin/bash
# Test for nba_health.sh with a fabricated run dir: a good run PASSES; no pid, tokens 0, no growth each FAIL. Run: bash test_nba_health.sh
D="$(cd "$(dirname "$0")" && pwd)"; T=$(mktemp -d); O=$T/o; mkdir -p $O; bad=0
( exec -a "node pm_sport_books.js" sleep 60 ) & P=$!; echo $P > $O/recorder.pid; sleep 0.3
echo '{"slug":"nba-a-b-2026-11-23"}' > $O/markets.jsonl; echo "x ws open, tokens 2" > $O/recorder.log
( for i in 1 2 3 4 5 6; do echo row | gzip >> $O/books.jsonl.gz; sleep 0.4; done ) &
bash $D/nba_health.sh $O 2 > $T/g.txt; [ $? = 0 ] && grep -q "HEALTH PASS" $T/g.txt || { echo "FAIL: good run did not PASS: $(cat $T/g.txt)"; bad=1; }
sleep 3; bash $D/nba_health.sh $O 1 > $T/n.txt; [ $? = 1 ] && grep -q "FAIL growth" $T/n.txt || { echo "FAIL: no-growth not detected"; bad=1; }
echo "x ws open, tokens 0" > $O/recorder.log; bash $D/nba_health.sh $O 1 > $T/t.txt; grep -q "FAIL tokens" $T/t.txt || { echo "FAIL: tokens 0 not detected"; bad=1; }
echo "x ws open, tokens 2" > $O/recorder.log; echo 4242424 > $O/recorder.pid; bash $D/nba_health.sh $O 1 > $T/p.txt; grep -q "FAIL pid" $T/p.txt || { echo "FAIL: dead pid not detected"; bad=1; }
kill $P 2>/dev/null; [ $bad = 0 ] && echo "PASS (4 health checks)"; exit $bad
