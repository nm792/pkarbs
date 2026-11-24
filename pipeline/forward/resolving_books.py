"""R-036 item 1: MEASURED own-token ask depth at decision time for late-resolving series. Never places orders.
Subcommands:
  snap   --series a,b,c [--out F]          one pass over every OPEN event of those series (labels each by hours to end)
  record --series-file F --out DIR [--max-hours H]   loop: for every open event snapshot all candidate tokens at T-3h, T-1h, T-30m (+-60 s) and append JSONL
  summarize --out DIR                      depth table: per series x lead, median own-token ask $ at leader ask..+0.02 and ..+0.05, leader ask, n
Candidate tokens: YES token of bracket events, both tokens of single Up/Down markets. Leader = candidate with the highest own best bid (own book, never 1 - other).
Own-token books: asks and bids of the SAME token; YES and NO are separate books."""
import argparse, collections, datetime as dt, fcntl, gzip, json, os, statistics, sys, time, urllib.request
GAMMA = "https://gamma-api.polymarket.com"; CLOB = "https://clob.polymarket.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip", "Content-Type": "application/json"}
LEADS_H = (3.0, 1.0, 0.5); LEADS_15M = (10 / 60, 5 / 60, 2 / 60); TOL_S = 60.0; FULL = set()


def leads_for(series):
    """decision leads in hours before the event end; 15-minute contracts use T-10m / T-5m / T-2m (a 3 h lead is before the contract exists)."""
    return LEADS_15M if series.endswith("-15m") else LEADS_H


def jget(url, body=None, timeout=20):
    req = urllib.request.Request(url, data=(json.dumps(body).encode() if body is not None else None), headers=UA)
    r = urllib.request.urlopen(req, timeout=timeout); b = r.read()
    if r.headers.get("Content-Encoding") == "gzip": b = gzip.decompress(b)
    return json.loads(b)


def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def slim_book(b):
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)
    return dict(asks=asks, bids=bids)


def ask_depth_usd(asks, slack):
    """printed-book $ available (price x size) from the best ask up to best ask + slack (own token)."""
    if not asks: return 0.0
    p0 = asks[0][0]
    return float(sum(p * s for p, s in asks if p <= p0 + slack + 1e-9))


def candidates(ev):
    out = []
    for m in ev["markets"]:
        if m.get("closed") is True or m.get("acceptingOrders") is False: continue    # closed brackets have no book
        toks = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds")
        outs = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes")
        if not toks or not outs or len(toks) != 2: continue
        low = [o.lower() for o in outs]
        if set(low) == {"yes", "no"}: out.append(toks[low.index("yes")])
        else: out += list(toks)
    return out


def leader(books):
    """books: {token: slim_book}. leader = highest own best bid among tokens that have any bid (a decided market can leave the winner with bids only);
    if no token has a bid, the lowest own best ask. Returns None only when every book is empty."""
    best = None
    for t, b in books.items():
        if b["bids"] and (best is None or b["bids"][0][0] > best[1]): best = (t, b["bids"][0][0])
    if best: return best[0]
    asks = [(b["asks"][0][0], t) for t, b in books.items() if b["asks"]]
    return min(asks)[1] if asks else None


def measure(books):
    """own-token summary of the leader. book_state: two_sided / bids_only (decided winner) / asks_only. ask is None and depth 0.0 when the leader has no asks."""
    t = leader(books)
    if t is None: return None
    a = books[t]["asks"]; bd = books[t]["bids"]
    st = "two_sided" if (a and bd) else ("bids_only" if bd else "asks_only")
    return dict(token=t, bid=bd[0][0] if bd else None, ask=a[0][0] if a else None, depth02=ask_depth_usd(a, 0.02), depth05=ask_depth_usd(a, 0.05), n_levels=len(a), book_state=st)


def open_events(series):
    cur = None; out = []
    for _ in range(10):
        u = f"{GAMMA}/events/keyset?closed=false&limit=50&series_slug={series}" + (f"&after_cursor={cur}" if cur else "")
        d = jget(u); out += d.get("events", []); cur = d.get("next_cursor")
        if not cur or not d.get("events"): break
    return out


def books_for(tokens):
    got = {}
    for i in range(0, len(tokens), 50):
        for x in jget(CLOB + "/books", [{"token_id": t} for t in tokens[i:i + 50]]): got[x["asset_id"]] = slim_book(x)
    return got


