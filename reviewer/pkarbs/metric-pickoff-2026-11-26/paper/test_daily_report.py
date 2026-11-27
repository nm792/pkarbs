import daily_report as D
fills = [dict(instrument_id="0xaa-111.POLYMARKET", side="BUY", filled_qty="571", avg_px="0.35", commissions="[1.29903 USDC]"),
         dict(instrument_id="0xbb-222.POLYMARKET", side="BUY", filled_qty="333", avg_px="0.60", commissions="[0.7992 USDC]"),
         dict(instrument_id="0xcc-333.POLYMARKET", side="BUY", filled_qty="100", avg_px="0.50", commissions="[1.0 USDC]")]
rows, tot = D.settle(fills, {"0xaa": "111", "0xbb": "999", "0xcc": None})
bad = []
if rows[0]["status"] != "WON" or abs(rows[0]["pnl"] - (571 * 0.65 - 1.29903)) > 1e-3: bad.append("winner pnl wrong")
if rows[1]["status"] != "LOST" or abs(rows[1]["pnl"] - (-333 * 0.60 - 0.7992)) > 1e-3: bad.append("loser pnl wrong")
if rows[2]["status"] != "UNRESOLVED" or rows[2]["pnl"] is not None: bad.append("unresolved must not be scored")
if tot["n"] != 2: bad.append("only resolved fills counted")
print("FAIL: " + "; ".join(bad) if bad else "PASS (4 checks)"); raise SystemExit(1 if bad else 0)
