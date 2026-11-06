# TASK: TheSports free trial: timing capture, 5 Nov 2026

From: Claude, PK arbs thread "Test TheSports feed speed on trial" (5 Nov 04:40Z). Nick has emailed TheSports asking for the free
trial. Status: **GO (Nick 6 Nov 09:23Z: IP whitelisted, Hermes has the access details). PART A (IP report) NOT NEEDED. PART B: START NOW, no further approval needed; if `/etc/pkarbs/thesports.env` is missing, say so in the outbox file and start the moment it exists.**

## Question (one only)
Do TheSports push messages (tennis points, LoL/CS2/Dota kills, NBA plays) reach our server **before the Polymarket price moves**?
The thread measures this from what you record; you only record. No orders, no money, no P&L in this task.

## Part A: now (before credentials)
1. **Fixed IP for the whitelist (do this FIRST, it is the only thing TheSports is waiting on; TheSports says Finland/Europe is fine, so state whether the box is Hetzner HEL1).** The trial needs our server's public IPv4 whitelisted. Write it in
   `agent/outbox/2026-11-05-thesports-trial.md` (and IPv6 if TheSports should use that), plus the server's country/city
   (Hetzner datacentre, e.g. FSN1/NBG1/HEL1) and whether the clock is NTP-synced (`timedatectl` "System clock synchronized").
   Claude passes the IP to Nick to send to TheSports. Nick never runs commands.
2. `pip install --user paho-mqtt` (websocket-client is already installed for the Cito logger).
3. Dry run, 10 minutes, without credentials (records Polymarket only):
   ```
   cd <repo> && git pull
   systemd-run --scope -p MemoryMax=500M -p MemorySwapMax=0 timeout 700 \
     python3 -I live/thesports/capture.py /root/thesports/dry 0.17
   ```
   PASS: `log.jsonl` has `start`, `thesports_no_creds`, `pmws_open`, `discover_pm` with tokens > 0, and `stop`;
   `books.jsonl` has 100+ rows. Then delete /root/thesports/dry. Report PASS/FAIL and the last 20 log lines in the outbox file.

## TheSports facts that change the run (from their trial PDF + docs.thesports.com, 6 Nov)
- MQTT: `mq.thesports.com:443`, TLS WebSocket, username/password = the same user/secret as the HTTP API, client IP must be whitelisted. **Topics are issued by TheSports per sport (football, basketball, tennis in their sample); never construct them.** Put the issued topics in `THESPORTS_TOPICS` (comma list). `#` will probably be refused. Messages are JSON; changed fields only (`score`, `stats`, `incidents`, `tlive` for football).
- The trial enables only endpoints requested from the business manager. Esports (LoL/Dota2/CS2) and cricket are eligible but need activation and their own topics. In `agent/outbox/2026-11-05-thesports-trial.md` report which topics Nick's email lists; if there is no LoL/Dota/cricket topic, say so at once (the thread asks TheSports).
- HTTP real-time endpoints are meant to be polled every 2 s. Schedule endpoints (`/v1/<sport>/match/diary`) map match ids to team names via `results_extra`; poll them every 300 s. Set, e.g., `THESPORTS_POLL_PATHS=/v1/basketball/match/diary@300,/v1/basketball/match/detail_live@2,/v1/tennis/match/diary@300` plus the esports/cricket paths once TheSports gives them.
- Basketball real-time = quarter scores + remaining seconds in the section + a timer with `update time` in whole seconds; no per-play ms timestamps. Football-style incidents carry minute/second only. So we time by our own receipt, as planned.

## Priority order once Part B runs (Nick 6 Nov 09:19Z)
1. **LoL**: Worlds semis 7-8 Nov, final 14 Nov. Live before the first semi. 2. **Dota 2**: BLAST Slam from 17 Nov. 3. **NBA** nightly, **cricket**, **tennis**.
capture.py covers all of these in one process; this order only sets what to check first in the first hour.

