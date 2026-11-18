# URGENT: run CS2 #422 now, then Goalserve tennis P30 (PandaScore thread, 18 Nov 23:35Z)

**Project goal:** find and build an automated, un-publicised edge worth $500/day; this row tests whether PandaScore's CS2 feed leads the Polymarket price.
**Where we stand:** no CS2 result exists (no run ID yet). `feeds/ps_lead_test.py` is signed CHECKED (PR #428). My earlier CS2 notes (#422, smoke) were returned NEEDS CHUNKING and never ran because I did not read `it/`; that was my fault. Nick has ordered this done now.
**Most important item:** ROW 1 below, started by **00:30Z 19 Nov** (committed start time; reply with the actual start time the moment it starts). Partial outputs committed as each finishes.

## ROW 1: CS2 #422 (one command, one routable chunk)
Exact command line, from the repo root on `origin/claude/project-thread-vg2ckg`:

`git fetch origin reviewer && git show origin/reviewer:it/REPLY-2026-11-18-2335Z-run_cs2_422.sh > /tmp/run_cs2_422.sh && bash /tmp/run_cs2_422.sh`

- Input: `--ps /mnt/HC_Volume_107257520/pkarbs/pandascore/raw`; `--pm` is every directory under `/mnt/HC_Volume_107257520` and `/vol2` that holds both `markets.jsonl*` and `books.jsonl*` (the script finds them and logs them in `agent/status/pandascore-cs2-422-pmdirs.log`).
- Outputs, committed each as soon as written: `agent/status/pandascore-cs2-422-plain.json` and `.log`, then `pandascore-cs2-422-latency.json` and `.log`, plus the pmdirs log.
- No Dota rows. No vendor contact. Nothing else is needed from anyone.
- If the script fails, commit the log and the exact error line; I will fix the script within 30 minutes.

## ROW 2: Goalserve tennis P30
Run immediately after ROW 1 finishes, as the Goalserve thread's note says; partial outputs committed as each finishes. I am telling that thread the same.

## Not in this note (will be separate, chunked)
Latency-field table, CS2 PM token-coverage check, smoke run and silent-gap share, CS2 both-token recorder code.

I will post the CS2 readout (UNCHECKED, exploratory) or a written reason by 04:00Z.

Confidence 7/10: command lines are exact and the script is simple, but I could not verify the CS2 `--pm` directories exist as the script assumes; the log will show which were found.
