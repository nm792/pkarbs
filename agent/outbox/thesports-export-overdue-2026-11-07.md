# from_agent/thesports-export-overdue-2026-11-07 — capture DOWN (restart gated)

**Root cause: the live TheSports capture is not running.** Checked 2026-11-07T18:35Z:
- No thesports capture process (`ps` / `/proc` cmdline scan), no tmux session, no systemd unit named for it, no crontab line guarding it.
- `/root/thesports/` holds only the stale `slim-1102-32295` export (created 11:02Z, ts_mqtt/books through ~11:02Z). No newer export exists to commit — there is no live chunk producing new ts_mqtt/books_mid data, so the every-2h slim export has produced nothing since ~11:02Z.

**No exporter can commit a fresh slim** because no capture is generating fresh data. The `export_slim.py` route (`_root/thesports/slim-<HHMM>-<chunk>`) can only re-slim the same 11:02Z data, which would duplicate already-committed rows, so I did NOT commit a stale re-export.

**Needed:** restart the thesports capture writer (the `final-topics-8917`/`final-topics-*` capture.py chunk that the diary/status references). This is a restart-or-kill → **consent-gated, awaiting Nick's approval at next interactive session.** Weekend Dota 2 / CS2 games are the data we need, per the note.
