# CHUNK H: is the Goalserve capture still running and storing tennis, hockey and basketball? Read-only. Posted 18 Nov 2026 08:30Z. URGENT: the first look is 19 Nov ~01:00Z.

**1. Goal.** Use the free Goalserve trial fully: esports now, tennis next, in parallel.
**2. Position.** The store-all capture (P15b) was installed on 17 Nov 09:00:02Z (026be71fe8) and writes `<sport>_payloads/` hour files. Your 04:35Z inventory listed `ls -1t` of the Goalserve folder with `goalserve_20261117.jsonl` newest, which is unexpected at 04:35Z on 18 Nov: either the 18 Nov poll log is missing or the listing was mtime-ordered oddly. I need to know now, because the first look reads the poll log and the hour files for 18 Nov.
**3. One item.** Run, read-only, on the data volume and Prime as applicable, and paste the output under `## H capture check (18 Nov)` in agent/status/goalserve.md. Do not print any key, URL or credential.
```
G=/mnt/HC_Volume_107257520/pkarbs/goalserve
date -u +%FT%TZ
ls -l --time-style=+%FT%TZ $G | head -30
for s in esports tennis hockey_nhl basketball; do echo "== $s"; ls -l --time-style=+%FT%TZ $G/${s}_payloads | tail -4; ls $G/${s}_payloads | grep -c 20261118; done
tail -c 400 $G/goalserve_20261118.jsonl 2>&1 | cut -c1-300 | tail -2
tmux ls 2>&1 | head -5; pgrep -af capture | sed 's/--[a-z-]*[= ][^ ]*//g' | head -5
df -B1 --output=avail $G | tail -1
ls $G/*STOP.log 2>&1 | head
# one tennis hour file, structure only (keys, no values):
f=$(ls -t $G/tennis_payloads/*.jsonl.gz | head -1); zcat $f | head -1 | python3 -I -c "import sys,json; r=json.loads(sys.stdin.readline()); print(sorted(r.keys())[:20]); b=r.get('body') or r.get('payload'); print(type(b).__name__, (sorted(b.keys())[:20] if isinstance(b,dict) else str(b)[:200]))"
```
If a `*_STOP.log` exists, paste its last 5 lines. If the capture is not running, say since when, and restart it only through a separate approved row.
**Done check:** the output pasted with the date line; each sport shows hour files for 20261118 (count 0 means not storing that sport).
