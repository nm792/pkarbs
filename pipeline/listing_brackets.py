"""Bracket series listing path: YES-token own prints in the first 30 min after listing; does the favourite at +30 min equal the winner?"""
import json, os, sys, collections, concurrent.futures as cf
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen, listing_study as L
S = ["us-gas-price-daily", "elon-tweets-48h", "trump-truth-social", "spy-daily-close-uo", "wti-daily-close-uo"]


def main(n=20):
    ev = collections.defaultdict(dict)
    for p in ("/home/user/pk_cache/events.jsonl", "/home/user/pk_cache/events_deep.jsonl"):
        for l in open(p):
            e = json.loads(l)
            if e.get("seriesSlug") in S and e.get("startDate"): ev[e["seriesSlug"]][e["id"]] = e
    out = []
    for s in S:
        es = sorted(ev[s].values(), key=lambda e: e["endDate"])[-n:]
        for e in es:
            ls = screen.parse_ts(e["startDate"]); end = screen.parse_ts(e["endDate"])
            mk = []
            for m in e["markets"]:
                b = screen.binary_resolved(m)
                if not b: continue
                lab = [x.lower() for x in b["labels"]]
                if "yes" not in lab: continue
                iy = lab.index("yes"); mk.append((b, iy))
            if len(mk) < 3: continue
            def f(x):
                b, iy = x; tok = b["tokens"][iy]
                h = L.hist(tok, ls - 60, ls + 3600)
                tr = [r for r in screen.get_trades(b["cond"])["rows"] if r[2] == tok and ls <= r[0] <= ls + 1800 and r[1] == "BUY"]
                return dict(win=b["win"] == iy, h=h, usd=float(sum(r[3] * r[4] for r in tr)), n=len(tr), tr=tr)
            with cf.ThreadPoolExecutor(6) as ex: res = list(ex.map(f, mk))
            row = dict(series=s, date=e["endDate"][:10], n_mk=len(mk), usd30=sum(r["usd"] for r in res), n30=sum(r["n"] for r in res))
            for lab, off in (("p1", 60), ("p5", 300), ("p30", 1800)):
                px = [L.last_at(r["h"], ls + off, 1800) for r in res]
                row[lab + "_fav"] = max([p for p in px if p is not None], default=None)
                wp = [p for p, r in zip(px, res) if r["win"]]; row[lab + "_win"] = wp[0] if wp and wp[0] is not None else None
                valid = [(p, r["win"]) for p, r in zip(px, res) if p is not None]
                row[lab + "_fav_is_win"] = (max(valid)[1] if valid else None)
            first = [r["tr"][0][0] - ls for r in res if r["tr"]]
            row["first_print_s"] = min(first) if first else None
            out.append(row)
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "out/listing1/brackets.json", "w"), default=float)
    print(len(out))


if __name__ == "__main__": main()
