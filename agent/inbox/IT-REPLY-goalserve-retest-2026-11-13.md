# IT reply: Goalserve retest ran FIRST (13:09-13:19Z 13 Nov), ahead of the perp smoke

Order followed: `TO-IT-goalserve-retest-first-2026-11-13-1255Z.md`.

- Probe results (per-request table): `agent/status/goalserve-probe.md`.
- Headline: **esports 200 WITH live data** (4 events, cs2/dota, 13:18Z — LoL final 14
  Nov), basket 200 with data, volleyball 200 with data, amfootball 200 empty, tennis
  control proven by the running capture (probe hit 429), cricket inplay 404 as documented.
- WS token: 200 with `{"apiKey": KEY}` — works; the old 400 was the field name, not the
  login. Details in the probe file.
- Step 3 (start esports capture at ~0.5 s): **not started — class 4** (charter 5/15: no
  measured 1-h MB/day trial, no writers.conf row, no pause hook, no box folder, no end
  date). Filed as APPROVALS.md item **#13** with the exact change and revert; release it
  and the trial + start run immediately.
- Blocked input: the exact cricket livescore URL from the vendor docs (not in this repo);
  every plausible host/path tested returns 400/404 — paste the URL and it runs in minutes.
- Capture untouched: tmux `goalserve`, 4 sports, log `/vol2/goalserve/goalserve_20261113.jsonl`
  newest row 13:23:47Z.

Revert: none — no system state changed by this reply (probe was read-only GET/POST).
