import sys, random, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
import stops_harness as H
bad = []
# 1 checkpoints: 10, 20, 40, 60, ... then every 20, last <= 432
cps = H.checkpoints(); 
if cps[:5] != [10, 20, 40, 60, 80] or cps[-1] != 420 or any(b - a != 20 for a, b in zip(cps[2:], cps[3:])): bad.append('checkpoints ' + str(cps[:6]) + str(cps[-2:]))
# 2 blind: strong edge but fewer than 10 games -> no verdict
v = H.run_study([100.0] * 9, [1.0] * 9)[0]
if v != 'not enough games': bad.append('verdict before game 10: ' + v)
# 3 always-valid coverage under the null: the CS (checked at EVERY game to 432, with the TRUE sigma) must exclude 0 in <= 5% of null streams (any-time validity)
rng = random.Random(5); viol = 0; N = 1000; sg = 50.0
for _ in range(N):
    s = 0.0; hit = False
    for n in range(1, 433):
        s += rng.gauss(0, sg)
        if abs(s / n) > H.cs_radius(n, sg): hit = True; break
    viol += hit
if viol / N > 0.05: bad.append('CS null violation rate %.3f > 0.05' % (viol / N))
# 4 positive control: mean +30, sd 50, sigma from baseline sd 35.8 (x1.5): SUCCESS reported, never before game 10
rng = random.Random(6); wins = 0
for _ in range(100):
    d = [rng.gauss(30, 50) for _ in range(432)]; b = [rng.gauss(0, 35.8) for _ in range(432)]
    r = H.run_study(d, b); wins += r[0] == 'SUCCESS' and r[1] >= 10
if wins < 95: bad.append('positive control detected only %d/100' % wins)
# 5 negative control: mean -30 -> FUTILITY
rng = random.Random(7); fut = sum(H.run_study([rng.gauss(-30, 50) for _ in range(432)], [rng.gauss(0, 35.8) for _ in range(432)])[0] == 'FUTILITY' for _ in range(100))
if fut < 95: bad.append('negative control FUTILITY only %d/100' % fut)
# 6 null checkpoint-only false SUCCESS rate (the rule actually used) <= 5%
rng = random.Random(8); fp = sum(H.run_study([rng.gauss(0, 50) for _ in range(432)], [rng.gauss(0, 35.8) for _ in range(432)])[0] == 'SUCCESS' for _ in range(500))
if fp / 500 > 0.05: bad.append('null false SUCCESS rate %.3f' % (fp / 500))
# 7 sigma is frozen at game 10: baseline arm values after game 10 must not change the verdict
rng = random.Random(9); d = [rng.gauss(30, 50) for _ in range(432)]; b = [rng.gauss(0, 35.8) for _ in range(432)]
b2 = b[:10] + [1e6] * 422
if H.run_study(d, b) != H.run_study(d, b2): bad.append('sigma not frozen at game 10')
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (7 harness checks)'); sys.exit(1 if bad else 0)
