"""Planted-edge power run THROUGH the stops harness at 250 ms (SETTLED A3 hold on NBA) and 1 s (gate wording). SYNTHETIC: it validates the harness (detects a planted edge, does not detect a null, loses the edge when delay kills it); it says NOTHING about whether the real market has this edge.
Mechanism of the plant: after each qualifying score event the market's quotes stay stale for S = 0.9 s; sell flow arrives at 2.0 fills/s per event while stale; a bid eligible at d seconds after the decision (d = hold + order latency 0.206 s) can fill only in (d, S). Each fill earns shares x (J + noise) 10-min markout; baseline-arm fills have zero-mean noise.
Planted J is set so that the mean per-game edge at the 250 ms hold is about the stack-layer target (+$27.8/game lower-bound bar is for $200/day; we plant +$30/game)."""
import sys, os, json, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import stops_harness as H
S_STALE, LAM, N_EV, SHARES, NOISE_SD, LAT = 0.9, 2.0, 40, 200, 0.03, 0.206
def poisson(rng, lam):
    L = math.exp(-lam); k = 0; p = 1.0
    while True:
        p *= rng.random()
        if p <= L: return k
        k += 1
def game(rng, hold, J):
    d = hold + LAT
    mean_fills = LAM * max(0.0, S_STALE - d)                 # per event
    real = sum(SHARES * (J + rng.gauss(0, NOISE_SD)) for _ in range(poisson(rng, mean_fills * N_EV)))
    base_n = poisson(rng, LAM * max(0.0, S_STALE - (0.250 + LAT)) * N_EV)       # baseline arm: matched count, fixed across latency cells (a fixed comparison set)
    base = sum(SHARES * rng.gauss(0, NOISE_SD) for _ in range(base_n))
    return real - base, base
def study(seed, hold, J):
    rng = random.Random(seed); gs = [game(rng, hold, J) for _ in range(H.MAX_GAMES)]
    return H.run_study([g[0] for g in gs], [g[1] for g in gs])
if __name__ == '__main__':
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    # J such that mean edge at hold 0.25 s ~ $30/game: fills/event = 2*(0.9-0.456)=0.888, x40 = 35.5 fills, x200 shares x J = 30 -> J = 0.0042
    J_PLANT = 30.0 / (LAM * (S_STALE - (0.250 + LAT)) * N_EV * SHARES)
    res = {'J_plant': J_PLANT, 'M': M, 'cells': []}
    for label, hold, J in [('planted, hold 250 ms', 0.250, J_PLANT), ('planted, hold 1 s', 1.0, J_PLANT), ('planted, hold 0 ms', 0.0, J_PLANT),
                           ('planted NEGATIVE edge (-J), hold 250 ms', 0.250, -J_PLANT), ('NULL (J=0), hold 250 ms', 0.250, 0.0), ('NULL (J=0), hold 1 s', 1.0, 0.0)]:
        out = [study(1000 + i, hold, J) for i in range(M)]
        v = [o[0] for o in out]; n = [o[1] for o in out if o[0] == 'SUCCESS']
        cell = {'cell': label, 'hold_s': hold, 'J': J, 'SUCCESS': v.count('SUCCESS') / M, 'FUTILITY': v.count('FUTILITY') / M, 'inconclusive': v.count('inconclusive, ranked') / M,
                'median_games_to_success': sorted(n)[len(n) // 2] if n else None}
        res['cells'].append(cell); print(cell, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'power_run_result.json'), 'w'), indent=1)
