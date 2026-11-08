# from_agent/thesports-new-messages-2026-11-07.md — ts_mqtt committed for chunk 32295

**Approvals needed:** none (read-only export + commit of committed data; source untouched).

## RESULT
- Committed the TheSports MQTT messages for the newer live chunk **final-topics-32295** (started 2026-11-07 04:00Z) into `rn1/scores/thesports/slim-0517-32295/ts_mqtt/`, partitioned to pass the 5 MB pre-push hook exactly like the `8917-slim` layout:
  - **303 gz parts, per-hour sub-dirs, max single file 159,650 B (all < 1 MB)**, 19 MB total.
  - Covers source `ts_mqtt.jsonl` snapshot 1794024009194 → 1794042081499 ms (04:00Z → ~05:08Z), the 2 h window the note named (counts show 1,760+245 tennis, 27,499+8,216 basketball for the 04:00/05:00 hours).
  - Rows written as-is (unchanged jsonl lines); NO basketball exclusion applied — included all topics, reviewer can drop basketball at review time (slim keeps it small).
- Source data: `/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295/ts_mqtt.jsonl` (~135 MB raw) — NOT modified, still live-growing.

## DATA
- Commit `2a497fa9` on `claude/project-thread-vg2ckg`.
- Path: `rn1/scores/thesports/slim-0517-32295/ts_mqtt/` (303 files, max 156 KB each).
- Also present in that slim dir from the prior round: books_mid, counts, log, markets, pmws, ts_poll.

## OPEN / NOT VERIFIED
- This is the snapshot up to ~05:08Z (the newer chunk keeps growing). The "keep doing it every 2 h export" cadence continues with the dispatch — each subsequent 2 h export should add ts_mqtt the same way; this commit covers the first window.
- basketball rows included (note said "skip if size is a problem"; it is not, so kept).

Count: notes run 1, outstanding 0, PENDING open 0.
Context: read-only export of the live capture chunk to the repo, partitioned per the existing 8917-slim layout and the 5 MB pre-push hook.
