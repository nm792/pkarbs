"""Kills-only event rule (kills_only.py) with order-ack latency and the ack-timeout guard (tennis PR #133 idea).
Ack draws = 30 measured Polymarket CLOB submit->accepted times from Nautilus runs on our server
(agent/outbox/nautilus-order-latency-2026-11-05.csv: median 0.21 s, p90 1.28 s, 30% > 0.3 s).
Per event: visible at st + 2 + U(0,20) s (WS lag), then the order rests from visible + ack.
  no guard : rests from visible + ack (late acks just rest late)
  guard    : ack > 0.3 s -> cancel (0.13 s) and drop the event
  guard+re : ack > 0.3 s -> cancel, re-place at next 1 s book tick with a new ack draw (what lol_pilot does), up to 5 tries
Approximation: the 30 s window starts at the rest time (ends <= ~5 s later than in kills_only)."""
import os, sys, csv, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kills_only as K
ROOT = os.path.abspath(os.path.join(HERE, '../../../..'))
ACK = np.array([float(r['submit_to_accepted_s']) for r in csv.DictReader(open(os.path.join(ROOT, 'agent/outbox/nautilus-order-latency-2026-11-05.csv'))) if r['submit_to_accepted_s']])
A = [np.random.default_rng(1)]   # separate stream for acks so WS lags match kills_only draw for draw
def ack(): return A[0].choice(ACK)
def ws(r): return 2 + r.uniform(0, 20)
def noguard(r): return ws(r) + ack()
def guard(r, T=0.3):
    v = ws(r); a = ack()
    return v + a if a <= T else 1e9
def guard_re(r, T=0.3):
    t = ws(r)
    for _ in range(5):
        a = ack()
        if a <= T: return t + a
        t += a + 0.13 + 1.0
    return 1e9
if __name__ == '__main__':
    print(f"ack sample n={len(ACK)} median {np.median(ACK):.3f} p90 {np.percentile(ACK,90):.3f} share>0.3 {np.mean(ACK>0.3):.2f}")
    print(f"{'set / variant':34}{'ser':>5}{'$fill':>9}{'1min%':>7}{'1min 90%':>14}{'res%':>7}{'res$':>8}{'res$ 90% (series)':>18}")
    for setname, sel in [('HOLDOUT', lambda g: g not in K.LOCK), ('all', lambda g: True)]:
        for n, f in [('WS lag, instant ack', ws), ('WS lag + ack, no guard', noguard), ('guard 0.3 s, drop', guard), ('guard 0.3 s, re-place', guard_re)]:
            A[0] = np.random.default_rng(1); K.report(f'{setname} {n}', sel, f, 30)
