# from_agent/rugby-probe-and-ab-commit-2026-11-07 — DONE

**AB capture committed.** AB ended 2026-11-07T18:05Z. Committed to `claude/project-thread-vg2ckg` at `dae68560`:
- `reports/rugby-capture/AB_rugbyrama_events.jsonl` (284 KB parsed events)
- `reports/rugby-capture/AB_summary.md`, `AB_launch.out`, `AB_log.txt`
- `reports/rugby-capture/manifest/AB_manifest.md` — sha256+size for big raw files kept on volume (AB_rugbyrama.jsonl 1.32 GB, AB_espn.jsonl 39.6 MB, AB_clob_rest.jsonl 6.6 MB), which exceed the 1 MB jsonl / 5 MB pre-push hook.

**5-min CLOB probe** (`rugby/probe_clob.jsonl`, read_clob from merged script, bounded 300 s, nice 19):
- CLOB WS connected @18:33:03Z (`CLOB open`), ran full 301 s.
- **0 market messages received** — silent stream, no probe_clob.jsonl written (file never created). This matches the project thread's own finding that Top 14 books are very thin (best bid/ask within 10c in only 2-7% of polls). First-message type: none (no messages). REST poll remains the price clock for windows D and C, as the note's fallback states.
