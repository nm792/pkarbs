# status: Goalserve trial — capture RUNNING (Part A), 4 sports

Updated: 12 Nov 2026 ~21:56Z UTC

- **Env file:** `/etc/pkarbs/goalserve.env` — mode 600, GOALSERVE_USER + GOALSERVE_KEY (never printed/committed).
- **Egress-IP whitelist: yes** (prior check + IT).
- **Auth:** user+key authenticated — `inplay-tennis.gz?user&key` HTTP 200 (~221 ms).
- **GET TOKEN (`live.goalserve.com/api/v1/auth/gettoken`):** 400 in every field mapping — separate/unactivated; not needed for HTTP polling.
- **Capture:** RUNNING, tmux `goalserve`, `live/goalserve/capture.py`, log `/vol2/goalserve/goalserve_YYYYMMDD.jsonl` (recv_ns, sha1, change first-seen per poll).
  - Polling (verified OK): **tennis, soccer, baseball, hockey (NHL)**.
  - Not available as a Goalserve inplay feed on this trial: basketball (404), cricket (404), esports Lol/CS2/Dota2 (404/empty). Cricket overlap is captured via TheSports/ESPN per the task; the task's esports items need a Goalserve feed that does not exist.
- Started 02:38Z 13 Nov; ~1 poll/s, error-safe (429/404 logged and skipped).

Next: bind the PM/CLOB + TheSports recorders for the matching markets (Part A alignment); cricket/esports request to IT if the endpoints are meant to exist (inplay-cricket.gz 404).
