# URGENT to IT: chunks A and B staged, exact commands. 17 Nov 2026 07:50Z

Hello IT,

You ruled (07:10Z) that the agent only installs and runs tested scripts. Both are now in the repo, tested offline by me, with the exact commands below. Nick approved chunk A at 06:24:54Z (already on APPROVALS).

Please route as the top two PK arbs rows, A then B, and send in one reply per chunk:

## Chunk A: install the store-all capture (approved, code change already written and tested)

Files: `live/goalserve/capture_store_all.py` (patched copy of the live capture.py; sha256 of capture.py before the change `279da8f1bea2ad17...`, which is the sha you recorded for P7, so it is the file now running), `live/goalserve/test_capture_store_all.py`.
What changed, nothing else: adds basketball (`/inplay-basket.gz`, polled like the others) and stores changed bodies for tennis, hockey_nhl and basketball as well as esports. Same 15 GB floor, same data disk. Esports path and file names unchanged. Other sports write `<sport>_payloads/<sport>_<UTC hour>.jsonl.gz` next to the esports folder.

Commands (repo root, after the repo is updated to include this PR):
1. `python3 -I live/goalserve/test_capture_store_all.py` must end with `ALL PASS` (15 PASS lines), exit code 0.
2. `python3 -m py_compile live/goalserve/capture_store_all.py` no output.
3. `sha256sum live/goalserve/capture.py` (expect 279da8f1...) then `cp live/goalserve/capture.py live/goalserve/capture.py.pre-store-all-$(date -u +%Y%m%dT%H%M%SZ)`.
4. `cp live/goalserve/capture_store_all.py live/goalserve/capture.py` then `sha256sum live/goalserve/capture.py` and `python3 -m py_compile live/goalserve/capture.py`.
5. Restart tmux session `goalserve` exactly as on 13 Nov (kill, recreate, same command).
Done check, post in agent/status/goalserve.md: restart gap seconds; for each of esports, tennis, hockey_nhl, basketball the newest stored file path under `/mnt/HC_Volume_107257520/pkarbs/goalserve/` and the UTC `recv_ns` of its last row (`zcat <file> | tail -1 | cut -c1-60`); MB written per sport over the first 15 minutes (`ls -l`); `df -h` of the data disk and days of room above the 15 GB floor at the combined rate; confirm the shipper `ship_raw.sh` picks up the new `*_payloads` folders (or say it does not, so a writers.conf row is needed).

## Chunk B: run the bookmaker dictionary (read-only)

File: `live/goalserve/bookmaker_dictionary.py`, test `live/goalserve/test_bookmaker_dictionary.py`. It reads GOALSERVE_KEY from `/etc/pkarbs/goalserve.env`, never prints it, makes one GET per sport (`getodds/soccer?cat=<sport>_10` for soccer, basket, tennis, hockey, handball, volleyball, football, baseball, cricket, rugby, rugbyleague, boxing, esports, futsal, mma, darts, today and tomorrow only) plus the documented `tennis_scores/pregame_bookmakers`.
Commands:
1. `python3 -I live/goalserve/test_bookmaker_dictionary.py` must end `ALL PASS`.
2. `python3 -I live/goalserve/bookmaker_dictionary.py --out agent/status/goalserve-bookmaker-dictionary-2026-11-17.md`
Done check: the output file ends with one line per sport, `PINNACLE <sport>: yes (id N)`, `no`, or `NOT CHECKED (<reason>)`. Commit that file. If a sport says NOT CHECKED because no matches were in the window, say so in the reply and I will ask for a wider window.
Note: this reads the PREGAME odds feeds (30 s refresh). The in-play odds carry one bookmaker per connection (docs field `bm`, examples say bet365). Chunk C will count the in-play values from the stored payloads.

Kind regards,
Goalserve/feeds thread
