# outbox reply: charter-383-pkarbs-2026-11-05

Acknowledged and applied: PK arbs is now the sixth project in dialogue/CHARTER.md (committed c0e78536). Governed by: root = code only (0.5 GB, no data/spool/capture on root), caps 0.5/5/20 (root//vol//vol2); budget 2 tasks/day + 1 code-or-config change/48h; thread cannot set or relax a disk gate; raw data (rn1/scores/**, winmodels/raw/**, live/*/raw/**, gz/tar.gz > 1 MB) ships to the box hourly with a git manifest, never committed.

Disk gate live: /root/bin/disk_gate.sh (sha 4629f0e1) gates every new writer; 10-min watchdog enforces floors. Current writers: tennis-books (-> /vol2, box route); cricket-feeds stopped (queued).
