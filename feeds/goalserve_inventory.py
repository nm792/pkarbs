#!/usr/bin/env python3
"""Goalserve stored in-play payload inventory (read-only). Answers: which bookmakers, markets, titles, fields and update
rates are in the stored bodies, and does the word 'Pinnacle' appear anywhere in them.
Input: hour files written by live/goalserve/capture.py store_payload(): gzip JSON lines {"recv_ns": int, "body": "<raw json>"}.
Body layout (vendor in-play docs): {"bm","updated","updated_ts","events":{id:{core,info,team_info,odds:{market_id:{id,name,suspend,
participants:{pid:{id,name,value_eu,suspend,handicap,is_main}}}},stats...}}}.
Usage: python3 -I feeds/goalserve_inventory.py --files '/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads/esports_20261115*.jsonl.gz' ... --out agent/status/goalserve-odds-inventory-2026-11-17.md
 (--files may be repeated; each value is a glob). Test: python3 -I feeds/test_goalserve_inventory.py
Update rate: for each event, the gap in seconds between consecutive stored payloads in which that event's odds block (market suspend,
participant value_eu or suspend) changed. Stored payloads exist only when the whole file changed, so the resolution is one poll (about 1 s).
"""
import argparse, collections, glob, gzip, json, re, statistics, sys


def rows(path):
    try:
        with gzip.open(path, "rt", errors="replace") as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    continue
    except (EOFError, OSError):
        return


def odds_sig(ev):
    s = []
    for mid in sorted((ev.get("odds") or {}), key=str):
        m = ev["odds"][mid] or {}
        parts = m.get("participants") or {}
        s.append((str(mid), m.get("suspend"), tuple((str(pid), p.get("value_eu"), p.get("suspend"), p.get("handicap"))
                                                      for pid, p in sorted(parts.items(), key=lambda x: str(x[0])) if isinstance(p, dict))))
    return tuple(s)


def pct(x, q):
    x = sorted(x)
    return x[min(len(x) - 1, int(q * len(x)))] if x else None


def scan(files):
    inv = {"files": 0, "rows": 0, "bm": collections.Counter(), "pinnacle_rows": 0, "pinnacle_examples": [],
           "titles": collections.Counter(), "markets": collections.defaultdict(collections.Counter),
           "participants": collections.defaultdict(collections.Counter), "event_keys": collections.Counter(),
           "info_keys": collections.Counter(), "stats_keys": collections.Counter(), "gaps": [], "events": set(),
           "first_ns": None, "last_ns": None}
    last_sig, last_t = {}, {}
    for p in files:
        inv["files"] += 1
        for r in rows(p):
            body = r.get("body")
            if not isinstance(body, str):
                continue
            inv["rows"] += 1
            t = r.get("recv_ns")
            if t is not None:
                inv["first_ns"] = t if inv["first_ns"] is None else min(inv["first_ns"], t)
                inv["last_ns"] = t if inv["last_ns"] is None else max(inv["last_ns"], t)
            if re.search("pinnacle", body, re.I):
                inv["pinnacle_rows"] += 1
                if len(inv["pinnacle_examples"]) < 3:
                    m = re.search("pinnacle", body, re.I)
                    inv["pinnacle_examples"].append(body[max(0, m.start() - 80):m.start() + 80])
            try:
                d = json.loads(body)
            except Exception:
                continue
            inv["bm"][repr(d.get("bm"))] += 1
            for eid, ev in (d.get("events") or {}).items():
                if not isinstance(ev, dict):
                    continue
                inv["events"].add(eid)
                info = ev.get("info") or {}
                title = info.get("sport") or "?"
                inv["titles"][title] += 1
                for k in ev:
                    inv["event_keys"][k] += 1
                for k in info:
                    inv["info_keys"][k] += 1
                for k in (ev.get("stats") or {}):
                    inv["stats_keys"][k] += 1
                for mid, m in (ev.get("odds") or {}).items():
                    if isinstance(m, dict):
                        inv["markets"][title][m.get("name") or "?"] += 1
                        for pid, pp in (m.get("participants") or {}).items():
                            if isinstance(pp, dict):
                                inv["participants"][title][pp.get("name") or "?"] += 1
                sig = odds_sig(ev)
                if eid in last_sig and sig != last_sig[eid] and t is not None and last_t.get(eid) is not None:
                    inv["gaps"].append((t - last_t[eid]) / 1e9)
                if eid not in last_sig or sig != last_sig[eid]:
                    last_sig[eid] = sig
                    last_t[eid] = t
    return inv


def top(c, n=25):
    return ", ".join(f"{k} ({v})" for k, v in c.most_common(n)) or "none"


def render(inv, now):
    g = inv["gaps"]
    o = [f"# Goalserve stored in-play payload inventory, read-only, {now:%d %B %Y %H:%MZ}", "",
         f"- files read: {inv['files']}; stored payload rows: {inv['rows']}; distinct events: {len(inv['events'])}",
         f"- first/last recv_ns: {inv['first_ns']} / {inv['last_ns']}",
         "", "## Bookmaker identifiers", f"- top-level `bm` values (count of rows): {top(inv['bm'])}",
         f"- rows whose raw body contains the string 'pinnacle' (any case): {inv['pinnacle_rows']}"]
    for e in inv["pinnacle_examples"]:
        o.append(f"  - example context: `{e}`")
    o += ["", "## Titles (info.sport) by event-appearances", f"- {top(inv['titles'])}", "", "## Markets by title (name: appearances)"]
    for t, c in sorted(inv["markets"].items()):
        o.append(f"- {t}: {top(c, 40)}")
    o += ["", "## Participant names by title (name: appearances)"]
    for t, c in sorted(inv["participants"].items()):
        o.append(f"- {t}: {top(c, 30)}")
    o += ["", "## Update rate of the odds block per event (seconds between consecutive changes)",
          f"- n changes: {len(g)}; median {statistics.median(g):.2f} s; p90 {pct(g, .9):.2f} s; p99 {pct(g, .99):.2f} s" if g else "- no changes seen",
          "", "## Field names present",
          f"- event keys: {top(inv['event_keys'], 40)}", f"- info keys: {top(inv['info_keys'], 40)}",
          f"- stats keys: {top(inv['stats_keys'], 40)}", "",
          f"PINNACLE in stored in-play bodies: {'yes (' + str(inv['pinnacle_rows']) + ' rows)' if inv['pinnacle_rows'] else 'no (0 rows)'}"]
    return "\n".join(o) + "\n"


def main():
    import datetime
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="append", required=True, help="glob; repeatable")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    files = sorted({f for g in a.files for f in glob.glob(g)})
    if not files:
        raise SystemExit("no files matched")
    inv = scan(files)
    text = render(inv, datetime.datetime.now(datetime.timezone.utc))
    open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
