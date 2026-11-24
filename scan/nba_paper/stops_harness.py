"""Stop-rule harness for the NBA maker paper test (spec v6 line 'sequential stops', MODELLING-PRINCIPLES 13). Unit = game; value = per-game (real arm - baseline arm) 10-min markout in $.
Rules, frozen BEFORE any P&L is read: first 10 games BLIND (no verdict); sigma = 1.5 x the baseline-arm per-game sd measured on games 1-10 and frozen from then on; looks only at games
10, 20, 40, then every 20; always-valid 95% interval (normal-mixture confidence sequence, Howard et al. 2021); SUCCESS lower > 0; FUTILITY upper < 0; MAX_GAMES then 'inconclusive, ranked'.
MAX_GAMES = 432 = 60 game-days x 7.2 games/day (v2 spec)."""
import math
ALPHA = 0.05; RHO_MULT = 1.0; MAX_GAMES = 432

def checkpoints(max_games=MAX_GAMES):
    cps, g = [10, 20, 40], 40
    while g + 20 <= max_games: g += 20; cps.append(g)
    return cps

def cs_radius(n, sigma, alpha=ALPHA, rho2=None):
    """Robbins normal-mixture two-sided confidence sequence for the MEAN of n terms with sub-Gaussian proxy sigma, valid at ALL n at once (prob >= 1 - alpha):
    |S_n| < sqrt((n s^2 + r2) * (2 ln(1/alpha) + ln((n s^2 + r2)/r2))), radius of the mean = that / n. r2 = sigma^2 * 100 (mixture tuned for about 100 games)."""
    r2 = rho2 if rho2 is not None else 100.0 * sigma ** 2
    v = n * sigma ** 2 + r2
    return math.sqrt(v * (2.0 * math.log(1.0 / alpha) + math.log(v / r2))) / n

def run_study(diffs, baseline_arm, max_games=MAX_GAMES):
    """diffs: iterable of per-game real-minus-baseline values; baseline_arm: per-game baseline-arm values (same length), used ONLY for sigma at game 10.
    Returns (verdict, n_at_stop, mean, lower, upper)."""
    diffs, baseline_arm = list(diffs)[:max_games], list(baseline_arm)[:max_games]
    if len(diffs) < 10: return ('not enough games', len(diffs), None, None, None)
    b = baseline_arm[:10]; mb = sum(b) / 10; sd_b = math.sqrt(sum((x - mb) ** 2 for x in b) / 9)
    sigma = 1.5 * sd_b                                        # frozen at game 10
    s = 0.0; cps = set(checkpoints(max_games)); last = None
    for i, x in enumerate(diffs, 1):
        s += x
        if i in cps:
            m = s / i; r = cs_radius(i, sigma); last = (i, m, m - r, m + r)
            if m - r > 0: return ('SUCCESS', i, m, m - r, m + r)
            if m + r < 0: return ('FUTILITY', i, m, m - r, m + r)
    if last is None: return ('no look', len(diffs), None, None, None)
    return ('inconclusive, ranked', last[0], last[1], last[2], last[3])
