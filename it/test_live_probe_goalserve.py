#!/usr/bin/env python3
"""Offline test for REPLY-2026-11-19-live_probe_goalserve.py. Run: python3 -I it/test_live_probe_goalserve.py  (last line must be ALL PASS).
Each check can fail: planted odds edge must create an event, planted PM move after it must give a positive onset, a PM move BEFORE it a negative onset,
flat PM gives none, spread/total markets must not map, suspended markets must not create events, preflight must fail with no PM messages."""
import importlib.util, os, sys, json, time, asyncio
here = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("probe", os.path.join(here, "REPLY-2026-11-19-live_probe_goalserve.py"))
P = importlib.util.module_from_spec(sp); sp.loader.exec_module(P)
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name); 
    if not ok: fails.append(name)

# 1 mapping
m = dict(hk=P.key_of("Team Liquid"), ak=P.key_of("G2 Esports"))
check("key_of drops filler words", m == dict(hk="liquid", ak="g2"))
check("outcomes in home,away order", P.tok_match(m, "Counter-Strike: Team Liquid vs. G2 Esports (BO3)", ["Team Liquid", "G2 Esports"]) == (0, 1))
check("outcomes in away,home order", P.tok_match(m, "Counter-Strike: Team Liquid vs. G2 Esports (BO3)", ["G2 Esports", "Team Liquid"]) == (1, 0))
check("spread market not mapped", P.tok_match(m, "Spread: Team Liquid (-1.5) vs. G2 Esports", ["Team Liquid", "G2 Esports"]) is None)
check("map market not mapped", P.tok_match(m, "Team Liquid vs. G2 Esports - Map 1 Winner", ["Team Liquid", "G2 Esports"]) is None)
check("over/under outcomes not mapped", P.tok_match(m, "Team Liquid vs. G2 Esports", ["Over", "Under"]) is None)
check("tennis surname key", P.key_of("Djokovic N.") == "djokovic")

# 2 goalserve parsing through gs_poll with a scripted feed
def body(ph_home_odds, away_odds, susp=0):
    return json.dumps({"events": {"E1": {"info": {"league": "CS2 - X"}, "team_info": {"home": {"name": "Team Liquid"}, "away": {"name": "G2 Esports"}},
        "odds": {"1": {"name": "Match Winner", "suspend": susp, "participants": {"a": {"name": "Team Liquid", "value_eu": ph_home_odds, "suspend": 0}, "b": {"name": "G2 Esports", "value_eu": away_odds, "suspend": 0}}},
                 "2": {"name": "Total Maps", "suspend": 0, "participants": {"a": {"name": "Over", "value_eu": "1.9", "suspend": 0}, "b": {"name": "Under", "value_eu": "1.9", "suspend": 0}}}}}}}).encode()
seq = [body("2.00", "2.00"), body("2.00", "2.00"), body("1.70", "2.30"), body("1.60", "2.50", susp=1), body("1.40", "3.00"), body("1.40", "3.00")]
state = {"i": 0}
def fake_fetch(sport):
    i = min(state["i"], len(seq) - 1); state["i"] += 1
    return time.time(), seq[i] + (b" " * i if i == 1 else b"")   # distinct sha on the duplicate
class Fast:
    @staticmethod
    async def sleep(x): await P_real_sleep(0.001)
    @staticmethod
    async def to_thread(f, *a): return f(*a)
P_real_sleep = asyncio.sleep
P.fetch = fake_fetch
async def run_gs():
    P.asyncio = Fast
    t = asyncio.ensure_future(P.gs_poll("esports")); await P_real_sleep(0.5); t.cancel()
    P.asyncio = asyncio
asyncio.run(run_gs())
ev = [e for e in P.events if e["sport"] == "esports"]
check("exactly one event (planted 2.00/2.00 -> 1.70/2.30; suspended step and the step after it excluded; Total Maps ignored)", len(ev) == 1)
check("event rising team is home", bool(ev) and ev[0]["rising"] == "home" and ev[0]["ph_after"] - ev[0]["ph_before"] > 0.02)

# 3 summarize on planted PM books
P.events.clear(); P.mt.clear(); P.mv.clear(); P.pm_mk.clear(); P.games.clear()
now = time.time(); t = now - 200
P.games[("esports", "E1")] = dict(label="Team Liquid vs G2 Esports", home="Team Liquid", away="G2 Esports", hk="liquid", ak="g2", league="")
P.pm_mk[("esports", "E1")] = [dict(q="Team Liquid vs. G2 Esports", tokens=["TH", "TA"], outcomes=["Team Liquid", "G2 Esports"], tok_home="TH", tok_away="TA")]
P.events.append(dict(sport="esports", eid="E1", label="x", t=t, rising="home", ph_before=0.5, ph_after=0.56))
def book(tok, pts):
    for dt, v in pts: P.mt.setdefault(tok, []).append(t + dt); P.mv.setdefault(tok, []).append(v)
book("TH", [(-300, .50), (10, .56)]); book("TA", [(-300, .50), (10, .44)])
rows, out = P.summarize()
check("planted PM move 10 s after the odds event gives onset about +10 s on the own token", rows and abs(rows[0]["onset_s"] - 10) < 0.01)
check("planted move gives positive R", rows and rows[0]["R"] > 0.04)
P.mt.clear(); P.mv.clear()
book("TH", [(-300, .50), (-10, .56)]); book("TA", [(-300, .50), (-10, .44)])
rows, out = P.summarize()
check("PM move 10 s BEFORE the odds event gives negative onset (price first)", rows and abs(rows[0]["onset_s"] + 10) < 0.01)
P.mt.clear(); P.mv.clear()
book("TH", [(-300, .50)]); book("TA", [(-300, .50)])
rows, out = P.summarize()
check("flat PM gives no onset", rows and rows[0]["onset_s"] is None)
P.mt.clear(); P.mv.clear()
book("TH", [(-300, .50), (10, .56)]); book("TA", [(-300, .50), (10, .56)])
rows, out = P.summarize()
check("away token is not used for a home-rising event (own token only)", rows and rows[0]["token"] == "TH")

# 4 preflight must be able to fail
P.pm_n.clear(); P.pm_lag.clear(); P.gs_seen_now["esports"]["E1"] = time.time(); P.gs_poll_t["esports"][:] = [now + i for i in range(40)]
pre = P.preflight(["esports"])
check("preflight fails with no PM messages and no lag data", pre["per_sport"]["esports"]["report"] is False)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
