import datetime as dt, calendar_build as B
now = dt.datetime(2026, 11, 26, 5, 0, tzinfo=dt.timezone.utc)
ev = [dict(id="1", slug="cpi", title="Core CPI MoM - November 2026", end="2026-12-10T13:30:00Z", markets=[1]),
      dict(id="2", slug="fed", title="Fed Decision in December?", end="2026-12-09T23:59:00Z", markets=[1]),
      dict(id="3", slug="x", title="Bitcoin up or down", end="2026-11-27T13:30:00Z", markets=[]),
      dict(id="4", slug="past", title="Core CPI MoM - October 2026", end="2026-11-01T13:30:00Z", markets=[]),
      dict(id="5", slug="far", title="Core CPI MoM - Dec 2026", end="2027-01-14T13:30:00Z", markets=[]),
      dict(id="7", slug="gas", title="Gas prices on November 26?", end="2026-11-26T15:00:00Z", markets=[]),
      dict(id="6", slug="u", title="Netflix top show this week", end="2026-12-02T04:59:00Z", markets=[])]
cal = {c["event_id"]: c for c in B.build(ev, now)}
bad = []
if "1" not in cal or cal["1"]["R"] != "2026-12-10T13:30:00Z" or not cal["1"]["R_source"].startswith("gamma-endDate-exact") or not cal["1"]["scheduled"]: bad.append("exact CPI time")
if "2" not in cal or cal["2"]["R"] != "2026-12-09T19:00:00Z": bad.append("fed rule clock should give 14:00 ET = 19:00Z on 9 Dec, got %s" % (cal.get("2") or {}).get("R"))
if "3" in cal: bad.append("crypto must be excluded")
if "4" in cal: bad.append("past event must be excluded")
if "5" in cal: bad.append("beyond 14 days must be excluded")
if "6" not in cal or cal["6"]["R"] is not None or cal["6"]["scheduled"]: bad.append("unknown time must be listed but NOT scheduled")
if "7" in cal: bad.append("gas dropped by Nick must be excluded")
print("FAIL: " + "; ".join(bad) if bad else "PASS (6 checks)"); raise SystemExit(1 if bad else 0)
