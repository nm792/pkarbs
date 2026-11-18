

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
