"""Tests for pickoff_core. Every check can fail. Run: python3 test_pickoff_core.py"""
import pickoff_core as C
bad = []; N = [0]
def ck(c, m):
    N[0] += 1
    if not c: bad.append(m)
P = C.parse_predicate; E = C.evaluate
# --- parsing real Polymarket question shapes (from Gamma, 26 Nov)
ck(P("Will the October 2026 unemployment rate be 4.1%?") == {"kind": "eq", "x": 4.1}, "eq unemployment")
ck(P("Unemployment rate over 4.3% in October?") == {"kind": "gt", "x": 4.3}, "over")
ck(P("Will Core CPI MoM be 0.3% or less in August?") == {"kind": "le", "x": 0.3}, "or less")
ck(P("Will Core CPI MoM be 0.3% or more in August?") == {"kind": "ge", "x": 0.3}, "or more")
ck(P("Will Core CPI MoM be 0.3% in August?") == {"kind": "eq", "x": 0.3}, "cpi eq")
ck(P("US adds between 50k and 100k jobs in August?") == {"kind": "between", "lo": 50000.0, "hi": 100000.0}, "between k")
ck(P("US adds less than 50k jobs in August?") == {"kind": "lt", "x": 50000.0}, "less than k")
ck(P("US adds more than 150k jobs in August?") == {"kind": "gt", "x": 150000.0}, "more than k")
ck(P("Will a dozen eggs be above $3.50 in July?") == {"kind": "gt", "x": 3.5}, "eggs above")
ck(P("Will a dozen eggs be below $3.50 in July?") == {"kind": "lt", "x": 3.5}, "eggs below")
ck(P("Will the total number of TSA passengers for April 5 be between 2,000,000 and 2,100,000?") == {"kind": "between", "lo": 2e6, "hi": 2.1e6}, "tsa between commas")
ck(P("Will Brazil's Q3 2026 GDP growth rate (QoQ) be less than -0.5%?") == {"kind": "lt", "x": -0.5}, "negative number")
ck(P("Fed decreases interest rates by 25 bps after December 2026 meeting?") == {"kind": "eq", "x": -25.0}, "fed eq")
ck(P("50+ bps decrease in ECB interest rates after March 2026 meeting?") == {"kind": "le", "x": -50.0}, "ecb 50+")
ck(P("gibberish with no number") is None, "unparsed must be None")
# --- evaluation: ladder + bracket all decided by ONE number
ck(E(P("Will Core CPI MoM be 0.3% or less in August?"), 0.3) is True, "le at edge inclusive true")
ck(E(P("Will Core CPI MoM be 0.3% or more in August?"), 0.3) is True, "ge at edge inclusive true (both true at once: ladder)")
ck(E(P("Will Core CPI MoM be 0.3% in August?"), 0.3) is True, "eq true")
ck(E(P("Will Core CPI MoM be 0.2% in August?"), 0.3) is False, "eq false -> NO token wins")
ck(E(P("Unemployment rate over 4.3% in October?"), 4.3) is False, "strict over at edge is False")
ck(E(P("US adds between 50k and 100k jobs in August?"), 100000) is None, "between edge ambiguous -> refuse")
ck(E(P("US adds between 50k and 100k jobs in August?"), 75000) is True, "between inside")
ck(E(None, 1.0) is None, "None predicate -> None")
# --- the lookup: both sides, whole event, one batch
mk = []
for i, q in enumerate(["Will Core CPI MoM be 0.1% in Oct?", "Will Core CPI MoM be 0.2% in Oct?", "Will Core CPI MoM be 0.3% in Oct?", "Will Core CPI MoM be 0.4% in Oct?",
                       "Will Core CPI MoM be 0.2% or less in Oct?", "Will Core CPI MoM be 0.3% or more in Oct?", "garbled market?"]):
    mk.append({"cond": "c%d" % i, "q": q, "tokens": ["y%d" % i, "n%d" % i], "outcomes": ["Yes", "No"]})
H = C.HeldOrders(mk)
# before the release every token (YES and NO of every market) has a held order once it has a stale-looking ask
for i in range(7):
    H.reprice("y%d" % i, 0.50, 1000, 1); H.reprice("n%d" % i, 0.50, 1000, 1)
ck(sum(1 for v in H.held().values() if v) == 14, "held order for BOTH tokens of ALL 7 markets")
# the number arrives: 0.3. Truth: c0 F, c1 F, c2 T, c3 F, c4 (<=0.2) F, c5 (>=0.3) T, c6 None
tt = C.truth_table(mk, 0.3)
ck(tt == {"c0": False, "c1": False, "c2": True, "c3": False, "c4": False, "c5": True, "c6": None}, "truth table wrong: %s" % tt)
# planted stale asks: winning tokens stale, others already repriced
H.reprice("n0", 0.74, 500, 2); H.reprice("n1", 0.80, 500, 2); H.reprice("y2", 0.35, 500, 2); H.reprice("n3", 0.97, 500, 2)
H.reprice("n4", 0.60, 500, 2); H.reprice("y5", 0.40, 500, 2); H.reprice("y6", 0.30, 500, 2)
orders, sk = C.fire(H, tt)
by = {o["cond"]: o for o in orders}
ck(set(by) == {"c0", "c1", "c2", "c4", "c5"}, "fired set wrong: %s" % sorted(by))
ck(by["c0"]["side"] == "NO" and by["c0"]["token"] == "n0", "losing bracket must fire NO token")
ck(by["c2"]["side"] == "YES" and by["c2"]["token"] == "y2", "winning bracket must fire YES token")
ck(by["c4"]["side"] == "NO" and by["c5"]["side"] == "YES", "ladder: NO on false threshold and YES on true threshold at once")
ck(all(o["limit"] == 0.95 for o in orders), "limit must be 0.95")
ck(by["c2"]["shares"] == int(200 / 0.35), "size = $200 / own ask")
reasons = dict(sk)
ck("c3" in reasons and "already repriced" in reasons["c3"], "NO ask 0.97 must be rejected as repriced")
ck("c6" in reasons and "ambiguous" in reasons["c6"], "unparsed market must be skipped, never guessed")
ck("y6" not in {o["token"] for o in orders}, "unparsed market's token must never be bought")
# pre-release rejection: with the stale-quote guard, an ask not refreshed recently is refused
orders2, sk2 = C.fire(H, tt, stale_ms=1000, now_ms=10_000)
ck(orders2 == [], "all quotes older than 1 s at t=10 s must be refused")
# daily cap: prefers the largest edge, never exceeds $2,000
orders3, sk3 = C.fire(H, tt, day_spent=1650.0)
ck(sum(o["stake"] for o in orders3) <= 350.0 + 1e-9 and len(orders3) < len(orders), "cap must drop orders")
ck(orders3 and orders3[0]["cond"] in ("c2", "c5"), "cap keeps highest edge first (YES at 0.35/0.40)")
# batching
ck([len(b) for b in C.batches(list(range(31)))] == [15, 15, 1], "batches of <= 15")
# mutation proof: if the NO side were dropped the test above must fail (shows the check can fail)
ck(len([o for o in orders if o["side"] == "NO"]) == 3, "NO side must be present (c0, c1, c4)")
print("FAIL: " + "; ".join(bad) if bad else "PASS (%d checks, each able to fail)" % N[0])
raise SystemExit(1 if bad else 0)
