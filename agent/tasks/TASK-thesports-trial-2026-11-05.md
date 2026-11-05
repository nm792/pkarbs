# TASK: TheSports free trial: timing capture, 5 Nov 2026

From: Claude, PK arbs thread "Test TheSports feed speed on trial" (5 Nov 04:40Z). Nick has emailed TheSports asking for the free
trial. Status: **PART A NOW; PART B WAITS FOR CREDENTIALS.**

## Question (one only)
Do TheSports push messages (tennis points, LoL/CS2/Dota kills, NBA plays) reach our server **before the Polymarket price moves**?
The thread measures this from what you record; you only record. No orders, no money, no P&L in this task.

## Part A: now (before credentials)
1. **Fixed IP for the whitelist.** The trial needs our server's public IPv4 whitelisted. Write it in
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
Read-only. One process: an MQTT client, a 1 s POST clob /books poller for live tennis/LoL/CS2/Dota/NBA/NFL game-winner tokens,
gamma every 5 min, and the PM sports WS. It runs alongside the tennis books logger (different file, same light rate).
Honest User-Agent `pkarbs-thesports-trial/1.0`; no 403 workarounds.
