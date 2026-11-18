# CHUNK N1: which process writes the Polymarket books, and for which sports. Read-only. Posted 18 Nov 2026 18:40Z.

**1. Goal.** Test Goalserve hockey (and later basketball and soccer) odds against the Polymarket price. The recorder holds books only for cricket, cs2, dota2, lol, nba, nfl, tennis (G inventory, 8a9310c96b); hockey needs its books recorded, else there is no benchmark.
**2. Position.** `live/thesports/capture.py` records 1 s books for the sports in its `--sports` list (tags in its `TAGS`); NHL is not among them. I will send a patch row next; first I need the facts, so I do not guess the command line.
**3. The one item.** Read-only, post under `## N1 recorder (18 Nov)` in agent/status/goalserve.md:
```
ps -eo pid,lstart,args | grep -E "thesports/capture|capture.py" | grep -v grep | sed -E 's/(THESPORTS|SECRET|KEY|USER)[A-Za-z_]*=[^ ]*/\1=[R]/g'
for p in $(pgrep -f "thesports/capture"); do echo "pid $p cwd $(readlink /proc/$p/cwd)"; done
ls -ld --time-style=+%FT%TZ /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b; ls -l --time-style=+%FT%TZ /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b | head -8
tmux ls 2>&1 | head
```
Print no key or credential. **Done check:** the process list line(s) with start time and the `--sports` argument, and the output directory of that process.
