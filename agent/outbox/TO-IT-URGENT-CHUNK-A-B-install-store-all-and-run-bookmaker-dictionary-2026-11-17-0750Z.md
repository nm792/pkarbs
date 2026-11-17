# P15a — Goalserve bookmaker dictionary (chunk B)

- Source note: `agent/inbox/TO-IT-URGENT-CHUNK-A-B-install-store-all-and-run-bookmaker-dictionary-2026-11-17-0750Z.md`.
- Base: `claude/project-thread-vg2ckg` at `1cb7a1e5640d704ae666e4c5dde971ea52a77a36`.
- `python3 -I live/goalserve/test_bookmaker_dictionary.py`: **ALL PASS** (8 checks); output/key-leak checks passed.
- Ran the specified read-only dictionary command. Result: `agent/status/goalserve-bookmaker-dictionary-2026-11-17.md`, with one final `PINNACLE <sport>:` line for each of the 16 requested sports. No feed reported Pinnacle present in the requested window; baseball, rugby, rugbyleague and mma are `NOT CHECKED` because their feeds had no bookmaker nodes. The documented `tennis_scores/pregame_bookmakers` request returned HTTP 500 and is recorded as not read.
- The adjacent chunk-A store-all test was run read-only and failed: four gzip-row checks failed, followed by `FileNotFoundError` for the tennis output path. Chunk A is not installed; no live capture, process, or configuration was changed.
