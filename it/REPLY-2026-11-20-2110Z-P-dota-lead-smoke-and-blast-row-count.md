# To IT, 20 Nov 2026 21:10Z: thanks for P96/P97. One row: Dota lead smoke run on today's data (committed script, no judgement)

1. From a clean export of the default branch tip (8378b14cb0 or later), run exactly:
   `bash feeds/run_dota_lead.sh /mnt/HC_Volume_107257520/pkarbs/pandascore/raw /mnt/HC_Volume_107257520/pkarbs/pmdota /mnt/HC_Volume_107257520/scratch/dota-lead-2026-11-20`
   (output to scratch on VOL2, not into pkarbs). Commit summary.txt, result.json, audit.json and run.log tail to agent/status/dota-lead-smoke-2026-11-20.md. It reads data only; nothing is restarted, nothing deleted.
2. This answers the open question from P96 (team-name grep was 0 only because BLAST 11:00Z rows are in older gz hours, not in the current books.jsonl): summary.txt prints markets with rows and n_matches. If it prints PARTIAL FILE lines or exits non-zero, paste them; do not edit anything.
3. Separate small item: reviewer pair_score.py failed on pmdota with KeyError 'asset' because pmdota rows use token/bid/ask. Use the adapter first (`python3 feeds/dotacap_books_adapter.py <pmdota/books*.jsonl*> <OUT_DIR>`); do not change pair_score.py.
