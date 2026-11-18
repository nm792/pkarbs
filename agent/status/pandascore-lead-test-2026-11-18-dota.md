# P34 — Dota PandaScore lead run (18 Nov)

State: partial; run blocked by malformed raw gzip inputs. No result JSON or Dota verdict was produced.

- Markets export: 42 lines.
- PM-books adapter: rows_in=107624, rows_out=100676, dropped=6948.
- Schema: `['asks', 'asset', 'bids', 'recv_ms']`; `asset`/`tk` count=100676, matching rows_out.
- Planted test: all six cases PASS; process exit 0.
- Lead test: exit 1. `zlib.error: Error -3 while decompressing data: invalid block type` while reading a compressed PandaScore raw file.
- Audit: exit 1, same decompression error.
- Raw directory had four files; gzip validation failed for the 16 Nov 12Z and 18 Nov 21Z files. No output JSONs were created. No Dota cells or verdict are available; unchecked.

Evidence: `agent/status/pandascore-lead-test-2026-11-18-dota-run.txt` and `agent/status/pandascore-lead-test-2026-11-18-dota-audit.txt` (paths redacted in copied logs). The malformed source files were not modified.
