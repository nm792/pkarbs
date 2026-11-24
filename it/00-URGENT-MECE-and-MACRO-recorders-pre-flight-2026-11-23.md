# 00-URGENT to IT, 23 Nov 2026 14:10Z (re-audit thread; R-070 A and D; R-058 pre-flight; R-047 no approval needed: offline code, read-only recorders)

1. **Goal:** find Polymarket edges that stack toward $200-500/day, each judged on own-token book depth recorded at decision time. Two edges are untestable today only because no book was recorded.
2. **Where it stands:** NO MEASURED $/day for MECE NO side (reopen rank 2) or macro stale quotes (reopen rank 5), because both-token books were never recorded at a release moment. Code is committed and passes pre-flight in a container (below); nothing has run on Prime.
3. **The one item:** run pre-flight 1 on Prime, then start the MECE recorder. Macro recorder needs nothing until 25 Nov 13:15Z.

Paste all output under `## MECE + MACRO recorders (23 Nov)` in `agent/status/goalserve.md`. Paper only: both recorders are read-only (public Gamma + market WebSocket), no keys, no orders.

## Row 1: MECE both-token recorder (3-way soccer sets), `it/pm_mece_books.js`
**Expected write:** about 0.3 GB/day worst case, normally less. Basis: container pre-flight 23 Nov 13:52-13:54Z with the 12 h look-ahead (MECE_HI_H=12): 87 three-way sets, 261 markets, 522 tokens, 4,964 rows and 205,626 bytes gz in 60 s, which includes the first full snapshot of every token (about 12 MB/h at that token count); the default live window (game start -3.5 h to +1 h) holds far fewer tokens. A 20 Nov smoke run measured 112 KB gz per 148 s for 462 tokens. The folder self-stops at the cap and the disk floor. **VOL2 is at 8.7 GB: the old default floor of 10 GB would stop it at once, so the commands below use floor 5 GB and cap 1 GB.**
Changes since P90b (commit with this note): R-058 single-instance pidfile lock, `preflight` mode, FATAL exit 4 when 0 tokens 120 s after start (set ALLOW_IDLE=1 only for a no-game window). Test: 9 checks (3 new: lock acquire, second copy refused, stale pid taken over); mutation proof: removing the live-pid check makes the test print `FAIL: second copy (live pid) not refused`.
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmmece; mkdir -p $D && cd $D
git -C /root/pkarbs fetch -q origin reviewer
for f in pm_mece_books.js test_pm_mece_books.js pm_cs2_books.js mece_score.py test_mece_score.py; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
sha256sum pm_mece_books.js; node test_pm_mece_books.js && python3 -I test_mece_score.py      # both PASS
# PRE-FLIGHT (R-058): 60 s of real data with the 12 h look-ahead so sets exist even between kickoffs; must print PASS (exit 0)
MECE_HI_H=12 node pm_mece_books.js $D/pf 2026-12-31T00:00:00Z 5 1 preflight 60; echo exit=$?
# expect {"preflight":"PASS","markets":N,"expected_tokens":2N,"ws_tokens":2N,"rows_written":>0}; paste it. If FAIL: stop, paste $D/pf/recorder.log tail.
# START (only after PASS), second copy must be refused:
nohup node pm_mece_books.js $D 2026-12-31T00:00:00Z 5 1 >> stdout.log 2>&1 &
sleep 5; node pm_mece_books.js $D 2026-12-31T00:00:00Z 5 1; echo second_copy_exit=$?    # must print REFUSED and exit 2
sleep 90; pgrep -f pm_mece_books.js; tail -4 recorder.log; ls -l books-*.jsonl.gz | tail -2
```
Then R-037 health read within 15 min: `python3 -I health_read.py ws $D --minutes 15 --pid-pattern pm_mece_books`. A line `live-markets=0` is not a fault in a no-game hour, but with the default window the recorder exits 4 after 120 s with 0 tokens; use ALLOW_IDLE=1 in the start line only if you want it to idle through a gap. Daily scorer as in P90b (cron 00:35Z, `mece_score.py`). **Release moments to watch** (public calendars, verify): soccer 3-ways every match day this week; Taiwan local elections 28 Nov; FOMC 9 Dec. The recorder does not need a release time: it covers every 3-way set live.
**Protect:** add `pkarbs/pmmece` to the ship_raw exclude and protected lists.

## Row 2: macro release book recorder, `it/pm_event_books.js` (new), first release Wed 25 Nov 13:30Z
Records both tokens' own books for the listed contracts, window R-15 min to R+15 min only, idle otherwise. Test: `node test_pm_event_books.js` prints PASS (6 checks).
**Expected write:** at most 10 MB per release (cap 0.5 GB self-stop). Basis: container pre-flight 23 Nov 13:55Z, 14 markets / 28 tokens, 60 s quiet market: 204 rows, 14,437 bytes (about 0.9 MB/h quiet); a release burst is not measured, so 10 MB per 30-min window is a 20x allowance.
**Next 3 US releases with listed PM contracts (Gamma, read 23 Nov 13:57Z; total event volume):**
| # | release | R (UTC) | slugs | markets | volume |
|---|---|---|---|---|---|
| 1 | Core PCE Oct | Wed 25 Nov 13:30 | core-pce-mom-october-2026, core-pce-yoy-october-2026 | 7+7 | $27K + $43K |
| 2 | Nov jobs (unemployment rate) | Fri 4 Dec 13:30 | november-unemployment-rate-2026 | 9 | $19K |
| 3 | FOMC Dec | Wed 9 Dec 19:00 (14:00 ET, verify on the Fed calendar) | fed-decision-in-december-20260729232808632, how-many-dissent-at-the-december-fed-meeting-20260730000304473 | 5+5 | $51.1M + $69K |
Then CPI Thu 10 Dec 13:30: core-cpi-mom-november-2026, core-cpi-yoy-november-2026, november-inflation-us-monthly, november-inflation-us-annual (7+10+10+12 markets, $7K-57K). CPI is the same capture shape; add it after row 3.
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/pmevent; mkdir -p $D && cd $D
for f in pm_event_books.js test_pm_event_books.js pm_cs2_books.js pm_mece_books.js; do git -C /root/pkarbs show origin/reviewer:it/$f > $f; done
sha256sum pm_event_books.js; node test_pm_event_books.js
# PRE-FLIGHT (any time; ignores the window): must print PASS
node pm_event_books.js $D/pf 2026-11-25T13:30:00Z core-pce-mom-october-2026,core-pce-yoy-october-2026 5 0.5 preflight 60; echo exit=$?
# START for release 1 (idle until 13:15Z, stops at 13:45Z; start any time before 13:10Z), one folder per release:
nohup node pm_event_books.js $D/pce-20261125 2026-11-25T13:30:00Z core-pce-mom-october-2026,core-pce-yoy-october-2026 5 0.5 >> $D/pce.log 2>&1 &
```
Live read at 13:10Z, 13:20Z and after 13:45Z: `pgrep -f pm_event_books; tail -3 $D/pce-20261125/recorder.log; ls -l $D/pce-20261125/books-*.jsonl.gz`; the file must grow after 13:15Z, and `ws open, tokens 28` must appear. Repeat rows 2 and 3 with their slugs and R before 4 Dec 13:10Z and 9 Dec 18:40Z. The re-audit thread writes the scorer (own-token ask at R+1 s plus the sports/finance taker delay read from each market's own `seconds_delay`, markout at +15 s and +60 s) offline once row 1 data exists.
