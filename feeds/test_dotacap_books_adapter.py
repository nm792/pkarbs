import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from dotacap_books_adapter import convert
r = convert({"recv_ms": 1, "token": "T", "bid": 0.61, "ask": 0.62})
assert r == {"asset": "T", "recv_ms": 1, "bids": [{"price": 0.61}], "asks": [{"price": 0.62}]}
assert convert({"recv_ms": 1, "token": "T", "bid": None, "ask": 0.62}) is None   # empty side dropped, nothing inferred
assert convert({"recv_ms": 1, "bid": 0.5, "ask": 0.6}) is None                    # no token -> dropped
# mid equals what ps_lead_test computes
b = [float(x["price"]) for x in r["bids"]]; s = [float(x["price"]) for x in r["asks"]]
assert abs((max(b) + min(s)) / 2 - 0.615) < 1e-9
print("ALL PASS")
