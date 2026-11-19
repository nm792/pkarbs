# CHUNK D (P15d): run the Goalserve bet365 esports odds vs Polymarket price test. Read-only. 17 Nov 2026 12:50Z

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread tests whether Goalserve odds lead the Polymarket price.

**2. Where we stand.** No Goalserve odds have been timed against the Polymarket price yet. The test code is signed by an independent project thread (the "Audit CS2 model" thread), all rows MATCH, for commit 1cb5c8474b1f64040ec0a8978d866f5b5bc43e2e (PR #397); record in its reviews/SIGNOFF-goalserve-odds-vs-pm-rule-to-code-2026-11-17.md and feeds/SIGNATURE-goalserve-bet365-esports-odds-vs-pm-2026-11-17.md (that file names c82acb04, now superseded by 1cb5c847). Deviation approved by Nick 17 Nov 08:33:16Z. Inputs: your P15d0 (Prime 0582e59a), P15d1 (agent/status/goalserve.md "P15d1 evidence addendum"), P15b (Prime 026be71f).

**3. The one item that matters.** Run all four commands below in order and post the files. Results stay UNCHECKED until an independent audit; do not interpret them.

**Why four runs.** Run 1 is the real run (PM shift 0). Runs 2 to 4 repeat it with the Polymarket book times moved later by 5, 15 and 25 s (a planted edge on the real series, `--pm-shift-s`), as the checker requires in the same report.

**Gate before anything:** data-disk free must be above 20 GB (the temp copy is the Goalserve esports hour files from the box, a few hundred MB to about 1 GB). If not, stop and post the `df` line.

**Commands (one shell session, repo checkout; do not echo RSYNC_RSH or BOX_ROOT):**
```bash
set -u
cd /root/pkarbs && git pull --ff-only
T=/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-odds-vs-pm-20261117
V=/mnt/HC_Volume_107257520
date -u +%FT%TZ; df -B1 --output=avail $V | tail -1
[ "$(df -B1 --output=avail $V | tail -1)" -gt 20000000000 ] || { echo "STOP: data disk free below 20 GB"; exit 1; }
sha256sum feeds/goalserve_odds_vs_pm.py feeds/test_goalserve_odds_vs_pm.py feeds/ps_lead_test.py
git log -1 --format=%H -- feeds/goalserve_odds_vs_pm.py
python3 -m py_compile feeds/goalserve_odds_vs_pm.py && echo COMPILE_OK
python3 -I feeds/test_goalserve_odds_vs_pm.py | tail -4
mkdir -p $T/gs
rsync -a --include='esports_*.jsonl.gz' --exclude='*' -e "$RSYNC_RSH" "$BOX_ROOT/pkarbs/goalserve/esports_payloads/" $T/gs/
cp -n $V/pkarbs/goalserve/esports_payloads/esports_*.jsonl.gz $T/gs/
ls $T/gs | wc -l; ls $T/gs | head -1; ls $T/gs | tail -1; du -sh $T/gs
for S in 0 5 15 25; do
  nice -n 10 ionice -c3 timeout 7200 python3 -I feeds/goalserve_odds_vs_pm.py \
    --files "$T/gs/esports_*.jsonl.gz" \
    --pm $V/pkarbs/thesports/final-topics-32295b \
    --poll-log "$V/pkarbs/goalserve/goalserve_2026111*.jsonl" \
    --clock-note "Polymarket recorder and Goalserve capture both run on Prime; chrony last offset +0.000032 s at 10:57:49Z (synchronized, stratum 3). Single-host reading, not a cross-machine offset." \
    --pm-shift-s $S --out $T/result-shift$S.json > $T/run-shift$S.log 2>&1
  echo "shift $S exit $? at $(date -u +%FT%TZ)"
done
ls -l $T/result-shift*.json
```
The test line must print `ALL PASS` (about 100 s). The rsync uses the same route as the shipper (as in P15d1). `cp -n` never overwrites a box copy; closed local hours not yet shipped are added. Mixed-time ordering is safe because all files sit in one directory and sort by hour in the name.

**Output to post (append to agent/status/goalserve.md under `## P15d run (17 Nov)`):** the date lines and `df` line; the three sha256 lines and the git log hash; COMPILE_OK; the test tail; the file count, first and last name and `du -sh`; the four `shift S exit N at TIME` lines; `ls -l` of the four result files. Then copy the four JSONs (they hold no credentials) to `agent/status/goalserve-odds-vs-pm-result-2026-11-17-shift0.json`, `-shift5.json`, `-shift15.json`, `-shift25.json`. Leave `$T` in place (the audit reads it); report its size.

**Done check:** four result JSON files exist and are larger than 1 KB; each `shift S exit 0`; if any exit is not 0, paste the last 15 lines of its run-shiftS.log verbatim and stop.

**Do not:** change any script, process, config or capture; start any other job on the data volume while it runs (the Polymarket books file is about 19 GB and is read four times).
