# PandaScore trial: dated window schedule, checks and fallbacks (PandaScore thread, 19 Nov 2026 08:25Z)

**Goal:** find an automated, un-publicised edge worth $500/day; this trial (CS2 and Dota, about 18 Nov to 2 Dec, end date is Nick's assumption, no vendor date) must lose no match window. **Where we stand:** PandaScore capture (ll_capture, PID 2235520 since 16 Nov) runs 24/7; CS2 Polymarket book recorder running since 03:29:52Z to 2 Dec 00:00Z (pid 2690054); Dota Polymarket book recorder running to 30 Nov (pid 2539785); CS2 probe PID 2694972 starts 08:50Z. **Most important item:** the CS2 probe is a one-off; the supervisor `it/pandascore_cs2_probe_loop.sh` (new, tested) covers every later window automatically (job 6 in the IT priority list).

## Design: no window can be missed because nothing is tied to one date
- PandaScore sockets: discovery every 60 s, one socket per CS2/Dota match from `opens_at`; a silent socket is not an error (capture rule). Fallback if capture dies: IT restarts the tmux `pandascore` session; there is no replay of missed matches, so a dead capture is a lost window: check hourly (below).
- Polymarket CS2 books: recorder discovers markets every 5 minutes (window now -8 h to +36 h), tokens subscribed live; new matches appear automatically.
- CS2 probe loop: runs the probe in 120-minute cycles from 11:20Z today to 2 Dec 00:00Z, retries every 5 minutes when nothing is live or PREFLIGHT fails; one `.log` and `.json` per cycle, one line per cycle in `probe-loop.log`.
- Daily look k, 01:00Z on 20 Nov to 1 Dec (12 looks, PREREG), on the previous UTC day's data. Verdict and audit 2 Dec.

## Dated windows known on 19 Nov 08:25Z (Polymarket gamma, `startTime`; PandaScore upcoming list is the authority and I cannot read it from the cloud session)
| UTC | game | window | check / fallback |
|---|---|---|---|
| 19 Nov 09:00 | CS2 | gothboiclique vs STATE (United21 Playoffs), probe 08:50Z | at 09:05Z log shows `CS2 feeds open now`, matched markets, PREFLIGHT; else fix, test, relaunch within 15 min |
| 19 Nov 11:00 | CS2 | GamerLegion vs Inner Circle (Stake Ranked Ep 6), inside probe run to 11:20Z, then loop | 11:25Z loop-log has a cycle line |
| 19 Nov 23:00 | CS2 | LAG Gaming vs Villainous (CROSSFIRE) | 23:10Z loop-log cycle with events |
| 20 Nov 01:00 | CS2 | four CROSSFIRE Playoffs matches | 01:10Z same; daily look 1 starts ~01:00Z (19 Nov data) |
| 20 Nov 09:00 | CS2 | Balkan Outlaws vs FORZE Reload (EPL Playoffs) | 09:10Z |
| 20 Nov 16:00, 22 Nov 20:00 | CS2 | ESEA Advanced Europe | loop |
| 20 Nov 10:00 | Dota | BLAST Slam IX window opens (20-29 Nov); Dota capture task P17b needs agent/tasks/dota-live-capture-2026-11-20 (restored in PR #438) | 09:30Z check files exist; 10:15Z Dota recorder rows growing |
| 21 Nov 12:00, 15:00, 18:00 | CS2 | CCT Europe Closed Qualifier series | loop |
| 22 Nov 03:00 | CS2 | Overtake vs Detonate (CROSSFIRE) | loop |
| 25 Nov | CS2 | Major day, AT RISK (Nick); confirm PM markets exist on 24 Nov | 24 Nov 12:00Z: count `Counter-Strike` events for 25 Nov in gamma; if none, say so |
| 29 Nov | Dota | BLAST Slam IX ends; Dota PM recorder ends 30 Nov 00:00Z (P40) | 29 Nov: extend to 2 Dec if the trial runs on (ask IT, 1 line) |
| 1 Dec / 2 Dec | all | last daily look 1 Dec ~01:00Z; recorder and loop end 2 Dec 00:00Z | 2 Dec verdict + independent audit |
LoL: out of scope (PandaScore feed capture excludes LoL per task).

## Checks (each takes under 2 minutes, from the reviewer-branch pastes)
- Every hour: PandaScore capture file for the current hour exists and grew (agent/status/pandascore.md or `ls -l` paste). If not, IT restarts tmux `pandascore` at once.
- 00:30Z daily: CS2 recorder `books.jsonl` rows grew in the last 10 minutes and disk above the 15 GB floor; Dota recorder same.
- Before each window above: T-60 minutes recorders growing; T-10 loop log line < 10 minutes old; T+15 events and quotes seen (loop log `FINAL` line or running 5-minute summary).
- Fallback ladder for any failed check: 1) fix in my committed code with test, 2) relaunch via the IT priority list owner, 3) name the exact blocker in a REPLY within 15 minutes.

Confidence 7/10: capture and recorder facts are from IT's pastes (commit b1b4358f42); the window list is Polymarket's, incomplete for days beyond 22 Nov (PandaScore's upcoming list is not readable from here), which is why the loop does not depend on it.
