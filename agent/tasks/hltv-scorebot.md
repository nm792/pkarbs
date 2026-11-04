# TASK: HLTV scorebot kill-feed timing vs Polymarket price (OPEN, run 1 today)

Owner thread: "Time HLTV live scoreboard on CS2" (branch claude/project-thread-6tydow). Written 4 Nov 2026 ~11:55Z.
Nick approved scraping HLTV's live scoreboard with an open-source client (4 Nov 11:31Z). The Claude sandbox is blocked by
HLTV, so this runs on the server. Read-only. No orders, no keys, no logins.

## Question (one only)
Does HLTV's scorebot deliver CS2 kills to this server, and how many seconds before or after each kill does the
Polymarket map-winner PRICE move? (Compared against the price, not against Polymarket's sports score stream.)

## What it does
`agent/tasks/hltv-scorebot/capture.js` (Node 22, one dependency: socket.io-client 2.4.0 — the same client and protocol the
open-source gigobyte/HLTV library uses): reads the HLTV match page once per match with an honest User-Agent
(`pkarbs-research/1.0`), takes the scorebot URL from it, opens a socket.io connection and records every kill/round
message with our receive time. If the match page is refused, it records the refusal and tries the public scorebot URL
directly. It does NOT try to get past any Cloudflare challenge (no browser emulation, no challenge solving).
Polymarket: POST clob.polymarket.com/books every 1 s for the Match/Map winner markets of matches that are live, written on change.
HLTV robots.txt (read 4 Nov) allows /matches/<id>/ pages; only /matches?* is disallowed. We never request /matches?*.

## Load
HLTV: one page request per match at start, at least 6 s apart (3 requests in run 1), then one websocket per match.
Polymarket: one POST /books per second. Expected output well under 200 MB.

## Run 1 — now (connectivity + first timing on a small live match)
```
cd agent/tasks/hltv-scorebot && npm ci --no-audit --no-fund    # installs socket.io-client 2.4.0 only
OUT=$HOME/hltvcap/run1-2026-11-04; mkdir -p $OUT
setsid nohup systemd-run --scope -p MemoryMax=400M -p MemorySwapMax=0 timeout 12600 \
  node capture.js config-run1.json $OUT $(date -u +%FT%TZ) 2026-11-04T16:00:00Z > $OUT/stdout.log 2>&1 < /dev/null &
```
Start as soon as you read this; it stops by itself at 16:00Z (or `touch $OUT/STOP`).

### Pass / fail, fixed before running
- PASS: `scorebot.jsonl` has at least 50 `"ev":"log"` rows containing `"Kill"` for match 2400076 (MEIA NOITE vs DAMAJUANA,
  PM start 13:00Z), AND `books.jsonl` has rows for that match's slug, AND `timedatectl` shows NTP synchronized.
- FAIL: zero `log` rows by 13:45Z, or only `connect_error`/`disconnect` rows. Then stop the job (touch STOP) and report
  the `http.jsonl` lines (status codes, cf-mitigated) and the first 5 `connect_error` rows. Do not retry or change anything.
- No lag figures in the status file: the owner thread does the analysis from the raw files.

### Checks and copies
- At ~13:20Z: `tail -5 $OUT/capture.log; cat $OUT/http.jsonl; grep -c '"ev":"log"' $OUT/scorebot.jsonl; wc -l $OUT/*.jsonl`
  and paste the output into agent/status/hltv-scorebot.md.
- Every 30 min and at the end: gzip copies of $OUT/*.jsonl and capture.log to `live/cs2_feeds/raw/hltv-2026-11-04/` and commit.
  Copy from scratch each time (overwrite the .gz files), never append into the repo.
- Cleanup at the end: confirm the node process is gone (`ps aux | grep capture.js`, `free -m`) and say so in the status file.

## Run 2 — IEM Beijing playoffs, 6 Nov 01:00Z-09:30Z (ONLY after the owner thread reviews run 1 and says go in agent/inbox)
Same command with `config.json` (quarter-finals 2400006/2400007; later ids are idle until those matches are set),
OUT=$HOME/hltvcap/run2-2026-11-06, window 2026-11-06T01:00:00Z .. 2026-11-06T09:30:00Z, `timeout 31000`.
