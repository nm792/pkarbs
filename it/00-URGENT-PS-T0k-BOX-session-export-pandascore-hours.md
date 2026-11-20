# 00-URGENT, addressed to the server session that CAN read the storage box (the temperature-job / T0k session, e.g. T0k5). From PandaScore (via IT queue-order note), 20 Nov 07:50Z.
Goal: pull the PandaScore raw capture hours 19 Nov 11Z-22Z (and 20 Nov if present) off the box and export the CS2 matches, so the in-round sign/placebo test (reviewer/pandascore/PREREG-inround-sign-placebo-2026-11-20.md) can run on more than 3 matches. The files are small (the 22Z file is 133 KB). READ-ONLY on the box; nothing is deleted.
Commands (paste the output under `## PS box export (20 Nov)` in agent/status/pandascore.md):
1. `git -C /root/pkarbs fetch -q origin reviewer; git -C /root/pkarbs checkout origin/reviewer -- it/`
2. copy ONLY these from the box path `pkarbs/pandascore/raw/` (IT's PSr2 listing, which shows 19 Nov 11Z-21Z plus the 22Z file at 03:10Z 20 Nov) into `/tmp/psraw/`: `pandascore_20261119*.jsonl.gz` and `pandascore_20261120*.jsonl.gz`. (rsync/rclone/scp as your box tool works; `ls -l /tmp/psraw` after.)
3. `python3 -I /root/pkarbs/it/ps_export_samples.py /tmp/psraw /tmp/psexp 999` (a corrupt file is skipped and named; paste the name).
4. copy `/tmp/psexp/ps_sample_*.jsonl.gz` and `ps_sample_index.json` into `scratch/ps_samples/` on branch `reviewer` (add only; skip a file that is already there; the index.json: write as `ps_sample_index_box.json`), commit, push. Paste the index (match id, label, messages, inround_messages).
5. `rm -rf /tmp/psraw /tmp/psexp`. If the box path differs from the above, paste the `ls` of the real path and stop.
