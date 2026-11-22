#!/usr/bin/env python3
"""One chart per sampled CS2 match: PandaScore in-round field changes vs public Polymarket trade prices.
usage: python3 ps_chart_samples.py SAMPLEDIR OUTDIR     (needs matplotlib; network to gamma + data-api v2)
Events (vertical lines): K=alive count drop (kill), B=bomb status change, T=round score rise (round end).
Prices: public trades for the match's moneyline + map winner markets (gamma tag counter-strike-2, matched on team names)."""
import sys, os, gzip, json, glob, re, urllib.request
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30); b = r.read()
    return json.loads(gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b)
def events(msgs):
    ev = []; prev = None
    for d in msgs:
        p = d["payload"]; t = d["recv_ns"] / 1e9; cr = p.get("current_round") or {}
        al = sum(bool(pl.get("alive")) for tm in ("home_team", "away_team") for pl in (cr.get(tm) or {}).get("players", []))
        has = any((cr.get(tm) or {}).get("players") for tm in ("home_team", "away_team"))
        cur = dict(score=((p.get("home_team") or {}).get("score"), (p.get("away_team") or {}).get("score")),
                   alive=al if has else None, bomb=(cr.get("bomb") or {}).get("status"), rnd=cr.get("round_number"))
        if prev:
            if cur["alive"] is not None and prev["alive"] is not None and cur["rnd"] == prev["rnd"] and cur["alive"] < prev["alive"]: ev.append((t, "K", f"alive {prev['alive']}->{cur['alive']}"))
            if cur["bomb"] != prev["bomb"] and cur["rnd"] == prev["rnd"]: ev.append((t, "B", f"bomb {prev['bomb']}->{cur['bomb']}"))
            if cur["score"] != prev["score"] and None not in cur["score"] + prev["score"]: ev.append((t, "T", f"score {prev['score']}->{cur['score']}"))
        prev = cur
    return ev
def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
def find_markets(h, a, t0):
    out = []
    for off in range(0, 400, 100):
        for e in get(f"https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2&limit=100&offset={off}&closed=false") + get(f"https://gamma-api.polymarket.com/events?tag_slug=counter-strike-2&limit=100&offset={off}&closed=true&order=startDate&ascending=false"):
            ti = norm(e.get("title"))
            if norm(h) in ti and norm(a) in ti:
                for m in e.get("markets", []): out.append((m.get("question"), m.get("conditionId"), json.loads(m.get("outcomes") or "[]")))
    return out
def trades(cid):
    r = []; cur = None
    for _ in range(40):
        j = get(f"https://data-api.polymarket.com/v2/trades?condition={cid}&limit=500" + (f"&cursor={cur}" if cur else ""))
        r += j.get("data", []); cur = j.get("next_cursor")
        if not cur or not j.get("data"): break
    return r
def main(sd, od):
    os.makedirs(od, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(sd, "ps_sample_*.jsonl.gz"))):
        msgs = [json.loads(l) for l in gzip.open(f, "rt")]
        if not msgs: continue
        p0 = next((m["payload"] for m in reversed(msgs) if m["payload"].get("home_team")), {})
        h, a = p0["home_team"].get("team_name"), p0["away_team"].get("team_name")
        t0, t1 = msgs[0]["recv_ns"] / 1e9, msgs[-1]["recv_ns"] / 1e9
        ev = events(msgs); mk = find_markets(h, a, t0)
        fig, ax = plt.subplots(figsize=(14, 6)); used = 0
        for q, cid, outs in mk:
            tr = [x for x in trades(cid) if t0 - 60 <= x["timestamp"] <= t1 + 60 and x.get("outcome_index") == 0]
            if len(tr) < 3: continue
            tr.sort(key=lambda x: x["timestamp"]); used += 1
            ax.plot([x["timestamp"] for x in tr], [x["price"] for x in tr], ".-", ms=3, lw=.6, label=f"{(q or '')[:50]} ({outs[0] if outs else ''}) n={len(tr)}")
        for t, k, lab in ev: ax.axvline(t, color={"K": "tab:red", "B": "tab:orange", "T": "k"}[k], alpha={"K": .25, "B": .6, "T": .5}[k], lw=.8)
        nk = sum(e[1] == "K" for e in ev); nb = sum(e[1] == "B" for e in ev); nt = sum(e[1] == "T" for e in ev)
        ax.set_title(f"{h} vs {a} match {msgs[0]['match_id']}: {len(msgs)} msgs; red=kill ({nk}), orange=bomb ({nb}), black=round end ({nt}); markets with trades: {used}")
        ax.set_xlabel("unix time (PandaScore receive time for lines; PM trade timestamp for dots)"); ax.set_ylabel("price of outcome 0"); ax.legend(fontsize=6)
        o = os.path.join(od, f"chart_{msgs[0]['match_id']}.png"); fig.savefig(o, dpi=110); plt.close(fig); print(o, h, a, "events", nk, nb, nt, "markets", used)
        json.dump([{"t": t, "k": k, "d": d} for t, k, d in ev], open(o.replace(".png", "_events.json"), "w"))
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
