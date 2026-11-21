import datetime as dt, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paper_post as P, rule as R
D = dt.date(2026, 11, 21)
ET = P.ET
def ns(h, m, s=0, day=D): return int(dt.datetime(day.year, day.month, day.day, h, m, s, tzinfo=ET).timestamp() * 1e9)
LAB = {0: "Will the US national average gas price be less than $3.7000 on November 21?",
       1: "Will the US national average gas price be between $3.7000 and $3.7099 on November 21?",
       2: "Will the US national average gas price be between $3.7100 and $3.7199 on November 21?",
       3: "Will the US national average gas price be $3.7200+ on November 21?"}
def snap(t, asks):
    """asks: {(bucket, 'Yes'/'No'): [[p, size], ...]} ; unspecified tokens have no asks."""
    tok = {}
    for b, lab in LAB.items():
        for out in ("Yes", "No"):
            tok[f"t{b}{out}"] = dict(label=f"{lab}|{out}", best_ask=None, asks=asks.get((b, out), []), bids=[], ltp=None, book_ts=None)
    return dict(recv_ns=t, tok=tok)
def page(t, status=200, asof="11/21/26", val=3.705): return dict(recv_ns=t, status=status, price_as_of=asof, regular_current=val)
PRM = R.Params(fee_rate=0.05, bank=10000, rule_caps=(("yes_fav", .10), ("no_out", .05), ("post", .10)))
