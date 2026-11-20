# 00-URGENT (coordinator 04:06Z, after Nick's sample request): export EVERY CS2 match in the raw capture since 19 Nov 11:20Z. READ-ONLY.
git fetch origin reviewer; git checkout origin/reviewer -- it/
Raw hour files: the live raw dir AND any copy shipped to the storage box (IT ship job moved old raw data); include every pandascore_2026111911..2026112003 file that reads. A corrupt file ("invalid block type") is skipped by the script and listed; paste its name.
python3 -I it/ps_export_samples.py <RAW_DIR> /root/ps_samples_all 999
(for a second raw dir run again into /root/ps_samples_all_b). Copy ps_sample_*.jsonl.gz + ps_sample_index.json into scratch/ps_samples/ on reviewer (add only, no deletions; skip files already there). Paste the index to agent/status/pandascore.md.
Also paste: `ls -l --time-style=full-iso <RAW_DIR> | tail -30` and the live read (it/pandascore_live_read.sh) so capture state is known.
