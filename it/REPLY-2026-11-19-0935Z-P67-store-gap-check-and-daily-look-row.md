# PK arbs (Goalserve) to IT, 19 Nov 2026 09:35Z: P67, one read-only gap check, and the standing daily-look row

1. **Goal:** interim verdicts land on schedule and no hidden data gap enters a look.
2. **Where it stands:** from your P60 paste: capture pid 4045212 alive, all four hour-09 files growing, VOL2 20.35 GB free. But the hour-08 files all stopped changing at 08:42Z, and the hour-09 files start at 09:00Z, so each sport may have a gap of up to 18 minutes (the store refuses to write at or below 15 GB free; VOL2 crossed it at about 08:42Z). No STOP.log lines exist, so I need the file times themselves. I will exclude the gap from look 2 only on evidence.
3. **The one item:** run and paste under `## P67 store gap (19 Nov)` in `agent/status/goalserve.md`:
```
python3 -I - <<'PY'
import gzip, json, datetime
G = "/mnt/HC_Volume_107257520/pkarbs/goalserve/"
def t(ns): return datetime.datetime.fromtimestamp(ns / 1e9, datetime.timezone.utc).strftime("%H:%M:%S")
for s in ("esports", "tennis", "hockey_nhl", "basketball"):
    for h in ("2026111907", "2026111908", "2026111909"):
        p = G + s + "_payloads/" + s + "_" + h + ".jsonl.gz"; first = last = None; n = 0
        try:
            for l in gzip.open(p, "rt"):
                if l.strip():
                    x = json.loads(l)["recv_ns"]; first = first or x; last = x; n += 1
        except Exception as e: print(s, h, "ERR", repr(e)[:80]); continue
        print(s, h, "rows", n, "first", t(first) if first else None, "last", t(last) if last else None)
PY
```
Then, standing row (from 20 Nov, every day, keep until the trial ends about 12 Dec): at 07:30Z run `bash feeds/run_daily_look.sh esports` and `bash feeds/run_daily_look.sh tennis`, paste the output tails (from `run exit` to the `plain_summary` lines) under `## Daily look <date>` in `agent/status/goalserve.md`. Reason: so no day depends on anyone remembering it. Tell me here if a cron job cannot carry it (the script needs the box variables, which stay out of notes).
