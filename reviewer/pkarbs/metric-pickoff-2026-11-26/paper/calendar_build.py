"""Build the rolling release calendar from OPEN Polymarket events (Gamma). Offline function + CLI. Each entry says where its release time came from.
R rules, in order: (1) event endDate with a non-placeholder time of day (placeholders: 00:00, 04:59, 05:59, 12:00, 23:59, 03:59) -> 'gamma-endDate-exact'; (2) family clock rule from release_sources
applied to the endDate date -> 'rule-clock (verify)'; (3) otherwise 'UNKNOWN' and the entry is listed but NOT scheduled. Weather, crypto, sports are excluded."""
import json, re, sys, datetime as dt
from zoneinfo import ZoneInfo
from families import classify
import release_sources as RS

PLACEHOLDER = {"00:00", "04:59", "05:59", "12:00", "23:59", "03:59", "11:59"}
SKIP = re.compile(r"\b(nba|nfl|nhl|mlb|ufc|vs\.?|premier league|champions league|f1|tennis|golf|ncaa|soccer|bitcoin|btc|ethereum|solana|xrp|temperature|weather|up or down)\b", re.I)
CLOCK = {"fed_decision": ("America/New_York", 14, 0), "cpi_inflation": ("America/New_York", 8, 30), "jobs_unemp": ("America/New_York", 8, 30), "gdp": ("America/New_York", 8, 30)}
# families with a numeric lookup the strategy can run (value -> every token). Others are listed for the calendar but need a parser before they trade.
TRADEABLE = {"cpi_inflation", "jobs_unemp", "gdp", "eggs_prices", "fed_decision", "ecb_boj_boe_bor", "earnings_beat", "box_office_opening"}


def entry(e, now):
    f = classify(e.get("title")) or "other"
    title = e.get("title") or ""
    if SKIP.search(title) or re.search(r"\bgas\b", title, re.I):      # gas dropped by Nick 22 Nov (R-026)
        return None
    end = e.get("end") or e.get("endDate")
    if not end:
        return None
    t = dt.datetime.fromisoformat(end.replace("Z", "+00:00"))
    hhmm = t.strftime("%H:%M")
    foreign = re.search(r"brazil|canada|\buk\b|china|japan|euro|germany|india|australia|mexico|saudi|korea", title, re.I)
    if hhmm not in PLACEHOLDER:
        R, src = t, ("gamma-endDate hour-level (UNVERIFIED vs company IR time)" if f == "earnings_beat" else "gamma-endDate-exact (UNVERIFIED vs source calendar)")
    elif f in CLOCK and not foreign:
        tz, h, m = CLOCK[f]; z = ZoneInfo(tz)
        d = t.astimezone(z).date() if hhmm not in ("00:00",) else t.date()
        R, src = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=z).astimezone(dt.timezone.utc), "rule-clock (verify against source calendar)"
    else:
        R, src = None, "UNKNOWN (date only)"
    return dict(event_id=e["id"], slug=e.get("slug"), title=e.get("title"), family=f, markets=len(e.get("markets", [])), end_date=end,
                R=None if R is None else R.strftime("%Y-%m-%dT%H:%M:%SZ"), R_source=src, scheduled=(R is not None and f in TRADEABLE and R > now),
                number_source=RS.SOURCES.get(f, {}).get("url"), parse_ready=False)


def build(events, now, horizon_days=15):
    out = []
    for e in events:
        x = entry(e, now)
        if x is None:
            continue
        if x["R"] is not None:
            r = dt.datetime.fromisoformat(x["R"].replace("Z", "+00:00"))
            if not (now <= r <= now + dt.timedelta(days=horizon_days)):
                continue
        out.append(x)
    out.sort(key=lambda x: (x["R"] or "9999", x["family"]))
    return out


if __name__ == "__main__":
    ev = json.load(open(sys.argv[1])); now = dt.datetime.now(dt.timezone.utc) if len(sys.argv) < 3 else dt.datetime.fromisoformat(sys.argv[2].replace("Z", "+00:00"))
    cal = build(ev, now); json.dump(cal, open(sys.argv[3] if len(sys.argv) > 3 else "calendar.json", "w"), indent=1); print(len(cal), "entries")
