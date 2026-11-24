#!/usr/bin/env python3
"""R-080 test: the trades fetch must refuse rows of other markets. Offline fake of data-api v2 that behaves like the real one: ONLY condition_id/condition/conditionId filter; any other param is silently ignored and returns other markets' trades.
usage: python3 -I feeds/test_audit_trades_param.py [MODULE_PATH]"""
import sys, os, re, json, tempfile, importlib.util
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "audit_ps_inround.py")
spec = importlib.util.spec_from_file_location("a", path); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
MINE, OTHER = "0xmine", "0xother"
def fake(url):
    q = dict(re.findall(r"[?&]([a-z_A-Z]+)=([^&]*)", url)); flt = q.get("condition_id") or q.get("condition") or q.get("conditionId")
    rows = [dict(condition_id=flt if flt else OTHER, price=.5, timestamp=1, outcome_index=0)] * 3 if flt == MINE else [dict(condition_id=OTHER, price=.4, timestamp=1, outcome_index=0)] * 3
    return dict(data=rows, next_cursor=None)
def wrong_param(url): return fake(url.replace("condition_id=", "markets="))
fails = []
def chk(n, ok, x=""):
    print(("PASS " if ok else "FAIL ") + n, x)
    if not ok: fails.append(n)
chk("condition_id request returns only the requested market", len(a.trades(MINE, tempfile.mkdtemp(), fetch=fake)) == 3)
try: a.trades(MINE, tempfile.mkdtemp(), fetch=wrong_param); ok = False
except a.WrongMarketRows as e: ok = True
chk("PLANTED wrong param ('markets=') makes the fetch FAIL", ok)
d = tempfile.mkdtemp(); json.dump([dict(condition_id=OTHER)], open(os.path.join(d, "trades_%s.json" % MINE), "w"))
try: a.trades(MINE, d, fetch=fake); ok = False
except a.WrongMarketRows: ok = True
chk("a poisoned CACHE file of another market is refused", ok)
print("ALL PASS" if not fails else "FAILED %s" % fails); sys.exit(1 if fails else 0)
