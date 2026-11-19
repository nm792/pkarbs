#!/usr/bin/env python3
"""Read-only probe of one sport's Goalserve hour files with the SAME payload parsing as the v2 test (open_events).
Prints counters, market names seen, league prefixes, a few league strings and event counts. No cells, no verdicts, no keys.
Usage: gs_sport_probe.py "<glob of hour files>" "<poll log glob>" [t_lo_utc t_hi_utc as epoch seconds]"""
import sys, os, glob, json, gzip, collections
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import goalserve_odds_vs_pm_v2 as g
files = sorted(glob.glob(sys.argv[1])); drops = collections.Counter()
polls = g.load_polls([sys.argv[2]], drops)
lo = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; hi = float(sys.argv[4]) if len(sys.argv) > 4 else 1e12
ev, audit = g.open_events(files, polls, lo, hi)
print("files", len(files), "polls", len(polls), "events", len(ev))
for k in ("counters", "bm_values", "market_names_used", "market_names_excluded", "league_prefixes_seen"):
    print(k, json.dumps(audit[k])[:1500])
ls = collections.Counter(); names = collections.Counter(); n = 0
for p in files[:2]:
    for line in gzip.open(p, "rt", errors="replace"):
        try: d = json.loads(json.loads(line)["body"])
        except Exception: continue
        for e in (d.get("events") or {}).values():
            if isinstance(e, dict):
                ls[str((e.get("info") or {}).get("league"))[:60]] += 1
                if n < 3:
                    ti = e.get("team_info") or {}; print("sample teams", (ti.get("home") or {}).get("name"), "|", (ti.get("away") or {}).get("name")); n += 1
print("league strings", json.dumps(ls.most_common(12)))