## TheSports facts that change the run (their trial PDF + docs.thesports.com)
- MQTT: `mq.thesports.com:443`, TLS WebSocket; username/password = the user/secret; IP must be whitelisted (Nick did). **Topics are issued by TheSports per sport (their sample: football, basketball, tennis); never construct them.** Put the issued topics in `THESPORTS_TOPICS` (comma list); `#` will probably be refused. Messages are JSON, changed fields only.
- Trial endpoints are enabled per account on request. Esports (LoL/Dota2/CSGO) and cricket need activation and their own topics. In `agent/outbox/2026-11-05-thesports-trial.md` report which topics you have; if there is none for LoL, Dota or cricket, say so at once.
- Real-time HTTP endpoints: poll every 2 s. Schedule endpoints (`/v1/<sport>/match/diary`) give match ids to names via `results_extra`: poll every 300 s. `THESPORTS_POLL_PATHS=/v1/basketball/match/diary@300,/v1/basketball/match/detail_live@2,/v1/tennis/match/diary@300`, plus esports/cricket paths once TheSports gives them.
- Basketball real-time = quarter scores + remaining seconds + whole-second timer; no per-play ms timestamps. We time by our own receipt.

## Part B: when Nick sends the trial user/secret (and topics) to you
1. Install them per `live/thesports/KEY-INSTALL-THESPORTS.md`. Never print, commit or message them.
2. Run in 12 h bounded chunks for the whole trial (15 days), one chunk at a time (PROTOCOL rule 2):
   ```
   cd <repo> && git pull && D=$(date -u +%Y-%m-%dT%H) && mkdir -p /root/thesports/$D && \
   set -a && . /etc/pkarbs/thesports.env && set +a && \
   systemd-run --scope -p MemoryMax=500M -p MemorySwapMax=0 timeout 43500 \
     python3 -I live/thesports/capture.py /root/thesports/$D 12 --share /root/thesports/$D/share
   ```
   Restart a new chunk as soon as one ends. `--share` holds gz copies refreshed every 10 min.
3. **First hour is the most important.** Within 60 min of the first start, commit `share/ts_mqtt.jsonl.gz` and `share/log.jsonl.gz`
   (even if small) so the thread can see the message format and write the parser. If `log.jsonl` shows `mqtt_err`,
   `mqtt_disconnect` loops, a non-zero `rc` on `mqtt_connect`/`mqtt_suback`, or no `ts_mqtt` rows after 15 min while
   matches are live, say so in the outbox file at once, with those log lines.
4. Copy out every hour to `rn1/scores/thesports/<chunk>/` on branch `hermes/thesports` (not the default branch):
   `ts_mqtt`, `ts_poll`, `pmws`, `markets`, `log` gz always; `books.jsonl.gz` for the first 48 h only (it is ~5-10 MB/h).
   After 48 h keep books on the storage box and commit them only when the thread asks. Before every commit run the
   secret check in KEY-INSTALL-THESPORTS.md step 3; it must print nothing.

## Pass / fail for Part B, fixed before running
- PASS (first 12 h chunk): MQTT connected for 95%+ of the chunk (gaps = `mqtt_disconnect` to next `mqtt_connect`), `ts_mqtt` rows
  from at least 3 of: tennis, LoL, CS2, Dota 2, NBA, and `books.jsonl` keeps growing while markets are live.
- FAIL: otherwise. Report the log lines; don't retry more than 3 times in a row without telling the thread.

## Clean up (rule 4)
After each chunk confirm the process is gone (`ps`, `free -m`) and delete `/root/thesports/<chunk>` once its final copy is
committed or on the storage box. At trial end delete `/etc/pkarbs/thesports.env`. Status in `agent/status/thesports-trial.md`
(chunk start/stop, rows per file, connected %, PASS/FAIL, "credentials installed: yes/no").

## Protocol notes
Read-only. One process: an MQTT client, a 1 s POST clob /books poller for live tennis/LoL/CS2/Dota/NBA/NFL/cricket game-winner tokens,
gamma every 5 min, and the PM sports WS. It runs alongside the tennis books logger (different file, same light rate).
Honest User-Agent `pkarbs-thesports-trial/1.0`; no 403 workarounds.


## 2026-11-06T12:32Z APPROVED, PROCEED NOW (Nick-approved via PR #164)
The `THESPORTS_TOPICS=#` env edit and capture restart in `agent/inbox/thesports-topics-2026-11-06.md` is **approved, proceed now**. Do not wait for Nick; he does not relay. Edit `/etc/pkarbs/thesports.env`, restart the chunk, record the `mqtt_suback` rc in `agent/status/thesports-trial.md` (first lines) and the outbox. If refused, restore the empty line and wait for real topics in this inbox.
