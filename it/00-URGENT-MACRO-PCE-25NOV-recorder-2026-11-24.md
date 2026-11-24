# 00-URGENT to IT, 24 Nov 2026 (re-audit thread; R-077 A, R-078 item 2, R-058). First capture: Core PCE, Wed 25 Nov 13:30Z. Read-only recorder, public Gamma + CLOB + market WebSocket, no keys, no orders.

1. **Goal:** find Polymarket edges that stack toward $200/day, judged on own-token book depth recorded at decision time. 2. **Where it stands:** no macro own-token capture exists; recorder it/pm_event_books.js passes pre-flight in a container (14 markets, 28/28 tokens, 136 rows, 14,319 B in 60 s). 3. **The one item:** it must be running before **12:55Z on 25 Nov** (idle until 12:30Z, records 12:30-14:00Z).
**Expected write:** at most 10 MB per release; folder cap 0.5 GB self-stop. Basis: 14,319 B in a quiet 60 s on 28 tokens (about 0.9 MB/h), x about 20 for the release burst. VOL2 is low: use floor 5 GB (the default 10 GB would stop it at once).
Code SHA-256 (first 16): pm_event_books.js 178a2102e4b117a7, pm_mece_books.js 95513f334e8cecdb, pm_cs2_books.js 8cccab59fbbf9615, macro_pickoff_score.py 967a69189935f26e. Tests: `node test_pm_event_books.js` PASS (7 checks); `python3 -I test_macro_pickoff_score.py` PASS (9 checks, mutation-proofed).
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmevent; mkdir -p $D && cd $D
git -C /root/pkarbs fetch -q origin reviewer
for f in pm_event_books.js test_pm_event_books.js pm_cs2_books.js pm_mece_books.js macro_pickoff_score.py test_macro_pickoff_score.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
sha256sum pm_event_books.js macro_pickoff_score.py | cut -c1-16; node test_pm_event_books.js && python3 -I test_macro_pickoff_score.py
# PRE-FLIGHT (R-058), now, ignores the window; must print PASS (exit 0), "ws_tokens" == "expected_tokens" == 28:
node pm_event_books.js $D/pf 2026-11-25T13:30:00Z core-pce-mom-october-2026,core-pce-yoy-october-2026 5 0.5 preflight 60; echo exit=$?
node pm_event_books.js $D/pf 2026-11-25T13:30:00Z x 5 0.5 preflight 5 & sleep 1; node pm_event_books.js $D/pf 2026-11-25T13:30:00Z x 5 0.5 preflight 5; echo second_exit=$?   # second copy: REFUSED, exit 2
# START (any time before 12:55Z on 25 Nov; defaults PRE_MIN=30 POST_MIN=30):
nohup node pm_event_books.js $D/pce-20261125 2026-11-25T13:30:00Z core-pce-mom-october-2026,core-pce-yoy-october-2026 5 0.5 >> $D/pce.log 2>&1 &
sleep 5; pgrep -f pm_event_books.js; tail -2 $D/pce-20261125/recorder.log; head -c 400 $D/pce-20261125/markets.jsonl     # markets.jsonl must show seconds_delay (a number) for every market
```
**Health reads to paste in INBOX (R-037):** 12:35Z (`ws open, tokens 28` in recorder.log), 12:50Z and 13:10Z (`ls -l --time-style=full-iso $D/pce-20261125/books-*.jsonl.gz`, twice 60 s apart; the file must grow), 14:05Z (`done` in recorder.log, folder size). `python3 -I /root/pkarbs-tools/health_read.py ws $D/pce-20261125 --minutes 15 --pid-pattern pm_event_books` where available. Ship nothing: add `pkarbs/pmevent` to the protected list.
After the release the re-audit thread posts `winners.json` (bucket winners mapped from the PRINT) and runs `python3 -I macro_pickoff_score.py $D/pce-20261125 2026-11-25T13:30:00Z winners.json --latency 0.5` (and 2, 5, 15) offline. Releases 2-4 (same command, new slugs and R): jobs Fri 4 Dec 13:30Z `november-unemployment-rate-2026`; Fed statement Wed 9 Dec 19:00Z (verify) `fed-decision-in-december-20260729232808632,how-many-dissent-at-the-december-fed-meeting-20260730000304473`; CPI Thu 10 Dec 13:30Z `core-cpi-mom-november-2026,core-cpi-yoy-november-2026,november-inflation-us-monthly,november-inflation-us-annual`.
