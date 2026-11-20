"""Self test for coverage_matrix.py. FEEDS_DIR=<feeds> python3 -I test_coverage_matrix.py -> ends ALL PASS."""
import gzip, json, os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); F = []
def chk(n, c): print(("PASS " if c else "FAIL ") + n); (F.append(n) if not c else None)
def pt(n, v): return {"name": n, "value_eu": str(v), "suspend": 0}
def row(h, a, name="To Win"): return json.dumps({"recv_ns": 1, "body": json.dumps({"events": {"1": {"team_info": {"home": {"name": h}, "away": {"name": a}}, "odds": {"9": {"name": name, "participants": {"0": pt(h, 2), "1": pt(a, 2)}}}}}})})
with tempfile.TemporaryDirectory() as t:
    g = os.path.join(t, "gs"); os.makedirs(g)
    with gzip.open(os.path.join(g, "tennis_2026112000.jsonl.gz"), "wt") as f:
        for h, a in (("alpha", "beta"), ("gamma", "delta"), ("eps", "zeta")):
            f.write(row(h, a) + "\n")
        f.write(row("only", "other", "Set 1 Winner") + "\n")      # not a winner market: must not count
    p1 = os.path.join(t, "pm1"); os.makedirs(p1)
    with open(os.path.join(p1, "markets.jsonl"), "w") as f:
        f.write(json.dumps({"cond": "c1", "q": "alpha vs beta", "smt": "moneyline", "outcomes": ["alpha", "beta"], "tokens": ["111", "222"]}) + "\n")
        f.write(json.dumps({"cond": "c2", "q": "gamma vs delta", "smt": "moneyline", "outcomes": ["gamma", "delta"], "tokens": ["333", "444"]}) + "\n")
        f.write(json.dumps({"cond": "c3", "q": "gamma vs delta", "smt": "moneyline", "outcomes": ["gamma", "delta"], "tokens": ["555", "666"]}) + "\n")   # rematch: ambiguous, excluded
    with open(os.path.join(p1, "books.jsonl"), "w") as f:
        for tk in ("111", "999"):
            f.write(json.dumps({"asset": tk, "recv_ms": 1, "bids": [], "asks": []}) + "\n")
    out = os.path.join(t, "o.json")
    p = subprocess.run([sys.executable, "-I", os.path.join(H, "coverage_matrix.py"), "--pm-dir", "pm1=" + p1, "--gs-dir", "tennis=" + g, "--out", out, "--every", "1"], capture_output=True, text=True)
    if p.returncode: print(p.stderr[-1200:])
    r = json.load(open(out))["tennis"] if not p.returncode else {}
    b = r.get("by_recorder", {}).get("pm1", {})
    chk("3 winner matches counted (set market ignored)", r.get("goalserve_matches_24h") == 3)
    chk("only the unique PM market matches (rematch and no-market excluded)", b.get("matches_with_unique_pm_market") == 1)
    chk("match rate 33.3%", abs((b.get("match_rate_pct") or 0) - 100 / 3) < 1e-6)
    chk("tokens needed 2, with book rows 1 (token 222 has none)", b.get("tokens_needed") == 2 and b.get("tokens_with_book_rows_in_tail") == 1)
print("ALL PASS" if not F else "FAILED: " + ", ".join(F)); sys.exit(1 if F else 0)
