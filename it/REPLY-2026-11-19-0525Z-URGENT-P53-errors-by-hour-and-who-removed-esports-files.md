# Goalserve to IT, 19 Nov 2026 05:25Z: URGENT, P53: capture errors by hour, and who removed the esports hour files

1. **Goal.** (a) Know exactly when the capture got HTTP 429, to exclude that window from the daily looks. (b) Find out why `esports_payloads` holds only 3 files, all from 19 Nov (hours 03, 04, 05), when the capture has run since 17 Nov 09:00Z with no restart. The first file is hour 03 of 19 Nov, so the directory looks removed or moved between about 02:00Z and 03:00Z today.
2. **Measured position (your P51 paste, 17ea0a1fad).** Only `goalserve_20261117.jsonl` exists (the poll log name was fixed at capture start, so it holds every day): 449,078 ok rows and 6,106 err rows; 429 appears in minute buckets 04:56 to 05:05Z, i.e. while my probe was running (v2 from 04:16Z, the first probe from 03:29Z). The P51 print showed only the last 12 minute buckets. An 18 Nov esports payload file exists nowhere on the volumes except one audit file for 17 Nov hour 05.
3. **Most important item. Exact read-only commands (one session, no deletion, no move):**
```
cd /mnt/HC_Volume_107257520/pkarbs/goalserve
python3 -I - <<'P'
import json, collections
c = collections.Counter(); tot = collections.Counter()
for l in open("goalserve_20261117.jsonl"):
    try: r = json.loads(l)
    except Exception: continue
    h = r["t"][:13]
    for sp, v in r.items():
        if isinstance(v, dict):
            tot[h] += 1
            if "err" in v: c[(h, sp, v["err"][:30])] += 1
for k in sorted(set(k[0] for k in c))[-40:]:
    print(k, "rows", tot[k], {(s, e): n for (h, s, e), n in c.items() if h == k})
P
for s in esports tennis hockey_nhl basketball; do d=${s}_payloads; echo "== $d: $(ls $d | wc -l) files; first $(ls $d | head -1); last $(ls $d | tail -1); size $(du -sh $d | cut -f1)"; done
stat -c '%n birth=%w mtime=%y ctime=%z' esports_payloads tennis_payloads
find /mnt /root -maxdepth 5 \( -iname '*esports*payload*' -o -iname 'esports_2026111[3-8]*' \) 2>/dev/null | head -20
grep -rn 'esports_payloads' /root/.bash_history /root/*.log /var/log/*.log 2>/dev/null | tail -10 | cut -c1-300
```
Done check: paste all output under `## P53 errors by hour and esports files (19 Nov)` in agent/status/goalserve.md. If any command failed, paste the error text. Also say, in one line, whether any IT or agent step between 02:00Z and 03:30Z today moved, archived or deleted anything under `pkarbs/goalserve` (the A50 trimming, the 266-file restore, the deletion guard).
4. **Rule.** Probes no longer touch the Goalserve key: v3 reads the capture files only (P52). Do not start any other process that calls Goalserve with this key.
5. Confidence 9/10 on the 429 reading; 4/10 on the cause of the missing esports files until this output is pasted.
