"""Release-window recorder: writes JSONL of (a) Polymarket own-token books for every bracket of a series' open event, (b) the external release source
(AAA page for gas; Yahoo SPX for the S&P open) at the same instants, so that repricing lag vs the release and the depth of stale asks can be measured.
Never places orders. Usage: python3 recorder.py --out DIR [--jobs gas,spxopen] [--interval 20]."""
import argparse, datetime as dt, json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoneinfo import ZoneInfo
import books as B
NY = ZoneInfo("America/New_York")


def parse_aaa(html):
    """Regular 'Current Avg.' and 'Yesterday Avg.' plus 'Price as of' date from gasprices.aaa.com HTML."""
    out = {}
    m = re.search(r"Price as of\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})", html)
    out["price_as_of"] = m.group(1) if m else None
    for key, lab in (("current", "Current Avg."), ("yesterday", "Yesterday Avg.")):
        m = re.search(re.escape(lab) + r"\s*</?[^>]*>\s*(?:<[^>]*>\s*)*\$?\s*([0-9]\.[0-9]{3})", html)
        out[key] = float(m.group(1)) if m else None
    return out


def fetch_aaa():
    r = urllib.request.urlopen(urllib.request.Request("https://gasprices.aaa.com/", headers={"User-Agent": "Mozilla/5.0"}), timeout=15)
    h = r.read().decode("utf-8", "ignore"); d = parse_aaa(h); d["http_date"] = r.headers.get("Date"); return d


def yahoo_last(sym):
    d = B.P.http_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=1m&includePrePost=true", timeout=15, tries=1)
    r = d["chart"]["result"][0]; ts = r["timestamp"]; cl = r["indicators"]["quote"][0]["close"]
    i = max(k for k, c in enumerate(cl) if c is not None); return dict(bar_start=ts[i], last=cl[i], prev_close=r["meta"].get("chartPreviousClose"))


def in_window(job, now):
    if job == "gas": return 2.5 <= now.hour + now.minute / 60 <= 9.5            # UTC; observed conversion 03:15-08:23Z
    if job == "spxopen":
        n = now.astimezone(NY); return n.weekday() < 5 and (9 * 60 + 20) <= n.hour * 60 + n.minute <= (9 * 60 + 50)
    return False


def tick(job, out_dir, now):
    rec = dict(job=job, t=time.time(), utc=now.isoformat())
    slug = {"gas": "us-gas-price-daily", "spxopen": "spx-open-daily-up-or-down"}[job]
    try:
        evs = B.open_event(slug)
        today = [e for e in evs if (e.get("endDate") or "")[:10] == now.astimezone(NY).date().isoformat() or (e.get("endDate") or "")[:10] == now.date().isoformat()]
        e = today[0] if today else None
        rec["event"] = e["slug"] if e else None; rec["books"] = []
        if e:
            for m in e["markets"]:
                toks = json.loads(m["clobTokenIds"]) if isinstance(m["clobTokenIds"], str) else m["clobTokenIds"]
                outs = json.loads(m["outcomes"]) if isinstance(m["outcomes"], str) else m["outcomes"]
                for tok, o in zip(toks, outs):
                    if o in ("Yes", "Up", "Down", "No"):
                        s = B.snapshot(tok); s["q"] = m["question"][-60:]; s["outcome"] = o; rec["books"].append(s)
    except Exception as ex:
        rec["pm_error"] = str(ex)[:200]
    try:
        rec["ext"] = fetch_aaa() if job == "gas" else yahoo_last("^GSPC")
    except Exception as ex:
        rec["ext_error"] = str(ex)[:200]
    with open(os.path.join(out_dir, f"{job}_{now.strftime('%Y%m%d')}.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--jobs", default="gas,spxopen"); ap.add_argument("--interval", type=int, default=20)
    ap.add_argument("--max-hours", type=float, default=30.0); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    t_end = time.time() + a.max_hours * 3600; last = {}
    while time.time() < t_end:
        now = dt.datetime.now(dt.timezone.utc)
        for j in a.jobs.split(","):
            if in_window(j, now) and time.time() - last.get(j, 0) >= a.interval:
                tick(j, a.out, now); last[j] = time.time()
        time.sleep(2)
