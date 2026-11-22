"""Offline checks for kalshi_mentions_daily.py. Run: python3 -I test_kalshi_mentions_daily.py <kalshi_mentions_daily.py> <mm_forward2.py>"""
import sys, importlib.util, datetime as dt
def L(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m
sys.argv_saved = sys.argv; sys.argv = [sys.argv[0], '--mm2', sys.argv[2], '--out', '/tmp', '--arm', '2']
D = L('d', sys.argv_saved[1]); K = L('k', sys.argv_saved[2]); D.FRz.update({k: K.ts(v) for k, v in D.FR.items()})
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
T0 = K.ts('2026-11-12T00:00:00+00:00'); iso = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()
def mkt(et, w, yes, t0, close):
    return dict(ticker=f'{et}-{w}', event_ticker=et, yes_sub_title=w, result='yes' if yes else 'no', open_time=iso(t0), close_time=iso(close), settlement_ts=iso(close))
data = {'S': []}
for i in range(10):  # 10 earlier resolved events, word 'a' always no
    t = T0 - 86400 * (i + 2); data['S'] += [mkt(f'H{i}', w, y, t, t + 3600) for w, y in (('a', 0), ('b', 1), ('c', 1))]
data['S'] += [mkt('F', w, y, T0, T0 + 7200) for w, y in (('a', 0), ('b', 1), ('c', 1))]
tr = {'F-b': [(T0 + 60, 'yes', .50, .50, 10.0)], 'F-a': [], 'F-c': []}
fn = lambda m: tr.get(m['ticker'], [])
rows = D.score(K, data, 2, T0 + 7200, fn); f = [r for r in rows if r['event'] == 'F'][0]
chk('eligible with 10 earlier events', f['eligible'] and f['hist'] == 10)
chk('bet YES b at .50 (q~.9)', f['bet'] and f['bet']['word'] == 'b' and f['bet']['price'] == .5)
chk('net = gross - kalshi fee', abs(f['bet']['pnl_net'] - (0.5 * 10 - K.fee(.5, 10))) < 1e-9)
tr['F-b'] = [(T0 + 60, 'yes', .93, .07, 10.0)]
chk('edge < 3c -> no bet', [r for r in D.score(K, data, 2, T0 + 7200, fn) if r['event'] == 'F'][0]['bet'] is None)
tr['F-b'] = [(T0 + 60, 'yes', .50, .50, 10.0)]
chk('window not done (30 min old) -> no bet', [r for r in D.score(K, data, 2, T0 + 1800, fn) if r['event'] == 'F'][0]['bet'] is None)
data2 = {'S': [m for m in data['S'] if not m['event_ticker'].startswith('H') or m['event_ticker'] != 'H0']}
chk('9 earlier events -> not eligible (arm 2 needs 10)', not [r for r in D.score(K, data2, 2, T0 + 7200, fn) if r['event'] == 'F'][0]['eligible'])
chk('arm 1 needs no minimum history', [r for r in D.score(K, data2, 1, T0 + 7200, fn) if r['event'] == 'F'][0]['eligible'])
tr['F-c'] = [(T0 + 60, 'yes', .50, .50, 3.0)]   # tie on time: tuple-min picks lower price then smaller size, same as mm_forward2
chk('tie-break equals mm_forward2 tuple min (word b size 10 vs c size 3 -> c)', [r for r in D.score(K, data, 2, T0 + 7200, fn) if r['event'] == 'F'][0]['bet']['word'] == 'c')
s = D.summarize(D.score(K, data, 2, T0 + 7200, fn), 2, T0 + 7200)
chk('verdict undefined below 100 bets', 'not yet defined' in s['verdict'] and s['bets_resolved'] == 1)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
