APPROVALS NEEDED:
- None. Read-only; ship_raw.sh was not edited.

RESULT
- Step 1: box copies for 13:00Z, 14:00Z and 15:00Z passed gzip integrity and contained 1,676, 2,277 and 2,336 rows. The local copies had been deleted after verified shipping; all three hours exist on the box.
- Step 2: the local 12:00Z gzip fails full-stream integrity. Tolerant reading recovered 588 complete JSONL rows from the old process (12:00:04–12:24:56Z) and 1,091 from the next gzip member (12:25:22–12:59:59Z). Total recoverable: 1,679 rows; 0 malformed JSON lines among those recovered. The new-process count is recovered from the member after the damaged stream, not a clean full-file gzip test.
- Proposed, not applied: make ship_raw.sh test gzip members independently and salvage complete JSONL records from readable members when a later member is damaged; write and validate a separate partial artifact, then checksum-verify the box copy before any deletion. Preserve the original and log recovered/dropped counts. This addresses BADGZ without changing the live shipper in this read-only step.
- Per feeds/STANDARD-feed-latency-test.md v1: counts only; no lead or verdict.

DATA
- Prime raw input: pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz. Box checks for hours 13–15 and retry history: /root/ship/ship.log and /root/ship/manifest/manifest.tsv.

OPEN / NOT VERIFIED
- Steps 3–4 remain: identify which hours each lead-test run read and state a safe restart/rollover procedure. No code or process changed.

Count: notes run 1, outstanding 1, PENDING open 0
