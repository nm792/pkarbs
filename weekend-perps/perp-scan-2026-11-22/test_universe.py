#!/usr/bin/env python3
"""Can-fail tests for universe.family_of (no network)."""
from universe import family_of

fails = []
def check(name, got, want):
    ok = got == want
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  got %r want %r" % (got, want)))
    if not ok: fails.append(name)

check("spx open", family_of("spx-opens-up-or-down-on-november-23-2026"), ("OPEN", "spx"))
check("spy open", family_of("spy-opens-up-or-down-on-november-24-2026"), ("OPEN", "spy"))
check("wti monthly touch", family_of("what-price-will-wti-hit-in-november-2026"), ("TOUCH-OIL", "wti"))
check("gold monthly touch", family_of("what-price-will-xauusd-hit-in-november-2026"), ("TOUCH-METALS", "xauusd"))
check("nvda weekly touch", family_of("will-nvda-hit-week-of-november-23-2026"), ("TOUCH-STOCK", "nvda"))
check("spx dec touch", family_of("spx-hit-dec-2026"), ("TOUCH-INDEX", "spx"))
check("nvda close above", family_of("nvda-close-above-on-november-23-2026"), ("CLOSE-STOCK", "nvda"))
check("spy closes above", family_of("spy-closes-above-on-november-23-2026"), ("CLOSE-INDEX", "spy"))
check("spy up or down", family_of("spy-up-or-down-on-november-23-2026"), ("CLOSE-INDEX", "spy"))
check("hype touch (Binance futures source)", family_of("what-price-will-hyperliquid-hit-in-november-2026"), ("HL-BINANCE-FUT", "hype"))
check("hip3 oi", family_of("what-will-hyperliquid-hip-3-open-interest-reach-2026"), ("HIP3-OI", None))
# out of scope / must NOT match
check("bitcoin touch is out of scope here (spot-referenced, MFW)", family_of("what-price-will-bitcoin-hit-in-november-2026"), None)
check("unknown ticker weekly is out of scope", family_of("will-zzzz-hit-week-of-november-23-2026"), None)
check("random event is None", family_of("epl-2027-champion-20260701200428749"), None)
check("hype updown 5m is out of scope (Chainlink TWAP, MFW)", family_of("hype-updown-5m-1795412400"), None)
print("ALL PASS" if not fails else "FAILED: %s" % fails)
raise SystemExit(1 if fails else 0)
