#!/usr/bin/env python3
"""Wrapper around feeds/ps_lead_test.py (unchanged file, same arguments, same STANDARD v1 rules).
Adds only: each event is tagged with the `latency` entry of field `round_score` in the SAME message that
produced it (PandaScore docs 17 Nov: latency = list of {field, delay}, delay in ms RELATIVE to the fastest
data point; round_score is usually the fastest). Extra cells in the output, per title and series:
  lat0 = round_score delay == 0 (round score is the fastest point in that message)
  lat>0 = round_score delay > 0
  lat_unknown = message has no latency array (before the field went live, or title without it)
Placebo for these cells = all placebo draws of the same title and series (placebo has no message).
No other behaviour change. Because extra cells draw from the same seeded random generator, the 'all' cells
of later titles can differ slightly from an unwrapped run: run both and say so.
Fails closed: if any patch target is not found exactly once in ps_lead_test.py, nothing runs.
Usage: same as ps_lead_test.py.  STATUS: exploratory, UNCHECKED (no rule-to-code table, not audited).
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "ps_lead_test.py")
SRC = open(PATH).read()

PATCHES = [
    ('def norm(s):',
     'def lat_of(m):\n'
     '    try:\n'
     '        for x in m.get("latency") or []:\n'
     '            if x.get("field") == "round_score":\n'
     '                return "lat0" if x.get("delay") == 0 else "lat>0"\n'
     '    except Exception:\n'
     '        pass\n'
     '    return "lat_unknown"\n\n\n'
     'def norm(s):'),
    ('ev.append((mid, slug, gid, r["recv_ns"] / 1e9, k[1], k[2], gorder[mid].index(gid) + 1))',
     'ev.append((mid, slug, gid, r["recv_ns"] / 1e9, k[1], k[2], gorder[mid].index(gid) + 1, lat_of(m)))'),
    ('for (mid, slug, gid, t, team, fld, gord) in ev:',
     'for (mid, slug, gid, t, team, fld, gord, latbin) in ev:'),
    ('stratum=vol_stratum(m), field=fld, t=t, tok=tok, lead=onset(tok, t, +1)))',
     'stratum=vol_stratum(m), field=fld, t=t, tok=tok, lead=onset(tok, t, +1), latbin=latbin))'),
    ('for strat in (("all", "<25k", ">=25k") if have_vol else ("all",)):',
     'for strat in (("all", "<25k", ">=25k") if have_vol else ("all",)) + ("lat0", "lat>0", "lat_unknown"):'),
    ('R = [r for r in rows if r["title"] == title and r["series"] == series_ and (strat == "all" or r["stratum"] == strat)]',
     'R = [r for r in rows if r["title"] == title and r["series"] == series_ and (strat == "all" or r["stratum"] == strat or r["latbin"] == strat)]'),
    ('P = [r for r in plc if r["title"] == title and r["series"] == series_ and (strat == "all" or r["stratum"] == strat)]',
     'P = [r for r in plc if r["title"] == title and r["series"] == series_ and (strat == "all" or strat.startswith("lat") or r["stratum"] == strat)]'),
]

for old, new in PATCHES:
    n = SRC.count(old)
    if n != 1:
        sys.exit("PATCH TARGET FOUND %d TIMES (need exactly 1), nothing run: %s" % (n, old[:70]))
    SRC = SRC.replace(old, new)

g = {"__name__": "__main__", "__file__": PATH}
exec(compile(SRC, "ps_lead_test_patched", "exec"), g)
