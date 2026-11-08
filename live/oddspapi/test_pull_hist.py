"""Offline test of pull_hist.py with a fake API (no network)."""
import gzip, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import pull_hist as P

P.COOLDOWN = {k: 0 for k in P.COOLDOWN}
calls = []

def fake(ep, params):
    calls.append((ep, dict(params)))
    if ep == "sports":
        return 200, [{"sportId": 12, "slug": "tennis", "sportName": "Tennis"},
                     {"sportId": 17, "slug": "counter-strike", "sportName": "Counter-Strike"},
                     {"sportId": 10, "slug": "soccer", "sportName": "Soccer"},
                     {"sportId": 25, "slug": "table-tennis", "sportName": "Table Tennis"}]
    if ep == "bookmakers":
        return 200, [{"slug": "pinnacle", "liveOdds": True}, {"slug": "bet365", "liveOdds": True},
                     {"slug": "1xbet", "liveOdds": False}, {"slug": "ggbet", "liveOdds": True}]
    if ep == "fixtures":
        return 200, [{"fixtureId": f"f{params['sportId']}a", "statusId": 2, "hasOdds": False},
                     {"fixtureId": f"f{params['sportId']}b", "statusId": 0, "hasOdds": True},
                     {"fixtureId": f"f{params['sportId']}c", "statusId": 2, "hasOdds": True,
                      "participant1Name": "Alcaraz, Carlos (Srl)", "participant2Name": "X (Srl)"}]
    if ep == "historical-odds":
        return 200, {"fixtureId": params["fixtureId"], "bookmakers": {}}

d = tempfile.mkdtemp(); os.environ["ODDSPAPI_KEY"] = "x"
rc = P.main([d], fetch=fake)
eps = [c[0] for c in calls]
assert rc == 0, rc
assert eps.count("fixtures") == 2 and eps.count("historical-odds") == 2, eps
assert all(c[1]["bookmakers"] == "pinnacle,bet365,ggbet" for c in calls if c[0] == "historical-odds")
assert sorted(os.listdir(os.path.join(d, "hist"))) == ["f12a.json.gz", "f17a.json.gz"]
print("4 of 4 checks pass")
