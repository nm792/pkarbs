"""Stage 1 ingestion: point-in-time store for Polymarket events and trades.

Every record written to disk carries `_fetched_at` (UTC epoch) so a later run can tell what was
knowable when. Trades are keyed by token (own-token prices only; NO is never derived from YES).
"""
import gzip, json, os, time, urllib.request, urllib.error

GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}


def http_json(url, timeout=60, tries=4):
    last = None
    for a in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
            return json.loads(b)
        except Exception as e:  # network / 5xx / 429
            last = e
            time.sleep(1 + 2 * a)
    raise RuntimeError(f"fetch failed {url}: {last}")


def slim_event(e):
    """Keep only fields the pipeline uses (full gamma events are ~28 KB each)."""
    ser = (e.get("series") or [{}])[0]
    mk = []
    for m in e.get("markets") or []:
        mk.append({k: m.get(k) for k in ("conditionId", "question", "outcomes", "outcomePrices", "clobTokenIds",
                                         "volumeNum", "endDate", "closedTime", "umaResolutionStatus", "secondsDelay")})
    return {"id": e["id"], "slug": e.get("slug"), "title": e.get("title"), "endDate": e.get("endDate"),
            "startDate": e.get("startDate"), "volume": e.get("volume"), "closedTime": e.get("closedTime"),
            "negRisk": e.get("negRisk"), "seriesSlug": e.get("seriesSlug"),
            "series": [{"slug": ser.get("slug"), "recurrence": ser.get("recurrence")}] if ser.get("slug") else [],
            "tags": [t.get("label") for t in e.get("tags") or []], "markets": mk}


def pull_events(end_min, end_max, out_path, page=100, max_pages=2000):
    """Closed events with endDate in [end_min,end_max] via /events/keyset. Resumable: appends JSONL."""
    seen = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            try: seen.add(json.loads(l)["id"])
            except Exception: pass
    cur, n_new = None, 0
    with open(out_path, "a") as f:
        for _ in range(max_pages):
            u = f"{GAMMA}/events/keyset?closed=true&limit={page}&end_date_min={end_min}&end_date_max={end_max}"
            if cur: u += f"&after_cursor={cur}"
            d = http_json(u)
            for e in d.get("events", []):
                if e["id"] in seen: continue
                seen.add(e["id"]); e = slim_event(e); e["_fetched_at"] = int(time.time())
                f.write(json.dumps(e) + "\n"); n_new += 1
            cur = d.get("next_cursor")
            if not cur or not d.get("events"): break
    return n_new


def load_events(path):
    return [json.loads(l) for l in open(path)]


def check_condition(rows, condition_id):
    """/v2/trades silently ignores unknown query params and then returns OTHER markets' trades (R-080): every returned row must carry the requested condition_id."""
    bad = [x.get("condition_id") for x in rows if (x.get("condition_id") or "").lower() != condition_id.lower()]
    if bad: raise RuntimeError(f"/v2/trades returned {len(bad)} rows for other conditions (first {bad[0]}) when {condition_id} was requested")


def pull_trades(condition_id, max_pages=40):
    """All trades for a market, paged by cursor. Rows: (ts, side, token_id, price, size, outcome_index)."""
    out, cur = [], None
    for _ in range(max_pages):
        u = f"{DATA}/v2/trades?condition={condition_id}&limit=500" + (f"&cursor={cur}" if cur else "")
        d = http_json(u)
        check_condition(d["data"], condition_id)
        out += [(x["timestamp"], x["side"], x["token_id"], x["price"], x["size"], x["outcome_index"]) for x in d["data"]]
        p = d.get("pagination", {})
        if not p.get("has_more") or not p.get("next_cursor"): break
        cur = p["next_cursor"]
    else:
        return out, True  # truncated
    return out, False


def pull_series(slug, out_path, page=100, max_pages=200):
    """All closed events of one gamma series (series_slug filter), full history. Resumable, de-duplicated."""
    seen = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            try: seen.add(json.loads(l)["id"])
            except Exception: pass
    cur, n_new = None, 0
    with open(out_path, "a") as f:
        for _ in range(max_pages):
            u = f"{GAMMA}/events/keyset?closed=true&limit={page}&series_slug={slug}"
            if cur: u += f"&after_cursor={cur}"
            d = http_json(u)
            for e in d.get("events", []):
                if e["id"] in seen: continue
                seen.add(e["id"]); e = slim_event(e); e["_fetched_at"] = int(time.time())
                f.write(json.dumps(e) + "\n"); n_new += 1
            cur = d.get("next_cursor")
            if not cur or not d.get("events"): break
    return n_new
