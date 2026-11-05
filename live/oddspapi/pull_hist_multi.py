#!/usr/bin/env python3
"""Pull OddsPapi historical odds (Pinnacle, bet365, 1xbet) for past matches of other sports:
NBA, NHL, NFL, cricket, rugby, LoL, CS2, Dota. Read-only, standard library only.

Usage: ODDSPAPI_KEY=... python3 pull_hist_multi.py OUTDIR [--from ISO] [--to ISO] [--cap N] [--total N] [--sports a,b]
Default window 2026-10-16 .. 2026-11-05 in 7-day fixture windows (API needs < 10 days).
Cost: /v4/historical-odds is FREE. Billable: 1 account check + 1 bookmakers + 1 fixtures call
per sport per window (8 sports x 3 windows = 24). Aborts if the account shows < 60 requests left.
The key is never logged or saved.
"""
import datetime as dt, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pull_hist import get, save, log

# sportId, label, tournament/category slug keywords (empty = keep all), per-sport cap multiplier
SPORTS = [(11, "nba", ("nba",)), (15, "nhl", ("nhl",)), (18, "lol", ()), (17, "cs2", ()), (16, "dota", ()),
          (27, "cricket", ()), (26, "rugby", ("top-14", "premiership", "urc", "united-rugby", "international", "autumn", "nations", "test")),
          (14, "nfl", ("nfl",))]
BOOKS = "pinnacle,bet365,1xbet"


def windows(frm, to, days=7):
    a = dt.datetime.fromisoformat(frm.replace("Z", "+00:00")); b = dt.datetime.fromisoformat(to.replace("Z", "+00:00"))
    while a < b:
        c = min(b, a + dt.timedelta(days=days)); yield a.strftime("%Y-%m-%dT%H:%M:%SZ"), c.strftime("%Y-%m-%dT%H:%M:%SZ"); a = c


def main(argv, fetch=None):
    out = argv[0]
    opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
    frm, to = opt("--from", "2026-10-16T00:00:00Z"), opt("--to", "2026-11-05T00:00:00Z")
    cap, total = int(opt("--cap", 60)), int(opt("--total", 480))
    only = set(opt("--sports", "").split(",")) - {""}
    key = os.environ.get("ODDSPAPI_KEY") or open(os.path.expanduser("~/.oddspapi_key")).read().strip()
    os.makedirs(os.path.join(out, "hist"), exist_ok=True)
    log(out, ev="start", frm=frm, to=to, cap=cap, total=total)
    st, acc = get("account", key, fetch)
    if isinstance(acc, dict):
        acc = {k: v for k, v in acc.items() if "key" not in k.lower()}   # never log the key
    log(out, ev="account", st=st, acc=acc)
    left = None
    if isinstance(acc, dict):
        for k, v in acc.items():
            if "remain" in k.lower() and isinstance(v, (int, float)): left = v
    if left is not None and left < 60:
        log(out, ev="fail", why="quota low", left=left); return 2
    st, books = get("bookmakers", key, fetch)
    if st != 200:
        log(out, ev="fail", why="bookmakers", st=st); return 2
    fixtures = []
    for sid, lab, kws in SPORTS:
        if only and lab not in only: continue
        keep = []
        for a, b in windows(frm, to):
            st, fx = get("fixtures", key, fetch, sportId=sid, **{"from": a, "to": b})
            if st != 200 or not isinstance(fx, list):
                log(out, ev="fixtures_err", sport=lab, st=st, body=str(fx)[:200]); continue
            save(os.path.join(out, f"fixtures_{lab}_{a[:10]}.json.gz"), fx)
            for f in fx:
                slug = (str(f.get("tournamentSlug")) + " " + str(f.get("categorySlug")) + " " + str(f.get("tournamentName"))).lower()
                if f.get("statusId") != 2: continue                       # finished only
                if "(srl)" in (str(f.get("participant1Name")) + str(f.get("participant2Name"))).lower(): continue
                if "simulated" in slug or "women" in slug and lab in ("nba", "nhl", "nfl"): continue
                if kws and not any(k in slug for k in kws): continue
                keep.append(f)
        keep.sort(key=lambda f: f.get("startTime", ""), reverse=("--oldest" not in argv))   # most recent first (or oldest with --oldest)
        log(out, ev="fixtures", sport=lab, finished_kept=len(keep), taking=min(cap, len(keep)))
        fixtures += [(lab, f) for f in keep[:cap]]
    fixtures = fixtures[:total]
    ok = 0
    for i, (lab, f) in enumerate(fixtures):
        path = os.path.join(out, "hist", f"{lab}_{f['fixtureId']}.json.gz")
        if os.path.exists(path): continue
        st, h = get("historical-odds", key, fetch, fixtureId=f["fixtureId"], bookmakers=BOOKS)
        if st == 200:
            save(path, {"sport": lab, "fixture": f, "hist": h}); ok += 1
        else:
            log(out, ev="hist_err", fid=f["fixtureId"], st=st, body=str(h)[:200])
            if st == 429 and "REQUEST_LIMIT" in str(h): break
        if i % 25 == 0: log(out, ev="progress", i=i, of=len(fixtures), ok=ok)
    log(out, ev="done", fixtures=len(fixtures), hist_ok=ok)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
