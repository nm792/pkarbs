#!/bin/bash
# Self test: fake tree where ONE recorder file grows during the gap, one stays still, one dir missing. Ends ALL PASS.
T=$(mktemp -d); H=$(dirname "$0"); fails=0
mkdir -p $T/pkarbs/goalserve/esports_payloads $T/pkarbs/goalserve/tennis_payloads $T/pkarbs/pmsport
echo a > $T/pkarbs/goalserve/esports_payloads/esports_2026112200.jsonl.gz
echo a > $T/pkarbs/goalserve/tennis_payloads/tennis_2026112200.jsonl.gz
echo a > $T/pkarbs/pmsport/books.jsonl.gz
( sleep 1; echo more >> $T/pkarbs/pmsport/books.jsonl.gz ) &
out=$(V=$T GAP=3 bash $H/read_all_recorders.sh)
echo "$out"
echo "$out" | grep -E '^pmsport_nhl .*GREW\+5' >/dev/null && echo "PASS pmsport growth detected" || { echo "FAIL pmsport growth"; fails=1; }
echo "$out" | grep -E '^goalserve_esports .*UNCHANGED' >/dev/null && echo "PASS still file reported UNCHANGED" || { echo "FAIL unchanged"; fails=1; }
echo "$out" | grep -E '^pmcs2 .*NO FILE' >/dev/null && echo "PASS missing dir reported" || { echo "FAIL missing dir"; fails=1; }
echo "$out" | grep -E '^VOL2 free bytes: [0-9]+' >/dev/null && echo "PASS VOL2 line" || { echo "FAIL vol2"; fails=1; }
rm -rf $T; [ $fails = 0 ] && echo "ALL PASS" || { echo FAILED; exit 1; }
