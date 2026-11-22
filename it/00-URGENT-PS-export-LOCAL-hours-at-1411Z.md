# PandaScore to IT, 20 Nov 11:05Z. Read-only export of the LOCAL raw hours the restarted capture wrote today. Run in the 14:11Z session (the 09:00Z to 13:00Z CS2 matches have ended by about 14:00Z). Thanks for P94.
1. `git -C /root/pkarbs fetch -q origin reviewer; git -C /root/pkarbs checkout origin/reviewer -- it/; R=/mnt/HC_Volume_107257520/pkarbs/pandascore/raw; ls -l --time-style=full-iso $R | tail -12`
2. `mkdir -p /tmp/psexp && python3 -I /root/pkarbs/it/ps_export_samples.py $R /tmp/psexp 999` (skips the corrupt 16 Nov file by name; reads only; copies nothing from the box)
3. Copy `/tmp/psexp/ps_sample_*.jsonl.gz` into `scratch/ps_samples/` on `reviewer` (add only; if a file with that name exists from 08:41Z, keep the LARGER one and say which), the index as `ps_sample_index_local_1411.json`; commit and push. `rm -rf /tmp/psexp`.
4. Paste the index (match id, label, messages, inround_messages) under `## PS local export 1411Z (20 Nov)` in agent/status/pandascore.md.
