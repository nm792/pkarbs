#!/bin/bash
# Test: a RUNNING recorder (pidfile + cmdline containing pm_sport_books) is NOT relaunched; a dead/stale pidfile IS relaunched. Run: bash test_nba_keepalive.sh
D="$(cd "$(dirname "$0")" && pwd)"; T=$(mktemp -d); OUT=$T/o; mkdir -p $OUT; fail=0; END=$(date -u -d '+1 hour' +%FT%TZ)
cp "$D/nba_keepalive.sh" $T/; sleep 30 & # stand-in recorder whose cmdline must contain pm_sport_books: exec -a
( exec -a "node pm_sport_books.js" sleep 30 ) & FAKE=$!; echo $FAKE > $OUT/recorder.pid; sleep 0.3
export START_CMD="echo launched >> $T/launches"
bash $T/nba_keepalive.sh $OUT $END >/dev/null; sleep 0.5
[ -f $T/launches ] && { echo "FAIL: running recorder was relaunched"; fail=1; }
kill $FAKE 2>/dev/null; wait $FAKE 2>/dev/null; sleep 0.3
bash $T/nba_keepalive.sh $OUT $END >/dev/null; sleep 0.5
[ -f $T/launches ] || { echo "FAIL: dead recorder was not relaunched"; fail=1; }
echo 4242424 > $OUT/recorder.pid; rm -f $T/launches   # stale pid
bash $T/nba_keepalive.sh $OUT $END >/dev/null; sleep 0.5
[ -f $T/launches ] || { echo "FAIL: stale pidfile not relaunched"; fail=1; }
rm -f $T/launches; echo $$ > $OUT/recorder.pid   # live pid but NOT the recorder (this shell): must relaunch
bash $T/nba_keepalive.sh $OUT $END >/dev/null; sleep 0.5
[ -f $T/launches ] || { echo "FAIL: unrelated live pid treated as recorder"; fail=1; }
[ $fail = 0 ] && echo "PASS (4 keep-alive checks)"; exit $fail
