"""Family definition and the frequency / volume screen (criteria 1 and 2)."""
import json, re, statistics, datetime as dt
from collections import defaultdict

_MONTHS = "january february march april may june july august september october november december jan feb mar apr jun jul aug sep sept oct nov dec".split()


def template_key(title):
    t = re.sub(r"[0-9][0-9,.:%$]*", "#", (title or "").lower())
    t = re.sub(r"\b(" + "|".join(_MONTHS) + r")\b", "M", t)
    t = re.sub(r"[^a-z# ]", " ", t)
    toks = ["X" if len(w) <= 2 and w != "#" else w for w in t.split()]  # state codes etc. collapse to X
    return "tpl:" + " ".join(toks[:5])


# Standing exclusions (Nick 19 Nov 03:48Z and project memory): sports and esports (faster-feed trials cover them),
# crypto (another project, Nick 19 Nov 03:48Z), weather markets, PM 5-minute up/down (MFW's). Crypto mirror-pair is a strategy, not a series filter.
EXCLUDE_TAGS = {t.lower() for t in (
    "Sports", "Games", "Esports", "Soccer", "Tennis", "Table Tennis", "Basketball", "Hockey", "Cricket", "Baseball",
    "Football", "NFL", "NBA", "NHL", "MLB", "MLS", "NCAA", "CFB (All)", "UFC", "MMA", "Boxing", "Golf", "Darts",
    "Rugby", "AFL", "F1", "Formula 1", "Chess", "counter strike 2", "Dota 2", "League of Legends", "Valorant",
    "Crypto", "Crypto Prices", "Bitcoin", "Ethereum", "Solana", "XRP", "Ripple", "BNB", "Dogecoin", "Zcash", "hype", "Weather", "Daily Temperature", "Highest temperature", "Lowest temperature", "Temperature", "Setka", "WTT")}
EXCLUDE_SLUG_SUFFIX = ("-up-or-down-5m",)
import re as _re
CRYPTO_SLUG = _re.compile(r"(^|[-_])(btc|bitcoin|eth|ethereum|sol|solana|xrp|bnb|doge|dogecoin|hype|zec|crypto|ada|avax|link|ltc|sui|pepe|megaeth)([-_]|$)")


def excluded_reason(ev):
    for t in ev.get("tags") or []:
        if (t or "").lower() in EXCLUDE_TAGS: return "tag:" + t
    slug = ((ev.get("series") or [{}])[0].get("slug") or ev.get("seriesSlug") or "")
    if slug.endswith(EXCLUDE_SLUG_SUFFIX): return "5m:" + slug
    if CRYPTO_SLUG.search(slug): return "crypto:" + slug
    return None


def family_key(ev):
    s = ev.get("series") or []
    if s and s[0].get("slug"): return "series:" + s[0]["slug"]
    if ev.get("seriesSlug"): return "series:" + ev["seriesSlug"]
    return template_key(ev.get("title"))


def _ts(s):
    if not s: return None
    try: return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception: return None


def screen(events, window_days, min_events=5):
    """Per family: events/day, active-day share, median and total volume, recurrence label."""
    fam = defaultdict(list)
    for e in events:
        end = _ts(e.get("endDate"))
        if end is None: continue
        fam[family_key(e)].append((end, float(e.get("volume") or 0), e))
    rows = []
    for k, v in fam.items():
        if len(v) < min_events: continue
        days = {dt.datetime.fromtimestamp(x[0], dt.timezone.utc).date() for x in v}
        vols = [x[1] for x in v]
        rec = ""
        s = v[0][2].get("series") or []
        if s: rec = s[0].get("recurrence", "")
        rows.append(dict(family=k, n_events=len(v), events_per_day=len(v) / window_days,
                         active_day_share=len(days) / window_days, median_vol=statistics.median(vols),
                         total_vol=sum(vols), recurrence=rec))
    return rows
