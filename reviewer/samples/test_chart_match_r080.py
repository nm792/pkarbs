import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_match as cm
F = []
def chk(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: F.append(n)
C = "0xabc"
good = lambda u: {"data": [{"condition_id": C, "price": 0.5}, {"condition_id": C, "price": 0.6}], "pagination": {"has_more": False}}
chk("rows of the requested market pass", len(cm.trades_for(C, good)) == 2)
other = lambda u: {"data": [{"condition_id": C}, {"condition_id": "0xOTHER"}], "pagination": {"has_more": False}}
try: cm.trades_for(C, other); ok = False
except SystemExit as e: ok = "another market" in str(e)
chk("PLANTED wrong-param response (other market's rows) is REFUSED", ok)
nokey = lambda u: {"data": [{"price": 0.5}], "pagination": {"has_more": False}}
try: cm.trades_for(C, nokey); ok = False
except SystemExit: ok = True
chk("rows without any condition id are REFUSED", ok)
seen = []
cm.trades_for(C, lambda u: (seen.append(u), good(u))[1])
chk("request uses condition= (not markets=/condition_ids=)", "v2/trades?condition=%s" % C in seen[0] and "markets=" not in seen[0])
print("ALL PASS" if not F else "FAILED: " + "; ".join(F)); sys.exit(1 if F else 0)
