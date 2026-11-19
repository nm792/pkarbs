#!/usr/bin/env python3
"""Nowcast of the AAA national average for date D from information known BEFORE the daily release, scored out of sample against
the Polymarket favourite at the same timestamps. Analysis only (public data).
Inputs: aaa_prints.json (Kalshi KXAAAGASD expiration_value = AAA national regular, 4dp), dgasnyh.csv / dgasgulf.csv (FRED spot, $/gal),
pm_hist.json (Polymarket buckets and 1-min price history), pm_trades.json (/v2/trades).
Target: P_D (price displayed 10:00 ET on D). Known at the three scoring times (16:00Z D-1, 03:00Z D, 05:00Z D): AAA prints up to D-1,
spot through D-2 at 16:00Z and through D-1 at 03:00Z and 05:00Z (D-1 spot assessed late afternoon ET)."""
import json, re, csv, time, calendar, datetime as dt, math
import numpy as np
LAGS_AR = 5
def load_prints(path="aaa_prints.json"):
    d = json.load(open(path)); out = {}
    for e, (ct, v) in d.items():
        m = re.search(r'-(\d\d)([A-Z]{3})(\d\d)', e); out[dt.datetime.strptime(m.group(1) + m.group(2) + m.group(3), '%y%b%d').date()] = v
    return out
def load_spot(path):
    s = {}
    for r in csv.reader(open(path)):
        try: s[dt.date.fromisoformat(r[0])] = float(r[1])
        except Exception: pass
    return s
def last_known(series, day):
    """value on the latest date <= day (spot is not published on weekends/holidays)."""
    for k in range(0, 8):
        d = day - dt.timedelta(days=k)
        if d in series: return series[d]
    return None
def features(prints, nyh, gulf, D, spot_lag):
    """feature vector for target day D; spot_lag = 2 (16:00Z D-1: spot through D-2) or 1 (03:00Z/05:00Z: through D-1)."""
    p = [prints.get(D - dt.timedelta(days=k)) for k in range(1, LAGS_AR + 2)]
    if any(x is None for x in p): return None
    dp = [(p[i] - p[i + 1]) * 100 for i in range(LAGS_AR)]            # cents, dp[0] = P_{D-1}-P_{D-2}
    sd = D - dt.timedelta(days=spot_lag)
    sn = [last_known(nyh, sd - dt.timedelta(days=k)) for k in (0, 1, 3, 5)]
    sg = [last_known(gulf, sd - dt.timedelta(days=k)) for k in (0, 1, 3, 5)]
    if any(x is None for x in sn + sg): return None
    x = dp + [(sn[0] - sn[1]) * 100, (sn[0] - sn[2]) * 100, (sn[0] - sn[3]) * 100, (sg[0] - sg[1]) * 100, (sg[0] - sg[3]) * 100,
              (p[0] - sn[0]) * 100]                                    # retail minus spot, cents (margin proxy)
    return np.array(x)
def ridge_fit(X, y, alpha=10.0):
    mu, sd = X.mean(0), X.std(0) + 1e-9; Z = (X - mu) / sd; b0 = y.mean()
    w = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ (y - b0))
    return mu, sd, w, b0
def ridge_pred(m, x): mu, sd, w, b0 = m; return float(((x - mu) / sd) @ w + b0)
def norm_cdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def bucket_bounds(q):
    """(lo, hi) of the price interval, in dollars, from a Polymarket gas question; hi exclusive."""
    nums = [float(x) for x in re.findall(r'\$(\d\.\d+)', q)]
    if 'less than' in q: return (-1e9, nums[0])
    if 'between' in q: return (nums[0], nums[1] + 0.0001)
    return (nums[0], 1e9)                                          # '$X+' i.e. at or above
def bucket_probs(mean, sd, bounds):
    return [norm_cdf((hi - mean) / sd) - norm_cdf((lo - mean) / sd) for lo, hi in bounds]
def oos_predict(prints, nyh, gulf, D, spot_lag, train_from, alpha=10.0, min_train=60):
    """expanding window: fit only on days d with d < D (target known by D-1 morning in live use: use d <= D-1), return (mu_cents, sigma_cents) or None."""
    X, y = [], []
    d = train_from
    while d < D:
        if d in prints and (d - dt.timedelta(days=1)) in prints:
            f = features(prints, nyh, gulf, d, spot_lag)
            if f is not None: X.append(f); y.append((prints[d] - prints[d - dt.timedelta(days=1)]) * 100)
        d += dt.timedelta(days=1)
    if len(X) < min_train: return None
    X, y = np.array(X), np.array(y); m = ridge_fit(X, y, alpha)
    res = y - np.array([ridge_pred(m, x) for x in X]); sig = max(float(res.std()), 0.5)
    f = features(prints, nyh, gulf, D, spot_lag)
    if f is None: return None
    return ridge_pred(m, f), sig
