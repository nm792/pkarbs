## P15d2 step 1/3 (2026-11-17 13:36–13:40Z)

- Data-volume free bytes: 41,877,303,296 at 13:36Z; 40,790,061,056 after input copy; both above the 20 GB gate. Code commit: `1cb5c8474b1f64040ec0a8978d866f5b5bc43e2e`.
- Source SHA-256: `feeds/goalserve_odds_vs_pm.py` `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5`; `feeds/test_goalserve_odds_vs_pm.py` `b977ea1bea9edb4aa63b5444da87a1fda08b068e5ff3542f4370fd99cfc97e8e`; `feeds/ps_lead_test.py` `0cbd918ed6e346c91293edbac8f648a30c47a5b3e244fb8af7a08f81804cfc99`.
- `py_compile`: COMPILE_OK. Isolated test: exit 0, `ALL PASS`. First test attempt exhausted `/tmp` (4,096 bytes free); unchanged retry with `TMPDIR` on the data volume passed.
- Inputs collected by prescribed rsync plus `cp -n`: 95 files, first `esports_2026111315.jsonl.gz`, last `esports_2026111713.jsonl.gz`, `du -sh` 550M. `$T/gs` retained at `$T/gs`.
- The four runs were not started; no result JSON/logs exist yet. No script, process or configuration changed. Step 1 complete; P15d3/P15d4 remain queued.


## P15d3 step 2/3 (2026-11-17)

- The four runs were already complete by this check. `runs.log` records shift 0 exit 0 at 14:29:43Z, shift 5 exit 0 at 14:35:58Z, shift 15 exit 0 at 14:42:18Z, and shift 25 exit 0 at 14:48:47Z. The runner file was created 14:22:46Z and the shift-0 log began 14:23:18Z; the process PID and exact process start UTC were not retained, and no matching process remained at inspection. No PID is inferred.
- Four valid result JSONs are present, each >1 KB and each with 214 `match_list` rows: shift0 113,234 bytes; shift5 112,693; shift15 112,698; shift25 112,804. Results remain UNCHECKED pending the independent audit. A scan found no IP-like values, hostnames, or credential-like fields.
- Data volume free: 33,892,593,664 bytes at 15:03Z. The retained input set is 95 files, `esports_2026111315.jsonl.gz` through `esports_2026111713.jsonl.gz`, 550 MB; scratch directory 551 MB. Inputs and outputs remain in the Goalserve scratch directory on the data volume for the next step.
- Code commit: `1cb5c8474b1f64040ec0a8978d866f5b5bc43e2e`. SHA-256 matches: `feeds/goalserve_odds_vs_pm.py` `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5`; `feeds/test_goalserve_odds_vs_pm.py` `b977ea1bea9edb4aa63b5444da87a1fda08b068e5ff3542f4370fd99cfc97e8e`; `feeds/ps_lead_test.py` `0cbd918ed6e346c91293edbac8f648a30c47a5b3e244fb8af7a08f81804cfc99`. `py_compile` passed and the isolated test ended `ALL PASS` at 15:03Z.
- At the time of the P15d3 report, no script, process, or configuration changed and the four JSONs had not yet been copied into `agent/status/`; the copy was completed in P15d4 below.


## P15d4 step 3/3 (2026-11-17 16:16Z)

- P15d4 outputs copied from the retained scratch run into `agent/status/`: shift0 113,234 bytes; shift5 112,693; shift15 112,698; shift25 112,804. Each contains 214 `match_list` rows and is greater than 1 KB. SHA-256: shift0 `05034c393a8278f4dff3f14d20015b2702f961ef0d113a41eea92bc87369a4bb`; shift5 `16b049f8212f605225d02f83d7043f21035f14cd58c12aa692fb7acf0eb3417c`; shift15 `a6cca6b2239927ede55f6e36157ef9bbff844ee00700ab65168a892a4a28e9f9`; shift25 `7ae134ee87ceec15103be7d5f53bb49c7b79fa039aaad658d02d34dd590da1d8`.
- Run exits/times from the already-recorded P15d3 evidence: shift0 exit 0 at 14:29:43Z; shift5 exit 0 at 14:35:58Z; shift15 exit 0 at 14:42:18Z; shift25 exit 0 at 14:48:47Z. Results remain UNCHECKED pending the independent audit; no interpretation added.
- Privacy scan of all four result files: clear. Scratch inputs and outputs remain on the data volume for the audit. No code, process, or configuration changed.


## E1 smoke (18 Nov) — blocked at disk gate

- At 2026-11-18 02:12Z, available bytes on the data volume: 10,917,199,872. The required gate is >20 GB free; it failed. No pull, scratch creation, compile, test, smoke run, or other data-volume job was started.
- Result: NOT RUN. Reopen P18 only after the data-volume gate is met.


## Disk inventory (18 Nov)

