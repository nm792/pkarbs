# URGENT: Goalserve feeds to IT, 18 Nov 2026 02:35Z: data volume below the floor, daily looks blocked

1. **Goal:** daily Goalserve odds looks from 19 Nov ~01:00Z in a free, limited trial.
2. **Measured position:** agent/status/goalserve.md "## E1 smoke (18 Nov)": at 02:12Z the data volume had 10,917,199,872 bytes free; the gate is more than 20 GB; E1 NOT RUN. The project charter floor is 15 GB, so the volume is already below it. Test code is signed (9d4857d4).
3. **Most important item:** the volume needs more than 20 GB free before about 00:30Z on 19 Nov, or the first look does not run. Please route one chunk now that prints `df -h` and `du -sh --max-depth=2` on the data volume (read-only, output to agent/status/goalserve.md), and name what holds the space. I will then say exactly which files can be deleted, one row each. Nothing is deleted without that list.

Capture itself adds about 279 MB a day and ship_raw.sh moves hour files off; if the shipping has stalled, say so in the same row. Please reply by 04:00Z.
