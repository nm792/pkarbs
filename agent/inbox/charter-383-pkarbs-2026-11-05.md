# PK arbs is now governed by the shared charter (note 383, Nick 14:00Z 5 Nov)

Full note: nm792/trading-test, branch `dialogue`, `dialogue/temperature/to_agent/383-pkarbs-into-charter-and-disk-gate.md`.

For this project thread:
- Disk gates are set only by the charter. The thread cannot set or relax one (the 05:25Z 6 GB ruling was the last of these).
- Budget: at most 2 new tasks per day and 1 code or config change per 48 hours.
- No PK arbs data on the root disk. Captures write to /vol2 and ship raw to the storage box hourly.
- Raw data (`rn1/scores/**`, `winmodels/raw/**`, `live/*/raw/**`, any gz/tar.gz over 1 MB) is not committed here. Git gets a manifest; ask the agent for a computed result, not the raw files.
- Every new task runs through `/root/bin/disk_gate.sh`. A refusal is final until the figures change.
