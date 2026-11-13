#!/usr/bin/env python3
"""Add a capture window to the rugby config from Polymarket gamma event slugs. Stdlib only.
  python3 build_rugby_window.py --window P1 --slugs ruprem-bat-bri-2026-12-04 --espn 267979 [--config PATH]
Each event gets: ticker, title, kickoffUTC (gameStartTime), espnLeague, markets[{question, conditionId, clobTokenIds}].
Exit 0 only if EVERY slug was found with tokens; otherwise exit 1 and the config is left unchanged (Polymarket lists
events ~2 weeks ahead, so an early call fails cleanly and is retried next round). Existing windows are never touched."""
import argparse, json, os, sys, urllib.request, urllib.parse
UA = {"User-Agent": "Mozilla/5.0 pkarbs-research"}
HERE = os.path.dirname(os.path.abspath(__file__))
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r: return json.load(r)
def find(slug):
    d = get("https://gamma-api.polymarket.com/events?slug=" + urllib.parse.quote(slug))
    return d[0] if d else None
def build(ev, espn):
    ms = []
    for m in ev.get("markets", []):
        t = m.get("clobTokenIds"); t = json.loads(t) if isinstance(t, str) else (t or [])
        if t: ms.append({"question": m.get("question"), "conditionId": m["conditionId"], "clobTokenIds": t})
    g = next((m.get("gameStartTime") for m in ev.get("markets", []) if m.get("gameStartTime")), None)
    if not g or not ms: return None
    ko = g.replace(" ", "T").replace("+00", "Z")
    return {"ticker": ev["slug"], "title": ev.get("title"), "kickoffUTC": ko, "espnLeague": espn, "markets": ms}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", required=True); ap.add_argument("--slugs", default="")
    ap.add_argument("--prefix", default="", help="discover instead of --slugs: every event whose slug starts with PREFIX- and ends with one of --dates")
    ap.add_argument("--dates", default="", help="comma list YYYY-MM-DD used with --prefix")
    ap.add_argument("--espn", default="267979"); ap.add_argument("--config", default=f"{HERE}/rugby-top14-config-2026-11-07.json")
    a = ap.parse_args()
    out, missing = [], []
    slugs = [x for x in a.slugs.split(",") if x.strip()]
    if a.prefix:
        dates = [d.strip() for d in a.dates.split(",") if d.strip()]
        found = {}
        for closed in ("false", "true"):   # tag 102193 = rugby; paged, newest first
            for off in range(0, 600, 100):
                d = get(f"https://gamma-api.polymarket.com/events?tag_id=102193&closed={closed}&limit=100&offset={off}&order=startDate&ascending=false")
                if not d: break
                for ev in d:
                    sl = ev.get("slug", "")
                    if sl.startswith(a.prefix + "-") and any(sl.endswith(x) for x in dates): found[sl] = 1
        slugs = sorted(found)
        if not slugs: print(json.dumps({"window": a.window, "ok": False, "missing": [f"{a.prefix}-*-{a.dates}"]})); sys.exit(1)
    for s in slugs:
        ev = find(s.strip()); b = build(ev, a.espn) if ev else None
        (out if b else missing).append(b or s.strip())
    if missing:
        print(json.dumps({"window": a.window, "ok": False, "missing": missing})); sys.exit(1)
    cfg = json.load(open(a.config)) if os.path.exists(a.config) else {}
    cfg[a.window] = out
    tmp = a.config + ".tmp"; json.dump(cfg, open(tmp, "w"), indent=1); os.replace(tmp, a.config)
    print(json.dumps({"window": a.window, "ok": True, "events": len(out), "kickoffs": [e["kickoffUTC"] for e in out]}))
main()
