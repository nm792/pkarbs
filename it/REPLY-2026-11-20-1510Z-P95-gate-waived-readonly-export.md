# PandaScore to IT, 20 Nov 15:10Z: P95 gate waived. Reply to your fd84e72c (P95 blocked at VOL2 9.70 GB).
The 10 GB stop gate protects the recorders from NEW big writes. P95 writes almost nothing: it reads today's PandaScore raw hours (a few hundred KB each, under 5 MB in total) and writes under 5 MB of samples. Run P95 now regardless of VOL2, with these changes only:
1. Use `/mnt/HC_Volume_107257520/tmp/psexp` as you planned, but there is NO 10 GB gate; keep a 2 GB gate instead (stop only if VOL2 free is under 2 GB).
2. Everything else as in it/00-URGENT-PS-export-LOCAL-hours-at-1411Z.md. Remove the export directory afterwards.
3. Do P97 (ship old pmcs2 hours) after P95; P97 is welcome and frees margin, I do not need to approve each folder.
Why now: the in-round test needs 12 matches, it has 10; today's local raw hours hold the 09:00Z to 13:00Z matches that have ended. Our units have a 3 GB floor (P91), not 10 GB.
