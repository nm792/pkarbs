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

# 1 mapping (new: fuzzy team tokens, outcomes must be exactly the two teams) and market-name filter
def meta(h, a): return dict(home=h, away=a, hk=P.key_of(h), ak=P.key_of(a))
check("outcomes in home,away order", P.tok_match(meta("Team Liquid", "G2 Esports"), ["Team Liquid", "G2 Esports"]) == (0, 1))
check("outcomes in away,home order", P.tok_match(meta("Team Liquid", "G2 Esports"), ["G2 Esports", "Team Liquid"]) == (1, 0))
check("Over/Under outcomes not mapped", P.tok_match(meta("Team Liquid", "G2 Esports"), ["Over", "Under"]) is None)
check("Yes/No outcomes not mapped", P.tok_match(meta("Team Liquid", "G2 Esports"), ["Yes", "No"]) is None)
check("Goalserve 'UTA Mammoth' / 'COL Avalanche' map to Polymarket 'Avalanche' / 'Utah' (prefix rule)", P.tok_match(meta("UTA Mammoth", "COL Avalanche"), ["Avalanche", "Utah"]) == (1, 0))
check("tennis surnames map", P.tok_match(meta("Tristan Schoolkate", "Alafia Ayeni"), ["Tristan Schoolkate", "Alafia Ayeni"]) == (0, 1))
check("both outcomes matching the SAME team is rejected", P.tok_match(meta("Team Liquid", "G2 Esports"), ["Team Liquid A", "Team Liquid B"]) is None)
check("kind_ok accepts winner names", all(P.kind_ok(x) for x in ("Match Winner", "To Win", "Money Line", "Moneyline (Including OT)", "Home/Away")))
check("kind_ok rejects sub-markets", not any(P.kind_ok(x) for x in ("Set 2 Winner", "Map 1 Winner", "1x2 (1st Period)", "Draw No Bet", "Highest Scoring Period", "Over/Under (Including OT)", "Asian Handicap", "Team To Win The Most Periods")))
check("tennis surname key", P.key_of("Djokovic N.") == "djokovic")

# 1b discovery against a fake gamma (events by tag, paginated at 100, moneyline only, ambiguity dropped)
def ev(title, mkts): return {"title": title, "markets": mkts}
def mk(kind, oc, tk, q=None): return {"sportsMarketType": kind, "outcomes": json.dumps(oc), "clobTokenIds": json.dumps(tk), "question": q or " vs ".join(oc), "gameStartTime": "2026-11-19 02:00:00+00"}
P.games.clear(); P.pm_mk.clear(); P.ambiguous.clear()
P.games[("hockey_nhl", "G1")] = dict(label="UTA Mammoth vs COL Avalanche", home="UTA Mammoth", away="COL Avalanche", hk="mammoth", ak="avalanche", league="")
P.games[("tennis", "G2")] = dict(label="Tristan Schoolkate vs Alafia Ayeni", home="Tristan Schoolkate", away="Alafia Ayeni", hk="schoolkate", ak="ayeni", league="")
P.games[("tennis", "G3")] = dict(label="Max Smith vs John Doe", home="Max Smith", away="John Doe", hk="smith", ak="doe", league="")
pages = {"nhl": [ev("Avalanche vs. Utah", [mk("moneyline", ["Avalanche", "Utah"], ["A1", "A2"]), mk("totals", ["Over", "Under"], ["T1", "T2"])])],
         "tennis": [ev("Sydney: Tristan Schoolkate vs Alafia Ayeni", [mk("moneyline", ["Tristan Schoolkate", "Alafia Ayeni"], ["S1", "S2"]), mk("child_moneyline", ["Tristan Schoolkate", "Alafia Ayeni"], ["C1", "C2"])]),
                    ev("X: Max Smith vs John Doe", [mk("moneyline", ["Max Smith", "John Doe"], ["D1", "D2"])]), ev("Y: Max Smith vs John Doe (rematch)", [mk("moneyline", ["Max Smith", "John Doe"], ["D3", "D4"])])]}
calls = []
def fake_get(url):
    calls.append(url); tag = url.split("tag_slug=")[1].split("&")[0]; off = int(url.split("offset=")[1].split("&")[0])
    return pages.get(tag, []) if off == 0 else []
