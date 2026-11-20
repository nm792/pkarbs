# To IT, 20 Nov 2026 14:30Z: free disk 10.8 GB (floor 15). Ship OUR completed pkarbs hours to the storage box, verify, then delete local copies

Thanks for disk-2026-11-20.md. pkarbs data is ours, so no further approval is needed for pkarbs; do NOT touch mfw-box-live, box-live-data-co-full or any MFW data (separate question to Nick).

One row, using the existing ship_raw / storage-box job you already run (same destination and method as the 19 Nov hourly ship; do not invent a new method):
1. Ship only COMPLETED hourly files older than 3 hours: pkarbs/pmcs2/books-*.jsonl* (all hours except the current and previous 3), plus any idle pkarbs folders with no open writer (check with fuser first: charts, thesports, old probe outputs).
2. After the copy, verify each file by checksum (sha256 local vs box) and by size. Delete the local copy ONLY for files where both match. Keep a list of shipped files and their checksums in agent/status/disk-ship-2026-11-20.md.
3. DO NOT ship or delete: pkarbs/pmdota (BLAST recorder, whole directory), pkarbs/pandascore/raw (needed for the Dota lead test), pkarbs/goalserve current files, any file with an open writer (fuser), and nothing in pkarbs/thesports/final-topics-32295b (holds PM book recorder data: never ship whole).
4. Report df before and after. Target: free above 15 GB. If a step fails (checksum mismatch, box unreachable) stop, delete nothing, and say FAIL on line 1.