def snap_event(ev, now=None, full=False):
    """full=True also stores the slim own-token ladders (asks best-first, top 20; bids best-first, top 5) of every candidate token (used for the Elon bracket series)."""
    now = now or time.time(); t0 = time.time(); bk = books_for(candidates(ev)); m = measure(bk)
    extra = dict(books={t: dict(asks=b["asks"][:20], bids=b["bids"][:5]) for t, b in bk.items()}) if full else {}
    return dict(**extra, series=ev.get("seriesSlug") or (ev.get("series") or [{}])[0].get("slug"), event=ev["id"], slug=ev.get("slug"), end=ev["endDate"],
                hours_to_end=(ts(ev["endDate"]) - now) / 3600, t=now, latency_s=time.time() - t0, n_tokens=len(bk), **(m or {}))


def due(end, lead_h, now):
    """True when now is within +-TOL_S of end - lead_h hours."""
    return abs(now - (end - lead_h * 3600)) <= TOL_S


def cmd_snap(a):
    rows = []
    for s in a.series.split(","):
        for ev in open_events(s):
            try: rows.append(snap_event(ev))
            except Exception as ex: rows.append(dict(series=s, event=ev.get("id"), error=str(ex)))
    json.dump(rows, open(a.out, "w")) if a.out else print(json.dumps(rows, indent=1)); return rows


def acquire_lock(out):
    """single-instance lock: returns the open handle, or None if another process holds it (second copy refused)."""
    os.makedirs(out, exist_ok=True); fh = open(os.path.join(out, ".lock"), "w")
    try: fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: fh.close(); return None
    fh.write(str(os.getpid())); fh.flush(); return fh


def preflight_check(expected_tokens, got_books, rows_written, min_rows):
    """R-058: tokens/books >0 and equal to expected; 60 s of real live data written. returns (ok, list of failures)."""
    f = []
    if expected_tokens <= 0: f.append("expected tokens = 0")
    if len(got_books) != expected_tokens: f.append(f"books returned {len(got_books)} != expected tokens {expected_tokens}")
    if not any(b["asks"] or b["bids"] for b in got_books.values()): f.append("no book has any level")
    if rows_written < min_rows: f.append(f"only {rows_written} live rows written (< {min_rows})")
    return (not f), f


def cmd_preflight(a):
    """Run by IT on Prime BEFORE starting the service. Any FAIL: exit 1, nothing starts. Writes 60 s of real snapshots to OUT/preflight.jsonl."""
    series = [l.strip() for l in open(a.series_file) if l.strip() and not l.startswith("#")]
    lk = acquire_lock(a.out)
    if lk is None: print("FAIL single-instance lock held by another process (a recorder is already running)"); sys.exit(1)
    evs = [ev for s in series for ev in open_events(s)]; toks = sorted({t for ev in evs for t in candidates(ev)})
    print(f"events {len(evs)} expected tokens {len(toks)} series {len(series)}")
    path = os.path.join(a.out, "preflight.jsonl"); n = 0; t_end = time.time() + a.seconds; bk = {}
    with open(path, "w") as f:
        while time.time() < t_end:
            bk = books_for(toks); f.write(json.dumps(dict(t=time.time(), n_books=len(bk), n_levels=sum(len(b["asks"]) + len(b["bids"]) for b in bk.values()))) + "\n"); f.flush(); n += 1; time.sleep(5)
    ok, fails = preflight_check(len(toks), bk, n, max(1, int(a.seconds / 5) - 2))
    print("PASS preflight" if ok else "FAIL preflight: " + "; ".join(fails)); print(f"rows {n} file {path} bytes {os.path.getsize(path)}"); lk.close(); sys.exit(0 if ok else 1)


def cmd_record(a):
    series = [l.strip() for l in open(a.series_file) if l.strip() and not l.startswith("#")]
    FULL.update(x for x in (a.full_series or "").split(",") if x)
    lock = acquire_lock(a.out)
    if lock is None: print("second copy refused: lock held"); sys.exit(1)
    os.makedirs(a.out, exist_ok=True); done = set(); t_end = time.time() + a.max_hours * 3600; ev_cache = {}; last_list = 0
    while time.time() < t_end:
        now = time.time()
        if now - last_list > 600:
            last_list = now
            for s in series:
                try: ev_cache[s] = open_events(s)
                except Exception: pass
        for s, es in ev_cache.items():
            for ev in es:
                try: end = ts(ev["endDate"])
                except Exception: continue
                for L in leads_for(s):
                    key = (ev["id"], L)
                    if key in done: continue
                    if due(end, L, now):
                        done.add(key)
                        try: r = snap_event(ev, now, full=(s in FULL)); r["lead_h"] = L
                        except Exception as ex: r = dict(series=s, event=ev["id"], lead_h=L, error=str(ex), t=now)
                        with open(f"{a.out}/resolving_books_{dt.datetime.utcfromtimestamp(now):%Y%m%d}.jsonl", "a") as f: f.write(json.dumps(r) + "\n")
        time.sleep(5)