P.get = fake_get
new_t, scanned = P.discover(["hockey_nhl", "tennis"])
check("NHL game mapped to the moneyline tokens, totals ignored", [x["tokens"] for x in P.pm_mk.get(("hockey_nhl", "G1"), [])] == [["A1", "A2"]] and P.pm_mk[("hockey_nhl", "G1")][0]["tok_home"] == "A2")
check("tennis game mapped to moneyline, child_moneyline ignored", [x["tokens"] for x in P.pm_mk.get(("tennis", "G2"), [])] == [["S1", "S2"]])
check("game matching two Polymarket events is dropped as AMBIGUOUS, not guessed", ("tennis", "G3") not in P.pm_mk and ("tennis", "G3") in P.ambiguous)
check("tags queried for both sports (nhl, ahl, hockey, tennis)", sum("tag_slug=nhl" in c for c in calls) == 1 and any("tag_slug=tennis" in c for c in calls) and any("tag_slug=ahl" in c for c in calls))

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


# 2b capture-tail source: reads rows appended to the capture's hour file (one gzip member per row), starts at the END, tolerates a half-written member
import gzip, tempfile, zlib
tmp = tempfile.mkdtemp(); sport = "tennis"
while time.gmtime().tm_min == 59 and time.gmtime().tm_sec > 55: time.sleep(1)
hf = P.hour_file(tmp, sport, time.time()); os.makedirs(os.path.dirname(hf))
def member(recv_ns, b): return gzip.compress((json.dumps({"recv_ns": recv_ns, "body": b.decode()}) + "\n").encode())
tb = lambda ho, ao, tag="": body(ho, ao).replace(b"CS2 - X", b"ITF" + tag.encode())
with open(hf, "ab") as f: f.write(member(1, body("1.20", "5.00")))                 # pre-start row: ph 0.81 would make the next row an event if it were read
rows, off = P.read_new(hf, 0); check("read_new decodes a whole member", len(rows) == 1 and off == os.path.getsize(hf))
m2 = member(2, body("2.00", "2.00")); half = len(m2) // 2
with open(hf, "ab") as f: f.write(m2[:half])
rows2, off2 = P.read_new(hf, off); check("half-written trailing member is not decoded and the offset does not move", rows2 == [] and off2 == off)
with open(hf, "ab") as f: f.write(m2[half:])
rows3, off3 = P.read_new(hf, off); check("completed member is decoded", len(rows3) == 1 and off3 == os.path.getsize(hf))
tmp2 = tempfile.mkdtemp(); hf2 = P.hour_file(tmp2, sport, time.time()); os.makedirs(os.path.dirname(hf2))
with open(hf2, "ab") as f: f.write(member(1, body("1.20", "5.00")))
P.events.clear(); P.games.clear(); P.gs_poll_t.clear(); P.gs_change_t.clear(); P.SOURCE.update(mode="capture", root=tmp2)
T_REC = int((time.time() + 5) * 1e9)
async def run_tail():
    P.asyncio = asyncio
    t = asyncio.ensure_future(P.gs_tail(sport)); await asyncio.sleep(0.8)          # tail has started at the end of the file
    for k, (ho, ao) in enumerate([("2.00", "2.00"), ("2.00", "2.00 "), ("1.70", "2.30")]):
        with open(hf2, "ab") as f: f.write(member(T_REC + k * 10**9, body(ho, ao.strip()) + b" " * k))
        await asyncio.sleep(0.8)
    t.cancel()
asyncio.run(run_tail())
ev2 = [e for e in P.events if e["sport"] == sport]
check("tail: pre-start row skipped (one event only: 2.00/2.00 -> 1.70/2.30)", len(ev2) == 1 and ev2[0]["rising"] == "home")
check("tail: event time is the capture's recv_ns, not the read time", len(ev2) == 1 and abs(ev2[0]["t"] - (T_REC + 2 * 10**9) / 1e9) < 1e-3)
check("tail: games learned from the stored payloads", ("tennis", "E1") in P.games)
P.SOURCE.update(mode="poll")

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
