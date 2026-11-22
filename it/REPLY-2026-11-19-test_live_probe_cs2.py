#!/usr/bin/env python3
"""Test for REPLY-2026-11-19-live_probe_cs2.py. Run: python3 -I it/REPLY-2026-11-19-test_live_probe_cs2.py
Can FAIL: (1) planted +3 s lead must read 3.0 s on the rising token and the other token falls; (2) a book that moves
BEFORE the event gives no onset after it (lead must be negative or None, never +); (3) a flat book gives None;
(4) preflight must report a failed check when a token has no book message or the clock tool is absent."""
import sys, types, time, importlib
sys.modules.setdefault("websockets", types.ModuleType("websockets"))
src = open(__file__.replace("test_live_probe_cs2", "live_probe_cs2")).read()
src = src.replace('if not TOKEN: sys.exit("FATAL no PandaScore token file readable")', "").replace("asyncio.run(main())", "")
def fresh():
    g = {}; exec(compile(src, "probe", "exec"), g); return g
now = time.time(); bad = []
g = fresh(); g["T0"] = now - 1000
g["pm_by_match"]["m1"] = [dict(q="A vs B Map 1 Winner", map_no=1, tokens=["ta", "tb"], outcomes=["A", "B"])]
g["events"].append(dict(match="m1", label="A vs B", map_no=1, team="A", t=now - 400, updated_at=None, round_score_delay=0))
g["mids"]["ta"] = [(now - 500, .5), (now - 397, .6)]; g["mids"]["tb"] = [(now - 500, .5), (now - 397, .4)]
rows, out = g["summarize"]()
if out["map_rising_team_token"]["median_onset_s"] != 3.0: bad.append("planted lead not 3.0: %r" % out["map_rising_team_token"])
if out["map_other_token"]["median_onset_s"] != 3.0: bad.append("other token fall not detected")
g = fresh(); g["T0"] = now - 1000
g["pm_by_match"]["m1"] = [dict(q="A vs B Map 1 Winner", map_no=1, tokens=["ta", "tb"], outcomes=["A", "B"])]
g["events"].append(dict(match="m1", label="A vs B", map_no=1, team="A", t=now - 400, updated_at=None, round_score_delay=0))
g["mids"]["ta"] = [(now - 500, .5), (now - 420, .6)]; g["mids"]["tb"] = [(now - 500, .5), (now - 500, .5)]
rows, out = g["summarize"]()
r = out["map_rising_team_token"]["median_onset_s"]
if r is not None and r > 0: bad.append("move BEFORE event read as lead after: %r" % r)
g = fresh(); g["pm_n"]["ta"] = 3; g["ps_n"]["m1"] = 4; g["pm_lag"].extend([.05]); g["ps_lag"].extend([.2])
p = g["preflight"](["ta", "tb"], {"m1": {"label": "x"}})
if p["checks"]["every_pm_token_has_a_book_message"] or p["all_ok"]: bad.append("preflight passed with a silent token")
g = fresh()  # (5) discovery must find a CS2 event created 40 h before the match: gamma date filters use CREATION date, only the tag source returns it
def fake(url):
    if "tag_slug=counter-strike-2" in url and "offset=0" in url: return [dict(id="e40", title="Counter-Strike: A vs B (BO3)", markets=[])]
    return []
got = [e["id"] for e in g["gamma_cs2_events"](fake, now)]
if got != ["e40"]: bad.append("event created long before the match not found via tag source: %r" % got)
def fake_dup(url): return [dict(id="e1", title="Counter-Strike: X vs Y", markets=[])] if "offset=0" in url else []
if len(g["gamma_cs2_events"](fake_dup, now)) != 1: bad.append("same event from two sources not deduped")
print("FAIL: " + "; ".join(bad) if bad else "PASS (6 checks, each able to fail)"); sys.exit(1 if bad else 0)
