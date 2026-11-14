# D1 — VOL2 storage check — 2026-11-14 08:34Z

- Measured `/vol2` (the pkarbs data volume): 105,089,261,568 bytes total, 69,750,575,104 bytes available (66G shown by `df -h`), 31% used. The D1 target of more than 40 GB free is already met.
- `/vol2/pkarbs/shadow` currently contains only 567 bytes; its `data-v2` directory has no files. The configured `pkarbs-shadow-v2` writer's dry run reported `nothing eligible local_bytes=0`; no archive was transferred this run, so no box checksum or new manifest row is claimed.
- `/vol2/pkarbs/thesports` contains one 22.7 GB `final-topics-32295b` directory, actively written by the live capture and trade-capture processes. It is not an old daily folder eligible under D1's >3-day rule. No live capture data was touched.
- Result: no eligible day folders were present to ship or delete. D1 is not marked complete: the historical box copies and their checksums were not independently verified, and there was no per-day archive to add to the manifest.