Capture time: 2026-11-18 04:35Z. P18 measured the data-volume mount at 10,917,199,872 bytes free at 02:12Z; the same mount is `/mnt/HC_Volume_107257520` and now reports 28G free (above P18's 20 GB gate). This inventory does not authorize deletion or by itself reopen P18; no deletion list was produced.

`df -B1 -h / /mnt/HC_Volume_107247271 /mnt/HC_Volume_107257520`:
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        38G   23G   13G  65% /
/dev/sdb         49G   37G   11G  79% /mnt/HC_Volume_107247271
/dev/sdc         98G   69G   28G  74% /mnt/HC_Volume_107257520
```

Data-volume depth-2 usage (`du -sh --max-depth=2` failed: `du: summarizing conflicts with --max-depth=2`; GNU du rejects `-s` with `--max-depth`. Equivalent `du -h --max-depth=2`, sorted descending, top 40):
```text
66G	/mnt/HC_Volume_107257520
60G	/mnt/HC_Volume_107257520/pkarbs
40G	/mnt/HC_Volume_107257520/pkarbs/thesports
8.4G	/mnt/HC_Volume_107257520/pkarbs/scratch
6.4G	/mnt/HC_Volume_107257520/pkarbs/from-vol
3.2G	/mnt/HC_Volume_107257520/pkarbs-ps-step2
2.8G	/mnt/HC_Volume_107257520/pkarbs-ps-step2/rn1
1.9G	/mnt/HC_Volume_107257520/pkarbs/tennis
1.5G	/mnt/HC_Volume_107257520/pkarbs/thesports-cricket
650M	/mnt/HC_Volume_107257520/pkarbs/charts
432M	/mnt/HC_Volume_107257520/pkarbs/dotacap
327M	/mnt/HC_Volume_107257520/pkarbs/goalserve
275M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/winmodels
140M	/mnt/HC_Volume_107257520/pmhl5s
115M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/live
94M	/mnt/HC_Volume_107257520/weekend-perps
88M	/mnt/HC_Volume_107257520/pkarbs/lol
64M	/mnt/HC_Volume_107257520/.p4-20261116T2246Z
46M	/mnt/HC_Volume_107257520/pkarbs/goalserve-audit-20261117
18M	/mnt/HC_Volume_107257520/pkarbs/oddspapi
17M	/mnt/HC_Volume_107257520/oddspapi
16M	/mnt/HC_Volume_107257520/oddspapi/hist
13M	/mnt/HC_Volume_107257520/nt_live_fire
9.3M	/mnt/HC_Volume_107257520/nvda-huang
9.2M	/mnt/HC_Volume_107257520/nvda-huang/raw
8.8M	/mnt/HC_Volume_107257520/pkarbs/cricket
7.0M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/rugby
5.6M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/reports
3.9M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/agent
3.5M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/weekend-perps
3.4M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/mentions
2.9M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/chess
1.7M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/forecast-edges
1.3M	/mnt/HC_Volume_107257520/pkarbs-ps-step2/reviews
688K	/mnt/HC_Volume_107257520/nt_live_fire/.t40a-stage-224410
664K	/mnt/HC_Volume_107257520/nt_live_fire/live
632K	/mnt/HC_Volume_107257520/pkarbs-ps-step2/shadow
604K	/mnt/HC_Volume_107257520/pkarbs-ps-step2/agent
456K	/mnt/HC_Volume_107257520/pkarbs/mentions
```

`ship_raw` check: no live `ship_raw.sh` process found (the first `pgrep -af` invocation also matched its own checker command; that self-match was excluded). Crontab has:
```text
50:*/30 * * * * SHIP_HOME=/root/ship /root/ship/ship_raw.sh >> /root/ship/ship.log 2>&1  # note 252
```

`/root/ship/writers.conf` identifies the `goalserve` source folder as `/mnt/HC_Volume_107257520/pkarbs/goalserve`. Listing results:
```text
$ ls -1t <folder> | head -3
goalserve_20261117.jsonl
tennis_payloads
hockey_nhl_payloads
$ ls -1t <folder> | tail -3
hockey_nhl_payloads
esports_payloads
basketball_payloads
$ ls -1 <folder> | wc -l
5
```

Largest measured consumers are `pkarbs/thesports` (40G) and `pkarbs/scratch` (8.4G). No files or processes were changed and nothing was deleted. Reviewer deletion list is still required before P18 is reopened.

## G inventory (18 Nov) — waiting

- The prescribed `git pull -q` failed because the checkout has local changes in tracked files and untracked files that would be overwritten. Exact error: `error: Your local changes to the following files would be overwritten by merge:`; `error: The following untracked working tree files would be overwritten by checkout:`; `Aborting`. No stash or cleanup was performed.
- The inventory was not run. The command's script is present on the fetched origin branch but absent from the stale local checkout; following the task gate, no workaround or retry was attempted.
- At 2026-11-18 05:04Z, `df -h / /mnt/HC_Volume_107257520` showed root 13G free and data volume 27G free.
- Status: waiting for a safe checkout/pull; no inventory output is claimed.

## E1 smoke (18 Nov 05:40Z) — waiting: required files absent

- The prescribed first check returned local checkout HEAD `026be71fe877197d43fc78056070b7c8d86cd741`. `ls -l feeds/goalserve_odds_vs_pm_v2.py feeds/test_goalserve_odds_vs_pm_v2.py` reported `No such file or directory` for both files.
- Per P18's explicit stop rule, the smoke, compile and tests were not run; no data-volume output was created and no pull, stash or cleanup was attempted.
- The exact 02:12Z command recorded in the earlier P18 reply was `df -B1 --output=avail /mnt/HC_Volume_107247271`; it reported 10,917,199,872 bytes. The P18 note's named data-volume path is `/mnt/HC_Volume_107257520`, so the recorded command measured the other mount.
- Status: waiting for the two required files to be present in the prescribed checkout; no smoke result is claimed.


## E1 smoke (18 Nov 06:14Z)

Status: **run attempted; required smoke pass condition not met.**

- Data-volume gate passed at 06:14Z: 26,427,822,080 bytes available (>20 GB).
- Exported `feeds/` from the fetched project branch tip `7ca1509d736a2349c3097c0b58b8da1b3fcfcfeb` into a fresh scratch directory; the checkout was not modified. Source SHA-256: `goalserve_odds_vs_pm_v2.py` `8885752f54c3dc0c13cc0b60270fa76698b2fc1aca1746b8e1f8f95357f5fd4c`; test `04f46d566359930851db9a8cfb77dd2453b4c90b4c346bc85aa3053275d3f6b1`.
- `py_compile` passed and the self-test printed `ALL PASS`.
- Smoke command exited 1 at 06:18Z. Exact output: `look K=-1 is outside 1..20 (no complete UTC day since 2026-11-18 or past the last look)`. No `smoke.json` was produced; therefore `files > 0` and `NO_TRACEBACK` pass criteria were not established. The final 600 bytes had no traceback/error text, but this does not change the failed run.
- No cells or verdicts were read or reported. No other data-volume job was started by this run.

Evidence: `agent/status/goalserve.md` section `E1 smoke (18 Nov 06:14Z)`; self-test and smoke logs in the P18 scratch output directory on the data volume.


## G inventory (18 Nov) — completed

- Ran the G2 read-only inventory script from the fetched origin branch copy, without pulling, stashing, cleaning, or changing the pkarbs checkout.
- `df -B1 --output=avail` on the data volume: 29,353,795,584 bytes available.
- Script exit=0; stdout 732 bytes; stderr empty. It found recorder directories: cricket (22 events, books 2026-11-05 15:10–17:46Z), scratch/reexport_full (cricket 35, cs2 110, dota2 67, lol 4, nba 27, nfl 14, tennis 1545; no books file), tennis (133 events, books 2026-11-05 15:10–21:10Z), and final-topics-32295b (cricket 101, cs2 397, dota2 168, lol 7, nba 73, nfl 27, tennis 3839; books 2026-11-08 00:11Z–2026-11-18 06:27Z).
- Evidence: `/mnt/HC_Volume_107257520/pkarbs/scratch/P18-20261118/inventory.out`; script copied from `feeds/pm_recorder_inventory.py` at fetched origin tip.

## E1b smoke (18 Nov)

- PASS at 07:48:54Z: compile and isolated self-test passed; smoke exit 0, `files=24`, `smoke_not_a_result=True`, no traceback. Report: `agent/outbox/TO-IT-CHUNK-E1b-smoke-run-goalserve-odds-v2-2026-11-18-0740Z.md`.


## H capture check (18 Nov)

- Read-only check at 08:21:24Z: Goalserve capture PID 4045212 was running (start 17 Nov 09:00:06Z); tmux session `goalserve` existed. No restart attempted.
- 18 Nov hour-file count: esports 3, tennis 3, hockey_nhl 3, basketball 3 (hours 06, 07, and in-progress 08). The 08 files were still growing at check time.
- `goalserve_20261118.jsonl` was absent. The directory instead had `goalserve_20261117.jsonl` (55,131,766 bytes; modified 08:21:23Z). Capture activity is evidenced by the live PID and current hour files; the missing 18 Nov daily log's cause is not established.
- No `*_STOP.log` existed. Available space on the data volume: 28,013,322,240 bytes.
- Latest tennis JSONL structure: outer keys `body`, `recv_ns`; `body` is a string containing JSON. No key, URL, or credential was output.
- Full command output for this check is retained in the session output, not committed; only the requested summary is recorded here.


## I tennis probe (18 Nov)

- Export commit: `322d8129253ea9b12d9f8b53e7126f3ae3d0ca07`; `feeds/gs_sport_probe.py` present, SHA-256 `5bc8d9dc2665254af0d0de19eff638c7efd34714446b8f78b9fca2947ac81304`.
- Local 06/07 hour files were absent; retrieved the exact two files from the existing `<box>` copy. No capture or configuration was changed.
- Probe exit 0; files=2, polls=44709, events=0, counters rows=3752, `market_names_used {}`, `league_prefixes_seen {"unparsed": 95671}`. No events matched the parser; no tennis verdict or market match is claimed. The probe itself truncates `market_names_excluded` to 1,500 characters.
- Full stdout follows verbatim. Raw output: `/mnt/<data-volume>/pkarbs/scratch/P26-20261118/probe.out`.

```text
files 2 polls 44709 events 0
counters {"rows": 3752}
bm_values {"''": 3752}
market_names_used {}
market_names_excluded {"To Win": 94405, "Odd/Even": 90712, "Next Break Serve": 61650, "Go The Distance?": 50510, "Set 1 Winner": 49665, "Set 2 Winner": 47609, "Game Winner (1st Set)": 44883, "Game to Deuce (1st Set)": 44869, "Game Score (1st Set)": 44869, "Game Winner (2nd Set)": 39266, "Set 2 Score": 39260, "Game to Deuce (2nd Set)": 39260, "Total Sets": 34627, "Correct Score (1st Set)": 29433, "Set 1 Correct Score Group": 29240, "Set 1 Race to": 26999, "Set 1 to Break Serve": 25300, "Set 2 to Break Serve": 24569, "Set 1 Correct Score Any Player": 24122, "Set 1 Score after 6 Games": 21472, "Set 2 Race to": 21296, "Set 1 Lead after": 20458, "Set 2 Correct Score Any Player": 20347, "Correct Score Group (2nd Set)": 19762, "Correct Score Any Player (2nd Set)": 17818, "Set 1 Score after 4 Games": 16070, "Score after 6 Games (2nd Set)": 15882, "Lead after (2nd Set)": 14621, "Set Betting": 13311, "Score after 4 Games (2nd Set)": 11520, "Player 1 To Win in Straight Sets": 8583, "Setcast": 8583, "Double Result": 8583, "Player 2 To Win in Straight Sets": 8563, "Total Games in Set 1": 8161, "Set 1 Handicap": 7921, "Total Games in Set 2": 4728, "Set 2 Handicap": 4728, "Game Score (3rd Set)": 4291, "Game to Deuce (3rd Set)": 4291, "Game Winner (3rd Set)": 4291, "Total Tie Breaks In Match": 3838, "Tie Break Handicap": 3838, "Tie Break Score": 3838, "Correct Score Group (3rd Set)": 3684, "Correct Score (3rd Set)": 3684, "Tie Break - Total Points (1st Set)": 3366, "Tie Break Score (1st Set)": 3366, "Tie Break Sc
league_prefixes_seen {"unparsed": 95671}
sample teams Alberto Odiseo Alvarado Berrospi | Alan Fernando Rubio Fierros
sample teams Hao Sheng Koay | Gunawan Trismuwantara
sample teams Natsuki Yamamoto | Shaheed Alam
league strings [["M15 Antalya", 15477], ["M15 Hua Hin", 11865], ["M15 Kuala Lumpur MD", 10251], ["UTR Pro Yokohama", 8681], ["Challenger Kobe MD", 8334], ["M25 Heraklion", 7260], ["UTR Pro Yokohama Women", 6433], ["W50 Heraklion", 6247], ["M25 Bhubaneswar", 4355], ["W75 Sydney WD", 3531], ["M25 Bhubaneswar MD", 3146], ["M15 Kuala Lumpur", 3068]]
```


## J tennis smoke (18 Nov)

- Clean `feeds/` export from commit `09b9665e64f56daf0095048828073f6fede87517`; no checkout pull, stash, or cleanup.
- Smoke exit 0 at 13:06:44Z; last-600-byte log check: `NO_TRACEBACK`. `sport tennis`, `smoke_not_a_result True`, files=2, events=1575.
- Drops: `events_no_pm_market=541`, `events_dropped_by_match_cap=262`, `events_tie_d_zero=15`, `book_rows_one_sided=4333`, `pm_book_rows_time_from_ms=126296`.
- Audit counters: rows=3752, skip_bad_odds=2674, skip_suspended=4845, events=1575, baseline_cleared_not_valid_open=89, baseline_cleared_poll_gap_gt_10s=18, payloads_after_poll_gap_gt_10s=1.
- `market_names_used`: `{"To Win": 94405}`; `league_prefixes_seen`: `{"tennis": 95671}`.
- Matches with events=43; PM candidates 0/1/2+ = 13/30/0. No cells or verdicts reported; smoke only, not a result.
- Evidence: `pkarbs/scratch/goalserve-tennis-smoke-20261118/smoke.json` and `smoke.log` on the Prime data volume. The 06/07 input SHA-256 values match the exact copies used in chunk I.
- No capture, configuration, process, or live code was changed.

## L tennis exploratory (18 Nov)

- Fetched project branch tip: `45b89dd0f108bef86d62029b4945a601a9e259d4`. Clean export contained `feeds/goalserve_odds_vs_pm_v2.py` (SHA-256 `cbd0f397f09eb92acdd2b6735c093e6a7bed97fcfa4a45dbe32a33f6cb3d1af0`); ran the signed script unchanged in `--smoke` mode. Inputs copied from `<box>` plus existing Prime files; no capture, configuration, live code, or process was changed.
- Day 17: exit 0; 15 hourly files, UTC coverage begins 09:00Z; `smoke_not_a_result=True`; 17,987 events; 100 primary matches / 3,115 events; `CELL tennis|Match Winner`: z_eq 8.2810, mean_d_per_match 0.01187, `plants_ok=True`, verdict `meets bar (needs audit)`. Counters: rows 25,395, baseline-cleared poll-gap >10s 170, post-gap payloads 5, suspended 50,745, bad odds 34,491, invalid-open clears 1,392. Drops: no PM market 6,069; ambiguous rematch 93; PM book timestamps from ms 1,042,355; one-sided books 29,089; match cap 5,833; tie d=0 129; PM recorder silent >300s 15.
- Day 18: exit 0; 24 hourly files; data through 2026-11-19 00:00Z (day 18 is partial); `smoke_not_a_result=True`; 25,463 events; 100 primary matches / 3,203 events; `CELL tennis|Match Winner`: z_eq 11.3841, mean_d_per_match 0.01738, `plants_ok=True`, verdict `meets bar (needs audit)`. Counters: rows 39,794, baseline-cleared poll-gap >10s 278, post-gap payloads 7, suspended 58,699, bad odds 39,432, invalid-open clears 1,659, malformed JSON 1. Drops: no PM market 6,040; ambiguous rematch 555; PM book timestamps from ms 1,402,836; one-sided books 41,489; match cap 10,149; tie d=0 168.
- Logs ended with `match_list rows: 308` (day 17) and `match_list rows: 403` (day 18); neither contains a traceback. JSON and logs scanned for IP-like dotted quads: zero. Files retained at `/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-explore-tennis/explore-20261117.{json,log}` and `explore-20261118.{json,log}`; inputs retained under `gs/`. These are exploratory smoke outputs, not a pre-registered look or a pass.

## F look 1 (2026-11-19)

- Command: signed `feeds/run_daily_look.sh esports`; invoked after 00:30Z as required. Script exit 1.
- It stopped at its signed-file gate before running the self-test or producing a result. Observed hashes: `feeds/goalserve_odds_vs_pm_v2.py` `cbd0f397f09eb92acdd2b6735c093e6a7bed97fcfa4a45dbe32a33f6cb3d1af0`; `feeds/test_goalserve_odds_vs_pm_v2.py` `9d4bdad46183f44d160b1e14bc6cae9bffbbac1aa3bc43625d20087d9fcdc6d8`; `feeds/ps_lead_test.py` `4b67d26f6f9f419cd330fdca7ee3c396ed99d5db9ddc56c5370012120c296cb1`; `feeds/goalserve_odds_vs_pm.py` `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5`.
- Exact stop: `STOP: code differs from the signed hashes; ask the Goalserve thread for the new SIGNED commit`. Expected results (`look=1`, `plant_c=0.01`, result SHA) were not produced. No code or capture changed.
- Full command stdout:
  - `date 2026-11-19T01:45:57Z avail_bytes 18584768512`
  - `commit d9f9f905c9eca26eaf0e432fb13f24e9fbc94658`
  - `cbd0f397f09eb92acdd2b6735c093e6a7bed97fcfa4a45dbe32a33f6cb3d1af0  feeds/goalserve_odds_vs_pm_v2.py`
  - `9d4bdad46183f44d160b1e14bc6cae9bffbbac1aa3bc43625d20087d9fcdc6d8  feeds/test_goalserve_odds_vs_pm_v2.py`
  - `4b67d26f6f9f419cd330fdca7ee3c396ed99d5db9ddc56c5370012120c296cb1  feeds/ps_lead_test.py`
  - `a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5  feeds/goalserve_odds_vs_pm.py`
  - `STOP: code differs from the signed hashes; ask the Goalserve thread for the new SIGNED commit`


## PK priority jobs 1 and 4-5 launched (19 Nov)

- Job 1 Goalserve live probe: offline test printed `ALL PASS`; launched at 03:29:12Z, PID 2689593, 90-minute run. The first observed preflight has not passed for any sport; the probe remains running and will re-check at its end.
- Exact first PREFLIGHT and NO NUMBER output follows (captured from the process log):

```text
PREFLIGHT {"clock": {"tool": "chronyc", "offset_s": 2.3022e-05, "ok": true}, "pm_lag_s_p10_p50_p90": [null, null, null], "n_pm_msgs": 0, "per_sport": {"esports": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": false, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.001, 1.009, 3.224], "goalserve_payload_change_gap_s_p50": 1.014, "n_live_games": 0, "n_matched_games": 0, "matched": [], "unmatched_live": [], "market_names_seen": {}}, "tennis": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": true, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.0, 1.01, 3.229], "goalserve_payload_change_gap_s_p50": 1.035, "n_live_games": 25, "n_matched_games": 0, "matched": [], "unmatched_live": ["Bella Lewis vs Zoe Olmos", "Tristan Schoolkate vs Alafia Ayeni", "Olivia Gadecki vs Hayu Kinoshita", "Yuto Oki vs Tomohiro Masabayashi", "Lucca Liu vs Alberto Odiseo Alvarado Berrospi", "Azuma Visaya vs Darrshan Suresh", "David Eichenseher vs Gunawan Trismuwantara", "Mattias Southcombe vs Max K Fardanesh", "Kenzhibayeva/Yoruk vs Boehner/Sevcikova", "Luis Carlos Alvarez Valdes vs Elijah Strode", "Matthew Segura vs Freddy Murray", "Geun Jun Kim vs Shaheed Alam", "Valentina Ivanov vs Emerson Jones", "Zaharije-Zak Talic vs Calvin Mueller", "Veronika Miroshnichenko vs Patrycja Niewiadomska"], "market_names_seen": {"To Win": 1155, "Odd/Even": 1059, "Next Break Serve": 960, "Go The Distance?": 743, "Set 2 Winner": 675, "Set Betting": 624, "Player 1 Over/Under by Games": 579, "Match Handicap": 579, "Player 2 Over/Under by Games": 579, "Total Games in Match": 579, "Match Result and Total Games": 575, "Game to Deuce (1st Set)": 528}}, "hockey_nhl": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": true, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.001, 1.011, 3.223], "goalserve_payload_change_gap_s_p50": 2.002, "n_live_games": 4, "n_matched_games": 0, "matched": [], "unmatched_live": ["HND Silver Knights vs SJ Barracuda", "UTA Mammoth vs COL Avalanche", "ONT Reign vs ABB Canucks", "SD Gulls vs BAK Condors"], "market_names_seen": {"Both teams to score at least 2 goal": 360, "Over/Under (Including OT)": 180, "1x2 (1st Period)": 180, "Asian Handicap": 180, "Race to": 180, "Home Team Total Goals": 180, "Away Winning Margin (14-Way)": 180, "Home Winning Margin (14-Way)": 180, "Odd/Even (Including OT)": 180, "Draw No Bet": 180, "Highest Scoring Period": 180, "Team To Win The Most Periods": 180}}}}
NO NUMBER for esports: failed checks ['goalserve_polling_ok', 'goalserve_has_live_games_now', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
NO NUMBER for tennis: failed checks ['goalserve_polling_ok', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
NO NUMBER for hockey_nhl: failed checks ['goalserve_polling_ok', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
```
- Job 4 daily esports look 1 rerun: script self-test printed `ALL PASS`, but run exited 1 at 03:34:05Z. It found zero Goalserve hour files for 18 Nov, then failed because `result-esports-look1.json` was not produced; no result/verdict is claimed.
- Job 5 open-contract recorder: test printed `RECORDER TESTS PASS`; launched 03:30:27Z, PID 2701410. At 03:34Z the gzip contained 104 rows covering SPX and SPY, each Up and Down; latest two output rows were SPY Up/Down. Recorder remains running.
- Evidence paths are on the data volume: `pkarbs/probe/goalserve-live-probe-2026-11-19.log`, `pkarbs/scratch/goalserve-daily-esports/`, and `pkarbs/ocbooks/ocbooks_20261119.jsonl.gz`.


## PK priority jobs 1 and 4-5 follow-up (19 Nov, 03:37Z)

- Goalserve probe remains active (PID 2689593; launched 03:29:12Z). At the latest captured check, no sport passed preflight; the exact lines follow.

```text
PREFLIGHT {"clock": {"tool": "chronyc", "offset_s": 2.3022e-05, "ok": true}, "pm_lag_s_p10_p50_p90": [null, null, null], "n_pm_msgs": 0, "per_sport": {"esports": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": false, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.001, 1.009, 3.224], "goalserve_payload_change_gap_s_p50": 1.014, "n_live_games": 0, "n_matched_games": 0, "matched": [], "unmatched_live": [], "market_names_seen": {}}, "tennis": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": true, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.0, 1.01, 3.229], "goalserve_payload_change_gap_s_p50": 1.035, "n_live_games": 25, "n_matched_games": 0, "matched": [], "unmatched_live": ["Bella Lewis vs Zoe Olmos", "Tristan Schoolkate vs Alafia Ayeni", "Olivia Gadecki vs Hayu Kinoshita", "Yuto Oki vs Tomohiro Masabayashi", "Lucca Liu vs Alberto Odiseo Alvarado Berrospi", "Azuma Visaya vs Darrshan Suresh", "David Eichenseher vs Gunawan Trismuwantara", "Mattias Southcombe vs Max K Fardanesh", "Kenzhibayeva/Yoruk vs Boehner/Sevcikova", "Luis Carlos Alvarez Valdes vs Elijah Strode", "Matthew Segura vs Freddy Murray", "Geun Jun Kim vs Shaheed Alam", "Valentina Ivanov vs Emerson Jones", "Zaharije-Zak Talic vs Calvin Mueller", "Veronika Miroshnichenko vs Patrycja Niewiadomska"], "market_names_seen": {"To Win": 1155, "Odd/Even": 1059, "Next Break Serve": 960, "Go The Distance?": 743, "Set 2 Winner": 675, "Set Betting": 624, "Player 1 Over/Under by Games": 579, "Match Handicap": 579, "Player 2 Over/Under by Games": 579, "Total Games in Match": 579, "Match Result and Total Games": 575, "Game to Deuce (1st Set)": 528}}, "hockey_nhl": {"report": false, "checks": {"clock_synchronised_under_50ms": true, "goalserve_polling_ok": false, "goalserve_has_live_games_now": true, "a_live_game_matched_to_a_polymarket_market_naming_both_teams": false, "every_matched_token_has_a_book_message": false, "pm_server_timestamp_lag_plausible": false}, "goalserve_poll_gap_s_p10_p50_p90": [1.001, 1.011, 3.223], "goalserve_payload_change_gap_s_p50": 2.002, "n_live_games": 4, "n_matched_games": 0, "matched": [], "unmatched_live": ["HND Silver Knights vs SJ Barracuda", "UTA Mammoth vs COL Avalanche", "ONT Reign vs ABB Canucks", "SD Gulls vs BAK Condors"], "market_names_seen": {"Both teams to score at least 2 goal": 360, "Over/Under (Including OT)": 180, "1x2 (1st Period)": 180, "Asian Handicap": 180, "Race to": 180, "Home Team Total Goals": 180, "Away Winning Margin (14-Way)": 180, "Home Winning Margin (14-Way)": 180, "Odd/Even (Including OT)": 180, "Draw No Bet": 180, "Highest Scoring Period": 180, "Team To Win The Most Periods": 180}}}}
NO NUMBER for esports: failed checks ['goalserve_polling_ok', 'goalserve_has_live_games_now', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
NO NUMBER for tennis: failed checks ['goalserve_polling_ok', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
NO NUMBER for hockey_nhl: failed checks ['goalserve_polling_ok', 'a_live_game_matched_to_a_polymarket_market_naming_both_teams', 'every_matched_token_has_a_book_message', 'pm_server_timestamp_lag_plausible']
```


## P49 Goalserve live probe v2 relaunch (19 Nov)

- Stopped the prior 90-minute probe PID 2689593 (cmdline matched the exact probe and output path named by the reviewer).
- Refetched reviewer branch; offline test printed `ALL PASS` (22 checks). Relaunched v2 at 04:15:59Z, PID 2766271, duration 120 minutes, output `/mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v2-2026-11-19.json`; live log `/mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v2-2026-11-19.log`.
- First observed preflight (04:18Z): hockey_nhl passed all checks, 4/4 games matched and books present; accepted market `Home/Away`. Tennis had 15/20 matches but failed polling health: 35 HTTP 429 errors across 51 polls. Esports had no live games or accepted markets at that instant and 38 HTTP 429 errors across 48 polls. `NO NUMBER` was emitted for esports and tennis. Probe remained alive at 04:30Z; 120-minute run not complete.

## P50 esports look 1 diagnostic rerun (19 Nov)

- Re-fetched `feeds/run_daily_look.sh` from `origin/claude/project-thread-vg2ckg`; signed self-test printed `ALL PASS`. Exact full run exit: 1 at 04:26:57Z.
- It found zero local esports payload files for 2026-11-18; the named esports payload directory contained no matching files. The listing of matching files was empty. Other payload directories (basketball, esports, hockey_nhl, tennis) existed, timestamped around 04:00Z.
- The script copied zero rows into the run input (`gs` remained 4.0K) and the analyzer exited 1; no result JSON/hash or verdict was produced. Its stdout then showed a `FileNotFoundError` while the wrapper tried to read the absent result JSON. The separate 03:34Z attempt had stopped at the signed-file gate; this 04:26Z run passed the signed checks, so the current blocker is missing esports capture files for the requested day.


## P51 capture health and esports files (19 Nov)

```text
probe_stopped
goalserve_20261117.jsonl ok 449078 err 6106
2026-11-19T03:59:57Z 158277 esports_2026111903.jsonl.gz
2026-11-19T04:59:58Z 100237 esports_2026111904.jsonl.gz
2026-11-19T05:05:28Z 10563 esports_2026111905.jsonl.gz
3
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111705.jsonl.gz
Filesystem      Size  Used Avail Use% Mount
VOL2             98G   78G   16G  84% <VOL2>
REPO             49G   38G  9.3G  81% <REPO>
```

- Correction to the pasted command's glob: only `goalserve_20261117.jsonl` exists; no 18 or 19 files matched, so the requested last-two-log comparison was unavailable. The sole file had 449,078 ok and 6,106 err rows; recent err rows included HTTP 429 in minute buckets 04:56–05:05 UTC. This file is dated 17 Nov, so it cannot establish whether the probe increased errors during 19 Nov.
- `esports_payloads` contained 3 files, all dated 19 Nov; the bounded volume search found only an audit file for 17 Nov and no 18 Nov payload. Capture PID 4045212 remained running (started 17 Nov 09:00:06Z).
- Probe PID 2766271 was stopped as directed; no other process was stopped.
## Goalserve live probe v3 (19 Nov)

- Offline test: `ALL PASS` (28 checks).
- Started: 2026-11-19 05:39:25Z; PID 2867115; mode `--source capture`; duration 180 minutes. The probe reads stored payloads and makes no Goalserve requests.
- First preflight observed at 05:39:48Z. Clock offset: 0.000200 s; Polymarket message lag p10/p50/p90: 0.018/0.018/0.023 s; messages: 27198.
- esports: report=false; poll gap p10/p50/p90=1.783/1.799/1.821 s; payload-change p50=1.799 s; polls=35, poll errors=0; live games=0, matched=0; accepted markets={}; matched tokens have books=false.
  - Failed checks: goalserve_has_live_games_now, goalserve_has_an_accepted_winner_market, a_live_game_matched_to_a_polymarket_market_naming_both_teams, every_matched_token_has_a_book_message.
- tennis: report=true; poll gap p10/p50/p90=1.778/1.799/1.82 s; payload-change p50=1.799 s; polls=49, poll errors=0; live games=14, matched=9; accepted markets={"To Win": 686}; matched tokens have books=true.
- hockey_nhl: report=true; poll gap p10/p50/p90=1.78/1.797/1.816 s; payload-change p50=1.797 s; polls=49, poll errors=0; live games=2, matched=2; accepted markets={"Home/Away": 85}; matched tokens have books=true.
- basketball: report=false; poll gap p10/p50/p90=1.781/1.796/1.814 s; payload-change p50=1.796 s; polls=49, poll errors=0; live games=8, matched=1; accepted markets={}; matched tokens have books=true.
  - Failed checks: goalserve_has_an_accepted_winner_market.

- First preflight result: tennis and hockey_nhl passed all checks; esports had no live games and failed its market/match/book gates; basketball had no accepted winner market. Probe remains running; final output is not yet available.
## AAA watch (19 Nov)

- Source commit: `71bd42c3`.
- SHA-1: `aaa_watch.py` `94cab973c2055a7b3a03422f1c79613313b517d1`; `test_aaa_watch.py` `585ed9b380962e88acbefcf61a556b9e7189c6a0`.
- Tests: `3 of 3 tests pass`.
- Scheduled watcher process launched at 05:45Z, PID 2879168; start is delayed until 07:28Z and ends at 09:00Z (max 5400 seconds; 5-second interval). It writes under `/mnt/HC_Volume_107257520/gas_watch`, not root.
- At 05:45Z the delayed process was alive; output files do not yet exist because the watcher has not started. HTTP status codes and the first three JSONL lines are therefore not yet available.

## P53 errors by hour and esports files (19 Nov)

Read-only checks at 06:16–06:21Z; no Goalserve request, move, or deletion was run.

```text
2026-11-17T09 rows 11412 {('tennis', "<HTTPError 429: 'Too Many Requ"): 1, ('soccer', "<HTTPError 429: 'Too Many Requ"): 1}
2026-11-17T14 rows 10506 {('soccer', "URLError(gaierror(-3, 'Tempora"): 1}
2026-11-19T03 rows 10716 {('tennis', "<HTTPError 429: 'Too Many Requ"): 677, ('hockey_nhl', "<HTTPError 429: 'Too Many Requ"): 672, ('esports', "<HTTPError 429: 'Too Many Requ"): 690}
2026-11-19T04 rows 11202 {('tennis', "<HTTPError 429: 'Too Many Requ"): 1248, ('hockey_nhl', "<HTTPError 429: 'Too Many Requ"): 1245, ('esports', "<HTTPError 429: 'Too Many Requ"): 1215}
2026-11-19T05 rows 11730 {('tennis', "<HTTPError 429: 'Too Many Requ"): 126, ('hockey_nhl', "<HTTPError 429: 'Too Many Requ"): 116, ('esports', "<HTTPError 429: 'Too Many Requ"): 114}
== esports_payloads: 3 files; first esports_2026111904.jsonl.gz; last esports_2026111906.jsonl.gz; size 488K
== tennis_payloads: 3 files; first tennis_2026111904.jsonl.gz; last tennis_2026111906.jsonl.gz; size 86M
== hockey_nhl_payloads: 3 files; first hockey_nhl_2026111904.jsonl.gz; last hockey_nhl_2026111906.jsonl.gz; size 21M
== basketball_payloads: 3 files; first basketball_2026111904.jsonl.gz; last basketball_2026111906.jsonl.gz; size 163M
esports_payloads birth=2026-11-13 17:38:56Z mtime=2026-11-19 06:20:56Z ctime=2026-11-19 06:20:56Z
tennis_payloads birth=2026-11-17 09:00:08Z mtime=2026-11-19 06:00:01Z ctime=2026-11-19 06:00:01Z
```

Bounded file search output sample (paths redacted):
```text
<VOL2>/pkarbs-ps-step2/agent/outbox/2026-11-13-goalserve-esports-store-payloads-APPROVED.md
<VOL2>/pkarbs-ps-step2/agent/inbox/2026-11-13-goalserve-esports-store-payloads-APPROVED.md
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111412.jsonl.gz
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111612.jsonl.gz
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111705.jsonl.gz
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111512.jsonl.gz
<VOL2>/pkarbs/goalserve-audit-20261117/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/goalserve/esports_payloads
<VOL2>/pkarbs/scratch/goalserve-odds-vs-pm-20261117/gs/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/scratch/p14-recount/goalserve/esports_payloads/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/scratch/p318/goalserve/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/scratch/p318-recount/goalserve/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/scratch/t321/gs/esports_2026111315.jsonl.gz
<VOL2>/pkarbs/scratch/goalserve-odds-vs-pm-20261117/gs/esports_2026111316.jsonl.gz
<VOL2>/pkarbs/scratch/p14-recount/goalserve/esports_payloads/esports_2026111316.jsonl.gz
<VOL2>/pkarbs/scratch/p318/goalserve/esports_2026111316.jsonl.gz
<VOL2>/pkarbs/scratch/p318-recount/goalserve/esports_2026111316.jsonl.gz
<VOL2>/pkarbs/scratch/t321/gs/esports_2026111316.jsonl.gz
<VOL2>/pkarbs/scratch/goalserve-odds-vs-pm-20261117/gs/esports_2026111317.jsonl.gz
```

- The requested exact-date search returned no `esports_20261118*.jsonl.gz` under either `/mnt/HC_Volume_107257520/pkarbs` or `/mnt/HC_Volume_107247271/pkarbs-recount-input`; the wider bounded search likewise found no Nov 18 file. The audit store has five old hourly files (13–17 Nov); scratch copies include 13–17 Nov. No source file for 18 Nov was found.
- The current canonical esports directory has only hours 04, 05, and 06 on 19 Nov. This differs from P51's 05:05Z listing, which included hour 03. Therefore the previously listed hour-03 file is now also absent; its destination/cause is not established. Directory birth time is 13 Nov 17:38:56Z.
- Live process check: PID 4045212 remains `python3 live/goalserve/capture.py`, started 17 Nov 09:00:06Z. The checked capture implementation appends changed bodies to one UTC-hour gzip and contains no retention/unlink/move operation.
- For 02:00–03:30Z, the fetched project-branch history contains no commit changing the Goalserve data directory; the searched shell/log files contain zero `esports_payloads` matches. No IT/agent move, archive, or deletion action was found in those records. This cannot rule out an unlogged manual filesystem action; the actor/cause is unverified.
- The prior P51 429 error window is confirmed and now quantified: 03Z had 677/672/690 errors for tennis/hockey/esports; 04Z 1248/1245/1215; 05Z 126/116/114. These are error counts from the single poll log, not proven causal attribution to the probe.

## P57 Goalserve hold and copy-back (19 Nov)

- `crontab -l` matched: `*/30 * * * * ... ship_raw.sh ...` (every 30 minutes; no Goalserve-specific crontab entry). `writers.conf` routes Goalserve to `pkarbs/goalserve`, with delete enabled and hourly mode. `ship_raw.sh` recursively enumerates regular files from the configured directory; its rsync writes to the matching box subdirectory and deletes local files only after checksum verification and its retention/Git condition.
- Backed up the script to `/root/ship/ship_raw.sh.bak-20261119`. Syntax check: `bash -n` passed. Diff: the single recursive `find` now excludes `./esports_payloads` and descendants, `./tennis_payloads` and descendants, `./hockey_nhl_payloads` and descendants, and `./basketball_payloads` and descendants before age filtering; no other script lines changed.
- A dry run for the Goalserve writer exited 0 and reported `goalserve nothing eligible`; it listed zero payload paths. This confirms the four payload directories are excluded. No files were deleted.
- Box path: `<box>:pkarbs/goalserve/`. Box inventory totals for the copy-back window: esports 129 files / 806,729,570 bytes; tennis 39 / 3,273,505,743 bytes; hockey_nhl 39 / 1,514,435,504 bytes; basketball 39 / 3,702,715,735 bytes. Available space before copy: 16,070,557,696 bytes. The 15 GB free-space gate therefore allowed only the specified esports 18 Nov subset.
- Copied esports 18 Nov only, 24 files / 143,272,111 bytes, with `rsync --ignore-existing`; first/last listings confirmed hours 00–23. After copy, 15,557,345,280 bytes remained free. Tennis, hockey_nhl and basketball were not copied because the 15 GB floor would be breached; their sizes are listed above.


## Probe v3 timed read and 07:30Z check (19 Nov; P55/P52b)

- At 08:06Z, the specified `.log` path did not exist. The live PID 2867115 was still running with `--out /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v3-2026-11-19.json`; its stdout/stderr are directed to `/tmp/hermes_bg_proc_c57eb8334d03.log`. The requested log filter and final-20-lines fallback therefore had no target; no substitute was treated as the requested log.
- The requested 07:30Z `^[0-9:]+Z events` check against the same absent `.log` path returned no lines (file-not-found).

## F look 1 rerun 2 (19 Nov)

- Re-ran the signed `feeds/run_daily_look.sh esports` once from fetched project tip `12f71169130c9219827e8c74669598fedd5bdadf` at 08:40:42Z. Signed self-test: `ALL PASS`; all 24 esports payload files for 18 Nov were present. Wrapper completed successfully.
- Result: `run exit 0`; `smoke_not_a_result=false`; `look=1`; `plant_c=0.01`; 24 input files; 3,052 Goalserve events; data through 18 Nov UTC. Primary CS2 Match Winner cell: 6 matches / 215 events, verdict `unknown` (minimum is 12 matches and 60 events); z_eq 1.86 vs boundary 10.61; planted edge not recovered/underpowered. This is a look result, not a positive pass. Result SHA-256: `cd46ef0e91bdfc1dccb32f012e3a6c9a8976fa43719a3452404833ec5b8f4c65`.
- VOL2 free at run start: 15,239,073,792 bytes; subsequent read at 08:47:48Z: 14,328,098,816 bytes (below the script's 15 GB run gate). Current read at report preparation: 14044434432 bytes. No further rerun or deletion was made. The reviewer-requested 12:00Z and 18:00Z readings are not yet due.

### Full run output

```text
date 2026-11-19T08:40:42Z avail_bytes 15239073792
commit 12f71169130c9219827e8c74669598fedd5bdadf
cbd0f397f09eb92acdd2b6735c093e6a7bed97fcfa4a45dbe32a33f6cb3d1af0  feeds/goalserve_odds_vs_pm_v2.py
9d4bdad46183f44d160b1e14bc6cae9bffbbac1aa3bc43625d20087d9fcdc6d8  feeds/test_goalserve_odds_vs_pm_v2.py
4b67d26f6f9f419cd330fdca7ee3c396ed99d5db9ddc56c5370012120c296cb1  feeds/ps_lead_test.py
a556636fbd0e57a2fa622c9c9eda20a564baab1acf01cffd1e3a9b955c1300c5  feeds/goalserve_odds_vs_pm.py
PASS completeness: hours without polls (capture outage, 4 matches' quiet hours) are listed in audit.hour_files and do not stop a complete day
ALL PASS
sport esports look_expected 1 days 20261118
hour files 20261118: 24
poll logs: /mnt/HC_Volume_107257520/pkarbs/goalserve/goalserve_20261117.jsonl 
PM last book row time 2026-11-19T08:43:54Z (epoch 1795077834)
137M	/mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-daily-esports/gs
run exit 0 at 2026-11-19T08:49:14Z
cd46ef0e91bdfc1dccb32f012e3a6c9a8976fa43719a3452404833ec5b8f4c65  /mnt/HC_Volume_107257520/pkarbs/scratch/goalserve-daily-esports/result-esports-look1.json
sport "esports"
smoke_not_a_result false
look 1
n_max {"cs2|Match Winner": 100, "dota2|Match Winner": 50}
c_bm 2.6
data_through_utc 1795046400.0
plant_c 0.01
seed 20261118
files 24
goalserve_events_total 3052
drops {"events_no_pm_market": 1284, "events_ambiguous_rematch_excluded": 287, "pm_book_rows_time_from_ms": 65108, "book_rows_one_sided": 6730, "events_dropped_by_match_cap": 768, "events_tie_d_zero": 13}
audit.counters {"rows": 40378, "baseline_cleared_poll_gap_gt_10s": 35, "payloads_after_poll_gap_gt_10s": 8, "events": 3052, "skip_suspended": 21918, "baseline_cleared_not_valid_open": 997, "skip_not_2_participants": 32050, "skip_bad_odds": 362}
audit.hour_files {"expected": 24, "present": 24, "missing_hours_utc": [], "missing_hours_without_polls_are_capture_outages": true}
audit.league_prefixes_seen {"cs2": 45647, "dota2": 13828, "unparsed": 11261}
audit.bm_values {"''": 40378}
cs2|Map 1 Winner [informational]: look 1 of 20 (data through 2026-11-18 UTC), 6 matches used, info time n/a, z_eq 2.50 vs boundary n/a, planted 1c edge: NOT recovered or underpowered ({"plus_step": 0.010000000000000009, "minus_step": -0.010000000000000009, "label_swap_plus_step": -0.010000000000000009, "plus_ok": true, "minus_ok": true, "swap_ok": true}), verdict: (informational) (informational) no boundary
cs2|Map 2 Winner [informational]: look 1 of 20 (data through 2026-11-18 UTC), 6 matches used, info time n/a, z_eq 3.30 vs boundary n/a, planted 1c edge: NOT recovered or underpowered ({"plus_step": 0.010000000000000007, "minus_step": -0.010000000000000009, "label_swap_plus_step": -0.010000000000000009, "plus_ok": true, "minus_ok": true, "swap_ok": true}), verdict: (informational) (informational) no boundary
cs2|Match Winner [primary]: look 1 of 20 (data through 2026-11-18 UTC), 6 matches used, info time 0.06, z_eq 1.86 vs boundary 10.61, planted 1c edge: NOT recovered or underpowered ({"plus_step": 0.010000000000000007, "minus_step": -0.010000000000000007, "label_swap_plus_step": -0.010000000000000009, "plus_ok": true, "minus_ok": true, "swap_ok": true}), verdict: unknown (6 matches, 215 events; needs >= 12 and >= 60)
unparsed|Map 3 Winner [informational]: look 1 of 20 (data through 2026-11-18 UTC), 1 matches used, info time n/a, z_eq n/a vs boundary n/a, planted 1c edge: NOT recovered or underpowered ({"plus_step": 0.010000000000000009, "minus_step": -0.010000000000000009, "label_swap_plus_step": -0.010000000000000007, "plus_ok": true, "minus_ok": true, "swap_ok": true}), verdict: (informational) (informational) no boundary
unparsed|Map 4 Winner [informational]: look 1 of 20 (data through 2026-11-18 UTC), 1 matches used, info time n/a, z_eq n/a vs boundary n/a, planted 1c edge: NOT recovered or underpowered ({"plus_step": 0.010000000000000009, "minus_step": -0.01000000000000001, "label_swap_plus_step": -0.010000000000000004, "plus_ok": true, "minus_ok": true, "swap_ok": true}), verdict: (informational) (informational) no boundary
CELL cs2|Match Winner {"role": "primary", "n_matches_used": 6, "information_time": 0.06, "boundary_z": 10.61445555206044, "z_eq": 1.8581954381002106, "mean_d_per_match": 0.008148055555555556, "plants_ok": false, "plant_recovery": {"plus_step": 0.010000000000000007, "minus_step": -0.010000000000000007, "label_swap_plus_step": -0.010000000000000009, "plus_ok": true, "minus_ok": true, "swap_ok": true}, "post_real": 0.011116666666666664, "pre_real": 0.00362083333333333, "post_placebo": -2.1388888888887893e-05, "pre_placebo": 0.0006308333333333335, "excluded_counts": {"events_dropped_by_match_cap": 414}, "matches_by_day": {"1": 6}, "matches_cumulative_by_day": {"1": 6}, "verdict": "unknown (6 matches, 215 events; needs >= 12 and >= 60)"}
first20_events_biggest_cell {"cell": "cs2|Map 1 Winner", "rows": [{"t": 1794992970.6581893, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": 0.15000000000000002, "placebo_mean": 0.06, "d": 0.09000000000000002}, {"t": 1794993592.7123625, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": 0.02000000000000013, "placebo_mean": 4.4408920985006264e-17, "d": 0.020000000000000084}, {"t": 1794993594.5919833, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.020000000000000018, "placebo_mean": 0.0040000000000000036, "d": -0.02400000000000002}, {"t": 1794993600.2369766, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.044999999999999984, "placebo_mean": 0.027000000000000073, "d": -0.07200000000000006}, {"t": 1794993668.067265, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.05000000000000002, "placebo_mean": 0.0, "d": -0.05000000000000002}, {"t": 1794993681.035662, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.08499999999999996, "placebo_mean": 0.016999999999999994, "d": -0.10199999999999995}, {"t": 1794993686.5593262, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": 0.05999999999999994, "placebo_mean": 0.011999999999999986, "d": 0.04799999999999996}, {"t": 1794993688.373261, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": 0.020000000000000018, "placebo_mean": -0.008000000000000002, "d": 0.028000000000000018}, {"t": 1794993699.4251018, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.030000000000000027, "placebo_mean": 0.006000000000000003, "d": -0.03600000000000003}, {"t": 1794993701.2524073, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.050000000000000044, "placebo_mean": 0.030000000000000016, "d": -0.08000000000000006}, {"t": 1794993919.5840013, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.06999999999999995, "placebo_mean": -0.01399999999999999, "d": -0.05599999999999996}, {"t": 1794993927.1563828, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": 0.06999999999999998, "placebo_mean": 5.551115123125783e-18, "d": 0.06999999999999998}, {"t": 1794994004.336813, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.035, "placebo_mean": -0.02100000000000001, "d": -0.013999999999999992}, {"t": 1794994041.870537, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": 0.04000000000000001, "placebo_mean": -1.6653345369377347e-17, "d": 0.04000000000000002}, {"t": 1794994043.7434223, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.039999999999999925, "placebo_mean": -0.007999999999999969, "d": -0.03199999999999996}, {"t": 1794994060.654278, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.04999999999999993, "placebo_mean": -0.009999999999999992, "d": -0.03999999999999994}, {"t": 1794994073.8778617, "match": "141356393", "rising_team": "gothboiclique", "token": "111951407336798735087095400039187127526620973240453880336229003194698922939388", "R_real": -0.02999999999999997, "placebo_mean": -5.551115123125783e-18, "d": -0.029999999999999964}, {"t": 1794994090.8344793, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": 0.06999999999999995, "placebo_mean": 0.013999999999999995, "d": 0.05599999999999995}, {"t": 1794994170.2164254, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.07999999999999985, "placebo_mean": 0.03199999999999996, "d": -0.11199999999999981}, {"t": 1794994172.0994754, "match": "141356393", "rising_team": "eyeballers", "token": "114052691946527873086650706008836495632176832947176031533592789623086951337672", "R_real": -0.17499999999999993, "placebo_mean": 0.03499999999999999, "d": -0.2099999999999999}]}
```

## P60 disk (19 Nov)

Read-only snapshot, 2026-11-19 09:23:35Z; no deletion or restart performed.

- VOL2 available: 20,354,613,248 bytes (20.35 GB); filesystem 80% used. An earlier 09:22:59Z read showed 20,545,753,088 bytes available.
- Largest `/vol2/pkarbs` directories: thesports 45G; scratch 7.6G; from-vol 6.4G; tennis 1.9G; thesports-cricket 1.5G; charts 762M; goalserve 453M; dotacap 432M; pmcs2 130M; lol 88M; goalserve-audit 46M; oddspapi 18M.
- Under Goalserve/scratch, largest entries: `scratch/goalserve-odds-vs-pm-20261117` 551M; `scratch/goalserve-daily-esports` 137M in the detailed read (the later 09:23:35Z `du` read measured its `gs` subtree at 143,272,111 bytes); `scratch/p318-recount` 141M; `scratch/ts_manual_1794409049` 123M; `scratch/P27-20261118` 119M.
- Fastest-growing paths in the last-hour mtime scan: `pkarbs/thesports/final-topics-32295b` 41,803,737,130 bytes (including `share` 6,038,597,356 bytes); `ship/manifest` 178,993,862 bytes; `pkarbs/scratch/goalserve-daily-esports/gs` 143,272,111 bytes; `nt_live_fire/segments/49742074` 1,178,269,752 bytes. The first large path is not under the Goalserve capture; no deletion was made.
- Goalserve capture PID 4045212 remained running (`python3 live/goalserve/capture.py`, elapsed 2d 00:23:49 at 09:23:35Z); tmux session `goalserve` exists. No `*_payloads_STOP.log` lines were present in the requested tail.
- Hour files were actively growing at 09:23Z: esports 2026111909 1,816,741 bytes; tennis 2026111909 28,550,043; hockey_nhl 2026111909 57,263; basketball 2026111909 7,223,030. Previous 08-hour files were present (esports 101,783; tennis 35,786,410; hockey_nhl 103,292; basketball 14,503,086 bytes), and their mtimes were 08:42Z.
- `pmcs2/books.jsonl` measured 136,185,464 bytes. PID 2690054 was absent from the requested `ps` output; P62 handles its prescribed check/restart gate. The requested `ship_raw.sh` grep showed the 10-day/day-before-today filter and excludes all four payload directories from that generic sweep.
- Disk grew from the 13.0 GB free reported at 09:00Z in the queue to >20.3 GB free at this check; no action here explains that increase. The current read is above the P60/P61 17 GB gate.
