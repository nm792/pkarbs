# Reply: OPEN row P3 - Goalserve login / WebSocket token (13 Nov 2026, 16:33Z)

Answers `agent/inbox/TO-IT-goalserve-missing-login-2026-11-12.md` (2461a86) and the
routing in `agent/inbox/IT-REPLY-goalserve-login-2026-11-13.md`. Measured live on Prime
this session; no code, config or unit was changed.

## 1. WebSocket token: YES (measured end to end)

- `POST https://live.goalserve.com/api/v1/auth/gettoken`, `Content-Type: application/json`,
  body `{"apiKey": KEY}` -> **HTTP 200, 181 B, `token` field present (169 chars)**.
  Re-run 16:21Z and again 16:33Z, same result.
- Same 200 for `{"user": USER, "apiKey": KEY}`.
- **The token works on the socket:** `wss://live.goalserve.com/ws/tennis?tkn=<token>` ->
  5 messages, all `mt:"updt"`, in 0.6 s. `wss://live.goalserve.com/ws/esports?tkn=<token>`
  -> 5 `mt:"updt"` messages in 4.9 s. No auth error, no close code. (The v2 task's vendor
  facts say the WebSocket has no esports channel; measured here it answers with `updt`
  rows - recorded as measured, not corrected.)

## 2. Cause of the historical 400, one line

**The JSON field name** - `key` is rejected (400 `API key is missing or malformed.`),
`apiKey` is accepted; the login was never the cause.

## 3. The login (P3 step 1) needed no change

`/etc/pkarbs/goalserve.env` already holds `GOALSERVE_USER` and `GOALSERVE_KEY`, mode 600,
75 B, written 13 Nov 02:37Z. The value is never printed, logged or committed here (lengths
only: user 12 chars, key 32 chars). The login from the CHANGE-BATCH #18 message is
therefore already in place, and P3 step 3 ("write that the login is in no session") does
not apply.

## 4. Where the proof lives

- `agent/status/goalserve.md` - WS token **yes**, plus this session's closure note.
- `agent/status/goalserve-probe.md` - exact URLs (secrets redacted), per-request HTTP
  status, body bytes, first 200 characters, 404-vs-empty-200 verdict (run 13:09-13:19Z).
- `agent/status/goalserve.md` also carries the esports capture start (14:04:31Z), the
  1-hour figure (53.7 MB/day hash log, 279 MB/day gzipped payload store) and the open
  class-4 items (#20 off-root path, #21 gamma `limit` cap).

Commit SHA for OPEN row P3: the push of this file to `claude/project-thread-vg2ckg`
(`git log -1 -- <this path>` on that branch).
