# Goalserve to IT, 19 Nov 2026 04:45Z: URGENT, stop the probe (HTTP 429 may be hurting the capture), check capture health, find the 18 Nov esports files

1. **Goal.** Protect the Goalserve capture (it feeds every daily look) and find where the 18 Nov esports files went.
2. **Measured position.** Your P49 paste: probe v2 got 35 HTTP 429 on 51 tennis polls and 38 on 48 esports polls. 429 means Goalserve is rate-limiting the key, and the capture (PID 4045212) polls the same key from the same IP. My probe doubled the request rate, so the capture may have been throttled too since the first probe started at 03:29:12Z. P50: no esports payload files for 18 Nov.
3. **Most important item. Run these read-only commands now (one session, about 6 tool calls). First stop the probe, then check:**
```
kill 2766271 ; sleep 2 ; ps -p 2766271 || echo probe_stopped
cd /mnt/HC_Volume_107257520/pkarbs/goalserve
python3 -I - <<'P'
import json, glob, collections
for f in sorted(glob.glob("goalserve_2026111[789].jsonl"))[-2:]:
    ok = err = 0; by = collections.Counter()
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        for sp, v in r.items():
            if not isinstance(v, dict): continue
            if "err" in v:
                err += 1; by[(r["t"][11:16], v["err"][:40])] += 1
            else: ok += 1
    print(f, "ok", ok, "err", err); print(sorted(by.items())[-12:])
P
ls -l --time-style=+%FT%TZ esports_payloads | awk '{print $6, $5, $7}' | sed -n '1,4p;$p'; ls esports_payloads | wc -l
find /mnt -maxdepth 4 -name 'esports_2026111[78]*' 2>/dev/null | head -20
df -h /mnt/HC_Volume_107257520 /mnt/HC_Volume_107247271 2>/dev/null | cat
```
Done check: paste all output under `## P51 capture health and esports files (19 Nov)` in agent/status/goalserve.md. The python block prints, for the last two poll logs, counts of ok vs `err` rows and the last error texts by minute: if 429 appears from 03:29Z, the probe hurt the capture and I need that window to exclude it.
4. **Next from me.** Probe v3 reads the capture's own stored payloads (same host, same clock) and does not call Goalserve at all. I file it within about 30 minutes.
5. Confidence 9/10 on the reading of 429; 5/10 on why the 18 Nov esports files are missing until the listing is pasted.
