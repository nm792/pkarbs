import sys, os, datetime as dt, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import listing_study as L


def mk():
    # 3 sessions of 5m bars 14:30Z..21:00Z (EST), close rises each day; day3 has a late spike after 20:00Z
    t, c = [], []
    for k, day in enumerate((2, 3, 4)):
        base = dt.datetime(2026, 12, day, 14, 30, tzinfo=dt.timezone.utc).timestamp()
        for i in range(78):
            t.append(base + 300 * i); c.append(100 + k + (50 if (k == 2 and i >= 66) else 0) + 0.001 * i)
    return np.array(t), np.array(c)


def test_nowcast_no_lookahead():
    t, c = mk()
    ET = L.ET
    days = {}
    import collections
    dd = collections.defaultdict(list)
    for i, tt in enumerate(t):
        d = dt.datetime.fromtimestamp(tt, ET); m = d.hour * 60 + d.minute
        if 570 <= m < 960: dd[d.date()].append(i)
    days = {d: dict(open=float(c[ix[0]]), close=float(c[ix[-1]]), n=len(ix)) for d, ix in dd.items()}
    d3 = dt.date(2026, 12, 4)
    # sigma needs >=6 prior days; fake extra history
    for k in range(10):
        days[dt.date(2026, 11, 10 + k)] = dict(open=100, close=100 + 0.5 * (k % 2), n=78)
    t_before = dt.datetime(2026, 12, 4, 14, 0, tzinfo=L.ET).timestamp()   # 14:00 ET = 19:00Z, before spike at 20:00Z
    r = L.nowcast(t, c, days, d3, t_before)
    assert r is not None and abs(r[0]) < 0.05          # spike not visible yet
    t_after = dt.datetime(2026, 12, 4, 15, 30, tzinfo=L.ET).timestamp()
    r2 = L.nowcast(t, c, days, d3, t_after)
    assert r2[0] > 0.3                                   # visible once its bar has ended


def test_bar_must_have_ended():
    t, c = mk()
    # decision exactly at a bar's start must not use that bar (its close is unknown)
    import collections
    dd = collections.defaultdict(list)
    for i, tt in enumerate(t):
        d = dt.datetime.fromtimestamp(tt, L.ET); m = d.hour * 60 + d.minute
        if 570 <= m < 960: dd[d.date()].append(i)
    days = {d: dict(open=float(c[ix[0]]), close=float(c[ix[-1]]), n=78) for d, ix in dd.items()}
    for k in range(10): days[dt.date(2026, 11, 10 + k)] = dict(open=100, close=100 + 0.5 * (k % 2), n=78)
    spike_start = t[2 * 78 + 66]
    r = L.nowcast(t, c, days, dt.date(2026, 12, 4), spike_start)
    assert r[0] < 0.05
