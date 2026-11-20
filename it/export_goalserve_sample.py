#!/usr/bin/env python3
"""READ-ONLY: export a small per-match sample of RAW Goalserve events so a human can eyeball them against Polymarket trades.
For each --sport DIR, picks the --n matches with the most winner-market odds changes in the given hour files, and writes
<out>/sample-<sport>[-game].jsonl.gz: one row per CHANGE of that event: {eid, recv_ns, event: <the raw event dict with ONLY the winner market kept in odds>}.
Also writes <out>/index.json (per match: eid, home, away, league, first/last recv_ns, n_changes, bytes). No credentials in the data. Writes only under --out.
Usage: python3 -I export_goalserve_sample.py --out DIR --files 'GLOB' [--files ...] --sport tennis [--game cs2|dota2] [--n 3]
(--game filters esports by the league prefix before ' - ', normalised: 'counter strike' -> cs2, 'dota 2' -> dota2.)"""
import argparse, collections, glob, gzip, hashlib, json, os, re


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def is_winner(sport, name):
    n = norm(name)
    return n == "to win" if sport == "tennis" else n == "home away"


def game_of(sport, league):
    if sport != "esports":
        return sport
    p = norm(str(league).split(" - ", 1)[0])
    return "cs2" if ("counter" in p or "cs" == p or "cs2" in p or "csgo" in p) else "dota2" if "dota" in p else p or "unparsed"


def run(a):
    files = sorted({f for g in a.files for f in glob.glob(g)})
    seen = {}        # eid -> list of (recv_ns, event_json_str)
    meta = {}
    last = {}
    for p in files:
        try:
            with gzip.open(p, "rt") as f:
                for l in f:
                    try:
                        r = json.loads(l); d = json.loads(r["body"])
                    except Exception:
                        continue
                    for eid, e in (d.get("events") or {}).items():
                        if not isinstance(e, dict):
                            continue
                        lg = (e.get("info") or {}).get("league") or ""
                        if a.game and game_of(a.sport, lg) != a.game:
                            continue
                        odds = {k: m for k, m in (e.get("odds") or {}).items() if isinstance(m, dict) and is_winner(a.sport, m.get("name"))}
                        if not odds:
                            continue
                        ev = dict(e); ev["odds"] = odds
                        s = json.dumps(ev, sort_keys=True)
                        h = hashlib.md5(s.encode()).hexdigest()
                        if last.get(eid) == h:
                            continue
                        last[eid] = h
                        seen.setdefault(eid, []).append((r["recv_ns"], s))
                        ti = e.get("team_info") or {}
                        meta[eid] = dict(eid=eid, home=(ti.get("home") or {}).get("name"), away=(ti.get("away") or {}).get("name"), league=lg)
        except (EOFError, OSError):
            pass
    top = sorted(seen, key=lambda k: -len(seen[k]))[:a.n]
    os.makedirs(a.out, exist_ok=True)
    name = "sample-%s%s.jsonl.gz" % (a.sport, "-" + a.game if a.game else "")
    idx = []
    with gzip.open(os.path.join(a.out, name), "wt") as f:
        for eid in top:
            nb = 0
            for t, s in seen[eid]:
                line = json.dumps({"eid": eid, "recv_ns": t, "event": json.loads(s)}); nb += len(line); f.write(line + "\n")
            idx.append(dict(meta[eid], first_recv_ns=seen[eid][0][0], last_recv_ns=seen[eid][-1][0], n_changes=len(seen[eid]), raw_bytes=nb))
    json.dump(dict(sport=a.sport, game=a.game, files=len(files), matches=idx), open(os.path.join(a.out, "index-%s.json" % name[7:-9]), "w"), indent=1)
    return idx


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--files", action="append", required=True)
    ap.add_argument("--sport", required=True, choices=("esports", "tennis", "hockey_nhl")); ap.add_argument("--game"); ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()
    for m in run(a):
        print(json.dumps(m))
