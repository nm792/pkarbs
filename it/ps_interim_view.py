#!/usr/bin/env python3
"""Interim per-match view of the PandaScore CS2 live probe (EXPLORATORY, UNCHECKED, read-only).
Usage: python3 -I ps_interim_view.py <books.jsonl> <probe1.json> [probe2.json ...]
Per match: events, rows with an onset, median lead (s; >0 = Polymarket moved AFTER the PandaScore message), share where PandaScore led, and the ask depth
of the rising team's token in the last book snapshot at or before the event (best ask size, sum of the top 3 ask levels, shares). Matches without book rows are reported as NO_BOOK_ROWS, never as zero.
Probe rows carry only the first 10 characters of a token id; the books file is matched by that prefix."""
import sys, json, re, statistics, collections
books, files = sys.argv[1], sys.argv[2:]
rows, summ = [], {}
for f in files:
    j = json.load(open(f)); summ[f] = j.get("summary"); rows += [dict(r, _file=f) for r in j.get("rows", [])]
def depth_index(path, wanted):
    """wanted: {tok10: [t_seconds...]} -> {(tok10, t): (best_ask_size, top3_size)} from the last snapshot with recv_ms <= t (within 120 s)."""
    ts = sorted({t for v in wanted.values() for t in v}); out = {}
    if not ts: return out
    lo, hi = (ts[0] - 120) * 1000, (ts[-1] + 1) * 1000; last = {}; pat = re.compile(r'"recv_ms":\s*(\d+)'); apat = re.compile(r'"(?:asset|tk)":\s*"(\d{1,10})')
    ev = {k: sorted(v) for k, v in wanted.items()}
    for line in open(path, errors="replace"):
        m = pat.search(line)
        if not m: continue
        r = int(m.group(1))
        if r < lo: continue
        a = apat.search(line)
        if not a or a.group(1) not in ev: continue
        try: d = json.loads(line)
        except Exception: continue
        asks = sorted((float(x["price"]), float(x["size"])) for x in d.get("asks", []))
        k = a.group(1)
        for t in ev[k]:
            if r <= t * 1000 + 0 and r >= (t - 120) * 1000: last[(k, t)] = (r, asks)
        if r > hi: break
    for key, (r, asks) in last.items():
        out[key] = (asks[0][1] if asks else None, round(sum(s for _, s in asks[:3]), 2) if asks else None)
    return out
def tok_prefix(tok):  # probe stored tok[:10] of the decimal id; the books file holds the full id
    return tok[:10]
by = collections.defaultdict(list)
for r in rows: by[(r.get("match"), r.get("series"))].append(r)
wanted = collections.defaultdict(list)
for r in rows:
    if r.get("direction") == 1 and r.get("token"): wanted[tok_prefix(r["token"])].append(r["t"])
D = depth_index(books, wanted) if rows else {}
print("EXPLORATORY / INTERIM / UNCHECKED. books=%s probes=%s" % (books, ",".join(files)))
print("match | series | events | with_onset | median_lead_s | share_PS_led | ask_best_sz(median) | ask_top3_sz(median)")
tot = []
for (mid, ser), rs in sorted(by.items(), key=lambda kv: str(kv[0])):
    up = [r for r in rs if r.get("direction") == 1]
    leads = [r["lead"] for r in up if r.get("lead") is not None]
    dp = [D[(tok_prefix(r["token"]), r["t"])] for r in up if (tok_prefix(r.get("token") or ""), r["t"]) in D]
    b = [x[0] for x in dp if x[0] is not None]; t3 = [x[1] for x in dp if x[1] is not None]
    med = round(statistics.median(leads), 2) if leads else None
    sh = round(sum(1 for v in leads if v > 0) / len(leads), 2) if leads else None
    print("%s | %s | %d | %d | %s | %s | %s | %s" % (mid, ser, len(up), len(leads), med, sh,
          (round(statistics.median(b), 1) if b else "NO_BOOK_ROWS"), (round(statistics.median(t3), 1) if t3 else "NO_BOOK_ROWS")))
    tot += leads
print("ALL: matches=%d series_rows=%d onsets=%d median_lead_s=%s share_PS_led=%s" % (len({k[0] for k in by}), sum(len(v) for v in by.values()), len(tot),
      round(statistics.median(tot), 2) if tot else None, round(sum(1 for v in tot if v > 0) / len(tot), 2) if tot else None))
for f, s in summ.items(): print("probe summary", f.split("/")[-1], json.dumps(s)[:900])
