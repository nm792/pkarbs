# 3 Nov 17:20Z: verify every offloaded file, not a spot check

Thanks for the offload (85 manifest rows, ~37 GB; /dev/sdc 31 GB free). The ruling needed a three-way sha256 match on EVERY file before its local delete. Your outbox says only one file was spot-checked.
1. Now, read-only: for every manifest row, compute sha256 on the storage box over SSH and compare it with the manifest sha256. Add a `box_sha_verified_at` column (or a separate file `agent/status/storage-offload-verify.csv` with path, manifest_sha, box_sha, match) and commit it.
2. Report in `agent/outbox/2026-11-03-offload-verify-all.md`: rows checked, matches, mismatches, missing files. If any row mismatches or is missing on the box, list it and do NOT delete anything further. Tell us; do not re-copy from anywhere without a note back.
3. No further deletes until this report is in. The shadow-logger stop stays with Nick (interactive terminal).
