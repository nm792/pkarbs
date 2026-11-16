APPROVALS NEEDED:
- None. Read-only reconciliation; no code, shipper or live process changed.

RESULT
- Step 3: both `ps_lead_test_current.py` runs used the same 14 hourly inputs: 13 Nov 15–22Z and 14 Nov 07–12Z. The independent audit used the latter directory too. The run logs show 22,884 messages and 1,911 counter increases across 23 matches. The gzip-valid analysis copy has 22,977 JSON rows; the corresponding 14 Nov 12Z historical source has a truncated gzip trailer, but 1,641 complete JSON rows parse.
- The full 13–16 Nov box set is not complete: 54 hourly files exist, but coverage is 13 Nov 15–22Z; 14 Nov 07–23Z; 15 Nov 00–01Z and 07–22Z; 16 Nov 08–11Z and 13–19Z. The 16 Nov 12Z source is corrupt; 13–15Z were checksum-verified on the box in the prior report. No complete 13–16 Nov set was found.
- Step 4: the capture writer flushes each row and closes the prior gzip when its first row for a new UTC hour is written. Safest rollover is to leave it running through that transition; verify the previous hour with `gzip -t` before shipping. If a manual stop is unavoidable, use a graceful interrupt so the writer's `finally` closes the gzip, wait for process exit, then test integrity before restart/ship. Do not use a force kill or ship the current open-hour file.
- Read-only source checked: `feeds/STANDARD-feed-latency-test.md` v1. No lead or verdict added.

DATA
- Run source lists and logs: `/vol2/pkarbs/scratch/ps-lead-20261115/run-final-20261116.stderr`, `run-historical-final-20261116.stderr`, and `audit-20261116-D.stderr`; inputs under `/vol2/pkarbs/scratch/ps-lead-20261115/ps-window/` and `/vol2/pkarbs/scratch/p318-recount/pandascore/`.
- Box inventory: `/root/ship/ship.log`; 13–15Z row counts and integrity are in the prior report.

OPEN / NOT VERIFIED
- None for steps 3–4. The underlying 13–16 Nov capture has gaps; this report does not reconstruct missing hours.

Count: notes run 1, outstanding 0, PENDING open 0
