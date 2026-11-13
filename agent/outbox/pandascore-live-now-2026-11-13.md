# Reply: PandaScore v2 - running, first capture 15:11Z (13 Nov, 16:36Z)

Answers `agent/inbox/pandascore-live-now-2026-11-13.md` (issue #283 stays open until
this file lands; this is that file's companion reply). Measured this session.

1. **Token:** present, not missing - `PANDASCORE_ACCESS_TOKEN` (51 bytes) lives in the
   API_KEYS store at mode 600. The planned `/etc/pkarbs/pandascore.env` copy could not be
   written from an unattended run (terminal consent gate), so the client reads the
   API_KEYS file as its second choice; it detects the token at start. Value never
   printed, logged or committed.
2. **Client built per v2:** yes - `live/pandascore/ll_capture.py` (214 lines,
   `py_compile` OK), correct URL `/matches/{id}/low_latency_feed`, discovery at
   `/low_latency_feeds`, close codes read, token never logged. tmux session `pandascore`
   up since 15:12:29Z, pid 212720; first capture landed 15:11Z.
3. **Class-4 items filed:** yes - `dialogue/APPROVALS.md` **#20** covers moving the
   PandaScore and Goalserve captures off the root volume (they write under `/vol2`,
   which resolves to root), and the gamma page-cap fix is **#21**. Both are on the daily
   approval batch; neither was applied by this session.
4. **Status cadence:** `agent/status/pandascore.md` posted (15:17Z) and refreshed at
   16:10Z with the Dota coverage report; the next 30-minute status is due 16:47Z.

Measured live: capture process running 1 h 24 min at 16:36Z; the Polymarket book stream
it is paired against (`books.jsonl`) is current to 16:25:49Z. Registration of new PM
markets is frozen (see `agent/outbox/TO-IT-URGENT-polymarket-recorders-dead-2026-11-13-1615Z.md`),
so new matches pair only after approval #21.
