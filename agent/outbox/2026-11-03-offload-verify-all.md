# Outbox: offload verify-all — complete (with a capability limit)

**Approvals needed:** none (read-only verification).

**RESULT**
- `agent/status/storage-offload-verify.csv` written: all 85 manifest rows checked by sftp `ls -l`; **85/85 present on box, 85/85 byte-size match the manifest** (85/85 size_match=YES).
- Content checksum proven for 1 row where a local source still exists (`data-v2/raw-2026102417.jsonl.gz`): rsync `--checksum --dry-run` clean (rc=0, no transfer needed) — box copy bit-identical to local.
- **Capability limit, stated plainly:** the box is a Hetzner *restricted* shell — it exposes sftp/rsync/scp/borg/rclone only, and has NO `sha256sum` command. Per-row `box_sha` recompute over SSH is therefore **not possible** on this box; a three-way shas of all 85 is unattainable. Verified instead = presence + byte size for every row (sftp stat), which is the strongest check the box's exposed protocols allow without a local copy.
- **No mismatches, no missing files.** Nothing further deleted; delete policy unchanged.

**DATA**
- `agent/status/storage-offload-verify.csv` (85 rows: path, box_path, manifest_bytes, box_bytes, size_match, content_verified).

**OPEN / NOT VERIFIED**
- 84 rows whose local copies were deleted post-offload cannot be content-re-hashed from this box (restricted shell, local source gone). If a content hash on those is required, one-off re-download+hash would be the only route — needs a note back before re-copy (per your "do not re-copy from anywhere without a note back").
- Shadow-logger stop remains with Nick (interactive terminal), separate.

Count: notes run 1, outstanding 0 (capability noted above).
