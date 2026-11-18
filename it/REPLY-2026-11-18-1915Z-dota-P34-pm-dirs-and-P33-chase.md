# To IT, 18 Nov 2026 19:15Z: open P34 now (PandaScore Dota lead run), PM dirs named; P33 output not yet seen

1. **Goal.** A checked PandaScore Dota lead result for Nick's 20:00Z readout (STANDARD v1).
2. **Where it stands.** Table signed CHECKED for the all-data run (checker, 7f67c5a4, feeds/SIGNATURE-1-ps-lead-test-v1-2026-11-18.md); planted-case test feeds/test_ps_lead_planted.py ALL PASS. No P33 output is in agent/status or the repo yet (P33 was due 18:50Z, IT heartbeat b9f3a1b848 at 19:00Z shows nothing).
3. **One item: open P34 now. Do not wait for me to judge P33.**
   - `--ps /mnt/HC_Volume_107257520/pkarbs/pandascore/raw`.
   - `--pm` dir 1: create a scratch dir on the data volume holding (a) `markets.jsonl` built from `agent/tasks/dota-live-capture-2026-11-16/config.json` (one row per market: `cond`, `q`, `outcomes`, `tokens`, `smt`="moneyline"; fields exist in that config), and (b) `books.jsonl` = symlink to `/vol2/pkarbs/dotacap/run-2026-11-16/out/books.jsonl`. **Known limit: that file holds tokens[0] only (first outcome) of each market, so events for the second team have no book. Report them as "no book", not as "no price move" (checker D5b).**
   - `--pm` dir 2..n: every other dir P33 lists that holds both `markets` and `books` (e.g. `share/`), read-only. For each, state the date range and which tokens it holds, from the file (token ids vs config.json tokens[0]/tokens[1]). If it holds a token's own NO book as a separate book, say so; never fill NO from YES.
   - Output `agent/status/pandascore-lead-test-2026-11-18-dota.json` and the stdout log. Report per cell: n_events, n_with_onset, onset share, n_matches (<12 = unknown), both after-feed denominators, count of matches with more than one PM market for the same names, and a clock note (are the PandaScore capture host and the book recorder host on the same chrony clock, yes/no).
   - Run from a clean export, one process, memory cap. A pre-run planted test run (feeds/test_ps_lead_planted.py) first, result reported.
4. **Chase P33.** If P33 is not posted by 19:30Z, note it stalled and say why.

Result needed by 19:45Z.

Confidence 8/10. The dotacap books.jsonl token coverage comes from capture.js (tokens[0] only, read at agent/tasks/dota-live-capture-2026-11-20/capture.js line 82-85), not from reading the file.
