# To IT, 22 Nov 2026 12:50Z. P105: ONE pmcs2 hour, raw-row plant run on Prime (Reviewer R-042 due 15:00Z; R-039: runs on Prime, not in a session container)

Read-only on the recorders' files. Scratch on VOL2 tmp (SCRATCH RULE), not /tmp. Pinned SHA: reviewer `04efbbee56` (feeds/ps_kills_vs_pmcs2.py, feeds/audit_ps_inround.py, it/ps_export_samples.py). Needs python3 only, no network. Run right after P102 (its coverage output tells which hour); if P102 has not run, choose the newest CLOSED pmcs2 hour whose markets.jsonl has a CS2 match.
1. Pick hour H (YYYYMMDDHH) = a closed `books-H.jsonl[.gz]` in /mnt/HC_Volume_107257520/pkarbs/pmcs2 with CS2 markets. Make `T=$(mktemp -d -p /mnt/HC_Volume_107257520/tmp)`; `mkdir $T/raw`; symlink the PandaScore raw hours H and H-1 (pandascore_YYYYMMDDHH.jsonl.gz, whichever exist and are closed) into $T/raw. Skip the newest growing file.
2. `python3 -I it/ps_export_samples.py $T/raw $T/samples 12`
3. `nice -n 10 python3 -I feeds/ps_kills_vs_pmcs2.py $T/samples /mnt/HC_Volume_107257520/pkarbs/pmcs2 --L 0.5 --plant 0.03 --nplacebo 200 --out $T/result.json`
4. Paste `result.json` (whole) and the first 20 lines of stdout into agent/status/pandascore.md under "## PS P105 (22 Nov)". Also paste: number of matches with both token books, plant recovery value and in_band_95_105, placebo mean. Delete $T afterwards. No restart, no edit of recorder files, no network.
PASS for this row = result.json exists and shows matches_with_both_token_books and plant.recovery. A recovery outside 95-105% is a valid, wanted answer: paste it, do not retry. Zero matches is a valid answer too: paste the list of files read.
Any number from this run is labelled "first Prime run, ONE hour, not evidence" until the spec's stops apply.

Expected write: ~3 MB ONE-OFF, 0 MB/day (basis: step 2 writes at most 12 sample files of 10-450 KB each, measured 2.4 MB for 15 matches in scratch/ps_samples, plus a result.json of about 5 KB; all in VOL2 tmp and deleted at the end of step 4; the scorer reads recorder files and writes nothing there).

R-070(F): restate the kills verdict at the 0.03 fee (0.75c at p 0.5; source: Polymarket gamma feeSchedule rate 0.03 sports_fees_v2 on current CS2 match markets, https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2, checked 23 Nov 09:00Z, which supersedes R-064(5)). The scorer's PRIMARY figure is row_15s_net03 (rate 0.03); net05 is secondary and labelled docs-table.
