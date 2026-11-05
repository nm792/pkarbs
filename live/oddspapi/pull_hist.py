#!/usr/bin/env python3
"""Pull OddsPapi historical odds (Pinnacle, bet365, + one more live book) for
tennis / CS2 / LoL / Dota fixtures in a UTC window. Read-only, standard library only.

Usage: ODDSPAPI_KEY=... python3 pull_hist.py OUTDIR [FROM_ISO] [TO_ISO] [--max-fixtures N]
Default window 2026-11-04T00:00:00Z .. 2026-11-05T12:00:00Z.

Cost: /v4/historical-odds is free (never counts). Billable calls: 1 sports + 1 bookmakers +
1 fixtures call per sport (about 6 total). Cooldowns respected (hist 5 s, fixtures 2 s).
"""
import gzip, json, os, sys, time, urllib.parse, urllib.request

HOST = "https://api.oddspapi.io"
UA = "pkarbs-oddspapi-hist/1.0"
SPORT_KEYS = ("tennis", "counter", "cs2", "csgo", "league of legends", "league-of-legends", "dota")
WANT_BOOKS = ["pinnacle", "bet365"]
EXTRA_BOOKS = ["1xbet", "ggbet", "sbobet", "betway"]  # first one that exists with liveOdds
COOLDOWN = {"historical-odds": 5.3, "fixtures": 2.2, "sports": 1.1, "bookmakers": 1.1}
_last = {}


def log(out, **kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = json.dumps(kw)
    print(line, flush=True)
    with open(os.path.join(out, "log.jsonl"), "a") as f:
        f.write(line + "\n")


def get(endpoint, key, fetch=None, **params):
    wait = COOLDOWN.get(endpoint, 1.1) - (time.time() - _last.get(endpoint, 0))
    if wait > 0:
        time.sleep(wait)
    params["apiKey"] = key
    url = f"{HOST}/v4/{endpoint}?" + urllib.parse.urlencode(params)
    _last[endpoint] = time.time()
    if fetch:
        return fetch(endpoint, params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            if e.code == 429 and "REQUEST_LIMIT" in body:
                return e.code, {"error": body}
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(6 * (attempt + 1)); continue
            return e.code, {"error": body}
        except Exception as e:  # network
            if attempt < 2:
                time.sleep(6 * (attempt + 1)); continue
            return -1, {"error": repr(e)}


def save(path, obj):
    with gzip.open(path, "wt") as f:
        json.dump(obj, f)


def main(argv, fetch=None):
    args = [a for a in argv if not a.startswith("--")]
    out = args[0]
    frm = args[1] if len(args) > 1 else "2026-11-04T00:00:00Z"
    to = args[2] if len(args) > 2 else "2026-11-05T12:00:00Z"
    maxfx = int(argv[argv.index("--max-fixtures") + 1]) if "--max-fixtures" in argv else 400
    key = os.environ.get("ODDSPAPI_KEY") or open(os.path.expanduser("~/.oddspapi_key")).read().strip()
    os.makedirs(os.path.join(out, "hist"), exist_ok=True)
    log(out, ev="start", frm=frm, to=to)

    st, sports = get("sports", key, fetch); save(os.path.join(out, "sports.json.gz"), sports)
    st2, books = get("bookmakers", key, fetch); save(os.path.join(out, "bookmakers.json.gz"), books)
    if st != 200 or st2 != 200:
        log(out, ev="fail", why="sports/bookmakers", st=st, st2=st2, body=str(sports)[:300]); return 2
    slugs = {b["slug"]: b for b in books}
    extra = next((s for s in EXTRA_BOOKS if s in slugs and slugs[s].get("liveOdds")), None)
    blist = [b for b in WANT_BOOKS if b in slugs] + ([extra] if extra else [])
    log(out, ev="books", use=blist, missing=[b for b in WANT_BOOKS if b not in slugs])
    chosen = [s for s in sports if any(k in (s.get("sportName", "") + " " + s.get("slug", "")).lower() for k in SPORT_KEYS)]
    log(out, ev="sports", chosen=[(s["sportId"], s["slug"]) for s in chosen], n_all=len(sports))

    fixtures = []
    for s in chosen:
        st, fx = get("fixtures", key, fetch, sportId=s["sportId"], **{"from": frm, "to": to})
        save(os.path.join(out, f"fixtures_{s['slug']}.json.gz"), fx)
        if st != 200:
            log(out, ev="fixtures_err", sport=s["slug"], st=st, body=str(fx)[:300]); continue
        keep = [f for f in fx if f.get("statusId") in (1, 2) and f.get("hasOdds")]
        log(out, ev="fixtures", sport=s["slug"], n=len(fx), live_or_done_with_odds=len(keep))
        fixtures += keep
    fixtures = fixtures[:maxfx]

    ok = 0
    for i, f in enumerate(fixtures):
        fid = f["fixtureId"]
        path = os.path.join(out, "hist", f"{fid}.json.gz")
        if os.path.exists(path):
            continue
        st, h = get("historical-odds", key, fetch, fixtureId=fid, bookmakers=",".join(blist))
        if st == 200:
            save(path, {"fixture": f, "hist": h}); ok += 1
        else:
            log(out, ev="hist_err", fid=fid, st=st, body=str(h)[:200])
            if st == 429 and "REQUEST_LIMIT" in str(h):
                break
        if i % 20 == 0:
            log(out, ev="progress", i=i, of=len(fixtures), ok=ok)
    log(out, ev="done", fixtures=len(fixtures), hist_ok=ok)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
