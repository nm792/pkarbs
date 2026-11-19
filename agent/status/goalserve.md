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