def summarize(rows):
    by = collections.defaultdict(list)
    for r in rows:
        if "error" in r or "token" not in r: continue
        by[(r["series"], r.get("lead_h"))].append(r)
    out = []
    for (s, L), rs0 in sorted(by.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        rs = [r for r in rs0 if isinstance(r.get("ask"), (int, float))]
        if not rs: out.append(dict(series=s, lead_h=L, n=len(rs0), n_one_sided=len(rs0), ask_med=None, depth02_med=None, depth05_med=None, depth02_min=None, depth02_max=None)); continue
        out.append(dict(series=s, lead_h=L, n=len(rs), n_one_sided=len(rs0) - len(rs), ask_med=statistics.median(r["ask"] for r in rs), depth02_med=statistics.median(r["depth02"] for r in rs),
                        depth05_med=statistics.median(r["depth05"] for r in rs), depth02_min=min(r["depth02"] for r in rs), depth02_max=max(r["depth02"] for r in rs)))
    return out


def health(expected, rows):
    """expected: set of (event_id, lead_h) windows that fell due in the period; rows: JSONL records of the period.
    returns dict(expected, captured, pct, errors, own_book_ok). A capture counts only if it has a numeric ask taken from the leader token's own book."""
    # a capture counts when the row names the leader token and either has a numeric ask or is an honest one-sided (decided) book: market state, not a miss
    got = {(r.get("event"), r.get("lead_h")) for r in rows if "error" not in r and r.get("token") and (isinstance(r.get("ask"), (int, float)) or r.get("book_state") in ("bids_only", "asks_only"))}
    errs = sum(1 for r in rows if "error" in r)
    hit = len(expected & got)
    return dict(expected=len(expected), captured=hit, pct=(100.0 * hit / len(expected)) if expected else None, errors=errs, own_book_ok=all(r.get("token") for r in rows if "error" not in r),
                one_sided=sum(1 for r in rows if r.get("book_state") in ("bids_only", "asks_only")))


def cmd_health(a):
    series = [l.strip() for l in open(a.series_file) if l.strip() and not l.startswith("#")]; now = time.time(); lo = now - a.minutes * 60 - TOL_S
    exp = set()
    for s in series:
        try:
            for ev in open_events(s):
                end = ts(ev["endDate"])
                for L in leads_for(s):
                    if lo <= end - L * 3600 <= now - TOL_S: exp.add((ev["id"], L))
        except Exception as ex: print("list error", s, ex)
    rows = []
    for fn in sorted(os.listdir(a.out)):
        if fn.startswith("resolving_books_") and fn.endswith(".jsonl"):
            rows += [r for r in (json.loads(l) for l in open(os.path.join(a.out, fn))) if r.get("t", 0) >= lo]
    h = health(exp, rows); st = os.statvfs(a.out); h["disk_free_GB"] = round(st.f_bavail * st.f_frsize / 1e9, 1); h["now"] = dt.datetime.utcfromtimestamp(now).strftime("%FT%TZ")
    h["verdict"] = "PASS" if (h["pct"] is None or h["pct"] >= 99) and h["errors"] == 0 and h["own_book_ok"] else "FAIL"
    h["price_source"] = "fields ask/bid/depth02 = best own ask/bid of the leader token (field `token`) from POST /books; never 1 - other token"
    print(json.dumps(h))


def cmd_summarize(a):
    rows = []
    for fn in sorted(os.listdir(a.out)):
        if fn.startswith("resolving_books_") and fn.endswith(".jsonl"): rows += [json.loads(l) for l in open(os.path.join(a.out, fn))]
    for r in summarize(rows): print(json.dumps(r))


if __name__ == "__main__":
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("snap"); s.add_argument("--series", required=True); s.add_argument("--out")
    r = sp.add_parser("record"); r.add_argument("--series-file", required=True); r.add_argument("--out", required=True); r.add_argument("--max-hours", type=float, default=26); r.add_argument("--full-series", default="")
    pf = sp.add_parser("preflight"); pf.add_argument("--series-file", required=True); pf.add_argument("--out", required=True); pf.add_argument("--seconds", type=float, default=60)
    h = sp.add_parser("health"); h.add_argument("--series-file", required=True); h.add_argument("--out", required=True); h.add_argument("--minutes", type=float, default=15)
    u = sp.add_parser("summarize"); u.add_argument("--out", required=True)
    a = p.parse_args(); {"snap": cmd_snap, "record": cmd_record, "summarize": cmd_summarize, "health": cmd_health, "preflight": cmd_preflight}[a.cmd](a)
