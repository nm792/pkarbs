"""Family definition and the frequency / volume screen (criteria 1 and 2)."""
import json, re, statistics, datetime as dt
from collections import defaultdict

_MONTHS = "january february march april may june july august september october november december jan feb mar apr jun jul aug sep sept oct nov dec".split()


def template_key(title):
    t = re.sub(r"[0-9][0-9,.:%$]*", "#", (title or "").lower())
    t = re.sub(r"\b(" + "|".join(_MONTHS) + r")\b", "M", t)
    t = re.sub(r"[^a-z# ]", " ", t)
    return "tpl:" + " ".join(t.split()[:5])


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
