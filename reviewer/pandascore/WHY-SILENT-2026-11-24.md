# Why the PandaScore capture went silent (Reviewer, 24 Nov 2026 15:05Z)

Read from code (`it/ll_capture_floor_env.py`, the file IT runs per P118) and IT's reads (trading-test `dialogue/from_agent/pkarbs/P118-pandascore.md` 23 Nov 06:23Z, `pandascore-P105.md` 23 Nov 15:26Z). No server access; nothing here was run on Prime.

## What the evidence shows
1. **Not a crash and not the disk floor.** PID 625842 was alive at 06:23Z 23 Nov. A floor stop writes a `stopped` event and exits; a discovery failure writes `discovery_error`. Neither is in `/root/pscap2.log`, whose last line is a normal `closed` (code 1000, match finished) for match 1816470 at 22 Nov 22:05:56Z. The last raw write was 21:51:46Z, so that socket was quiet for 14 minutes and then the server ended the match.
2. **PandaScore listed no live CS2 or Dota feed at the one moment we checked.** In P118 the pre-flight's discovery call succeeded (no `2 discovery error` line, so the token worked, HTTP 200), and it printed `3 real data: not measurable without a live match`, the branch taken only when E = 0: no CS2/Dota low-latency feed with `opens_at` at or before 06:23Z. One reading only; 41 hours are unaccounted for.
3. **The code cannot tell "nothing listed" from "hung".** When discovery succeeds with no eligible match the loop writes nothing, and there is no heartbeat. A loop stuck inside the synchronous `urllib` discovery call (it runs on the asyncio loop thread) would also write nothing. Both produce the same silent log. This is the root defect.
4. **The events log is gone.** `events.jsonl.gz` was missing at 06:23Z. `ev()` recreates it on any call, so no event was written after it disappeared, which fits point 3. Who removed it is UNVERIFIED (disk-relief moves ran on 23-24 Nov).
5. **Why P105 found a "truncated" file.** The hourly gzip writer only closes an hour file when the next message arrives in a new hour. Messages stopped at 21:51:46Z, so `pandascore_2026112221.jsonl.gz` stayed open with no gzip trailer, and P105's scorer rejected it. Second code defect. (P118 saw 91,194 bytes at 06:23Z; P105 copied 94 bytes at 15:26Z. That difference is UNVERIFIED.)
6. **Lock not held** because PID 625842 was started without the `flock` wrapper in the P118 note. Not a cause of the silence.

## Most likely cause, and what settles it
Most likely: PandaScore's trial lists low-latency feeds only for some tournaments, and none was live for long stretches after 22 Nov 22:05Z. A hung discovery call is the alternative. Three read-only commands settle it. They must run BEFORE the restart in IT-OPS 7304fa4b9, because the restart destroys the evidence:
```
cat /proc/625842/wchan; echo; ls -l /proc/625842/fd | grep -c socket; ss -tnp | grep 'pid=625842' | head
cd /root/pkarbs && python3 -I -c "import sys; sys.path.insert(0,'it'); import ps_preflight as p, collections; f=p.discovery(); it=f if isinstance(f,list) else f.get('data',[]); print('items',len(it)); c=collections.Counter(((i.get('match') or {}).get('videogame') or {}).get('slug') for i in it); print(dict(c)); print(sorted(((i.get('endpoint') or {}).get('opens_at') or '') for i in it if ((i.get('match') or {}).get('videogame') or {}).get('slug') in ('cs-go','dota-2'))[:10])"
ls -la /mnt/HC_Volume_107257520/pkarbs/pandascore/ /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | tail -8
```
Reading: `wchan` in a socket read plus an ESTABLISHED connection to api.pandascore.co means hung. A zero CS2/Dota count, or `opens_at` values all in the future, means idle because nothing is listed. No token is printed by these commands.

## Fix (draft, NOT deployed: server code, Nick approves)
`reviewer/pandascore/ll_capture_v4.py` (diff against `it/ll_capture_floor_env.py` is the three changes only) with `test_ll_capture_v4_smoke.py` (no network, no token, temp dir; `SMOKE PASS` here):
1. a heartbeat event every 10 min (items listed, CS2/Dota count, eligible, active sockets, age of the last raw write), and a `discovery_summary` event whenever the CS2/Dota count changes;
2. discovery in a worker thread under a 60 s timeout (`discovery_timeout` event), so a stuck call cannot freeze the loop;
3. the hour file is closed after 300 s with no message, so a quiet hour is a complete gzip.
Expected write: the heartbeat adds about 150 bytes per 10 min, under 0.1 MB/day, on top of the capture's under 50 MB/day.

Confidence 7/10 on "most likely idle because nothing listed". It reaches 9 with the three reads above.
