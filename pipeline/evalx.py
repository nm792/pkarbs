"""Signal evaluation: rank IC, decay, clustered t-stats, multiple-testing penalty, walk-forward split."""
import math
from collections import defaultdict


MIN_TEST_BUCKETS = 8  # fewer OOS buckets than this = 'insufficient', p set to 1


def _rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v); i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]: j += 1
        for k in range(i, j + 1): r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3: return float("nan")
    rx, ry = _rank(x), _rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx); syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        de = d * c; h *= de
        if abs(de - 1) < 1e-12: break
    return h


def _betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2): return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t_sf2(t, df):
    """Two-sided Student-t p-value (df = n-1 buckets). Small samples must not use the normal."""
    if df < 1: return 1.0
    return _betai(df / 2.0, 0.5, df / (df + t * t))


def pearson(x, y):
    n = len(x)
    if n < 3: return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def norm_sf2(z):  # kept for tests; evaluation uses t_sf2
    return math.erfc(abs(z) / math.sqrt(2))


def mean_t(vals):
    v = [x for x in vals if x == x]
    n = len(v)
    if n < 2: return float("nan"), float("nan"), n
    m = sum(v) / n; s = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, (m / (s / math.sqrt(n)) if s > 0 else float("nan")), n


# Pearson, not Spearman, on edge = win - price. Binary payoffs are two-point and skewed; under perfect calibration
# Spearman(price, edge) is non-zero (a null market showed 14/16 false discoveries), Pearson is exactly zero.
IC_FN = pearson


def ic_series(rows, sig="sig", ret="ret", by="day", min_n=6):
    """Cross-sectional rank IC per `by` bucket (e.g. day). Returns {bucket: ic}."""
    g = defaultdict(list)
    for r in rows: g[r[by]].append(r)
    out = {}
    for k, rs in g.items():
        if len(rs) >= min_n:
            out[k] = IC_FN([r[sig] for r in rs], [r[ret] for r in rs])
    return out


def cluster_mean(rows, key="ret", cluster="event"):
    """Mean of key with t-stat treating each cluster (event) as one observation."""
    g = defaultdict(list)
    for r in rows: g[r[cluster]].append(r[key])
    per = [sum(v) / len(v) for v in g.values()]
    m, t, n = mean_t(per)
    return m, t, n


def bh_fdr(pvals, q=0.1):
    """Benjamini-Hochberg: returns list of bool 'discovery' in input order."""
    m = len(pvals); order = sorted(range(m), key=lambda i: pvals[i]); kmax = -1
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m: kmax = rank
    keep = [False] * m
    for rank, i in enumerate(order, 1):
        if rank <= kmax: keep[i] = True
    return keep


def walk_forward(rows, ts_key="ts", frac=0.6):
    """Chronological split: first `frac` of distinct events by time = train, rest = test."""
    first = {}
    for r in rows: first[r["event"]] = min(first.get(r["event"], r[ts_key]), r[ts_key])
    ev = sorted(first, key=first.get); cut = set(ev[: int(len(ev) * frac)])
    return [r for r in rows if r["event"] in cut], [r for r in rows if r["event"] not in cut]


def evaluate(rows, sig="sig", ret="ret"):
    """Full evaluation of one signal on rows with keys day,event,ts,sig,ret.
    The sign of the signal is chosen on TRAIN only and applied to TEST."""
    tr, te = walk_forward(rows)
    ic_tr = ic_series(tr, sig, ret); ic_te = ic_series(te, sig, ret)
    m_tr, t_tr, n_tr = mean_t(list(ic_tr.values())); m_te, t_te, n_te = mean_t(list(ic_te.values()))
    sign = 1 if m_tr == m_tr and m_tr >= 0 else -1
    m_all, t_all, n_all = mean_t(list(ic_series(rows, sig, ret).values()))
    return dict(ic_all=m_all, t_all=t_all, n_days=n_all, ic_train=m_tr, ic_test=m_te * sign, t_test=t_te * sign,
                n_test_days=n_te, sign=sign, p_all=t_sf2(t_all, n_all - 1) if t_all == t_all else 1.0,
                p_test=t_sf2(t_te, n_te - 1) if (t_te == t_te and n_te >= MIN_TEST_BUCKETS) else 1.0, n_rows=len(rows))
