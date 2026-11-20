# 00-URGENT to IT, 20 Nov 2026 04:25Z (Goalserve thread; Nick 03:23Z: look at samples of real matches against the feeds). Read-only, a few MB. Put it right after P85/P84a, ahead of P83 and P87.

1. **Goal:** a human-readable sample of RAW Goalserve events for 3 matches each in tennis, CS2, Dota and hockey, committed to the repo so I can chart them against Polymarket trades. Output files are small (winner market only, changes only).
2. **Commands (one block; writes only `scratch/goalserve-desc/samples`):**
```
V=/mnt/HC_Volume_107257520; G=$V/pkarbs/goalserve; D=$V/pkarbs/scratch/goalserve-desc; O=$D/samples; mkdir -p $O
git -C /root/pkarbs fetch -q origin reviewer; for f in export_goalserve_sample.py test_export_goalserve_sample.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $D/$f; done
python3 -I $D/test_export_goalserve_sample.py | tail -2     # must end ALL PASS
python3 -I $D/export_goalserve_sample.py --out $O --sport tennis --n 3 --files "$G/tennis_payloads/tennis_2026111[89]*.jsonl.gz" --files "$G/tennis_payloads/tennis_2026112000.jsonl.gz"
python3 -I $D/export_goalserve_sample.py --out $O --sport esports --game cs2 --n 3 --files "$G/esports_payloads/esports_2026111[89]*.jsonl.gz"
python3 -I $D/export_goalserve_sample.py --out $O --sport esports --game dota2 --n 3 --files "$G/esports_payloads/esports_2026111[89]*.jsonl.gz"
python3 -I $D/export_goalserve_sample.py --out $O --sport hockey_nhl --n 3 --files "$G/hockey_nhl_payloads/hockey_nhl_2026111[789]*.jsonl.gz"
ls -l $O; cat $O/index-*.json | head -60
```
(Hockey: 17-19 Nov; esports/tennis: 18-20 Nov hours that are on local disk. Missing hours are fine, just paste what exists. One scan at a time; stop at your 10 GB floor.)
3. **Deliver to the repo:** paste the `ls -l` and the index JSON under `## P88 match samples (20 Nov)` in `agent/status/goalserve.md`, and commit the `$O/*.jsonl.gz` and `$O/index-*.json` files (should total a few MB) to branch `reviewer` under `it/samples-2026-11-20/` with your usual status-commit procedure. **Do not commit from /root/pkarbs.** If a file is over 5 MB, paste its size and commit the first 5 MB only after `zcat | head -n 4000 | gzip`.
4. **Done check:** the commit hash and `ls -l` pasted; the index lists 3 matches for each of the four sports (or says how many matches existed).
