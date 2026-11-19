"""Refresh the xtracker hourly count file used by elon_listing.py (21-day profile; the rule needs the file to end within 3 days of listing).
Fetches https://xtracker.polymarket.com/api/users/elonmusk/trackings, then /api/trackings/<id>?includeStats=true for trackings that overlap the last LOOKBACK days,
merges stats.daily (hourly buckets: date, count) into the JSON {iso_hour: count} atomically. Exit 0 = file ends within 3 h of now; exit 2 = stale; exit 3 = host unreachable.
usage: refresh_elon_hourly.py FILE [--lookback 40]"""
import argparse, datetime as dt, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elon_listing as E
X = "https://xtracker.polymarket.com"


def merge(hours, trackings_stats):
    for st in trackings_stats:
        for p in (st or {}).get("daily", []): hours[p["date"]] = p["count"]
    return hours


def refresh(path, lookback=40, getter=E.jget, now=None):
    now = now or time.time(); hours = json.load(open(path)) if os.path.exists(path) else {}
    lst = getter(f"{X}/api/users/elonmusk/trackings")["data"]; cut = now - lookback * 86400; stats = []
    for t in lst:
        end = dt.datetime.fromisoformat(t["endDate"].replace("Z", "+00:00")).timestamp()
        if end < cut: continue
        stats.append(getter(f"{X}/api/trackings/{t['id']}?includeStats=true")["data"].get("stats"))
    merge(hours, stats); tmp = path + ".tmp"; json.dump(hours, open(tmp, "w")); os.replace(tmp, path)
    last = max(dt.datetime.fromisoformat(k.replace("Z", "+00:00")).timestamp() for k in hours)
    return len(hours), (now - last) / 3600


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--lookback", type=int, default=40); a = ap.parse_args()
    try:
        n, age_h = refresh(a.file, a.lookback)
    except Exception as ex:
        print("FAIL xtracker unreachable or bad reply:", ex); sys.exit(3)
    print(f"{'PASS' if age_h <= 3 else 'FAIL'} hours={n} newest_hour_age_h={age_h:.1f}"); sys.exit(0 if age_h <= 3 else 2)
