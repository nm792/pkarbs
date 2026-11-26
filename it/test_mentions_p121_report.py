"""Offline checks, each can fail. Run: python3 -I test_mentions_p121_report.py <mentions_p121_report.py>"""
import sys, importlib.util, os, json, tempfile, subprocess
sp = importlib.util.spec_from_file_location('r', sys.argv[1]); R = importlib.util.module_from_spec(sp); sys.modules['r'] = R; sp.loader.exec_module(R)
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
r = dict(side='YES', fair=.5, limit=.4, fee_rate=.04, take=dict(levels=[[.30, 100.0], [.38, 100.0]]))
c, n, s = R.pnl_take(r, 1)
chk('YES take wins: pays 1 per share, minus cost and fee', abs(c - 68) < 1e-9 and abs(s - 200) < 1e-9 and abs(n - (200 - 68 - .04 * .34 * .66 * 200)) < 1e-9)
chk('YES take loses: net = -cost - fee', abs(R.pnl_take(r, 0)[1] - (-68 - .04 * .34 * .66 * 200)) < 1e-9)
rn = dict(r, side='NO'); chk('NO take wins when the market resolves NO (w = 0)', R.pnl_take(rn, 0)[1] > 100 and R.pnl_take(rn, 1)[1] < 0)
chk('reprice_on same when the on-key limit is unchanged', R.reprice_on(r, .5)[0] == 'same' or R.reprice_on(r, .5)[0] == 'on_only_more')
st, lv = R.reprice_on(r, .45)   # fair .45, limit .35: only the .30 level survives
chk('reprice_on shrinks to the levels at or under the new limit', st == 'shrunk' and lv == [[.30, 100.0]])
chk('reprice_on drops the take when no level clears the new limit', R.reprice_on(r, .35)[0] == 'dropped')
chk('reprice_on flags on_only_more (higher limit, logged ladder is cut) instead of inventing fills', R.reprice_on(r, .7)[0] == 'on_only_more')
rows = [dict(oi=0, event='e1', cond='c1', title='Will A beat?', t=1000, best_ask=.45, asks=[[.45, 100.0], [.49, 1000.0], [.60, 500.0]]),
        dict(oi=0, event='e1', cond='c1', title='Will A beat?', t=1060, best_ask=.40, asks=[[.40, 100.0], [.49, 1000.0]]),
        dict(oi=1, event='e1', cond='c1', title='Will A beat?', t=1060, best_ask=.10, asks=[[.10, 100.0]]),
        dict(oi=0, event='e2', cond='c2', title='Will B beat?', t=1000, best_ask=.62, asks=[[.62, 100.0]]),
        dict(oi=0, event='e3', cond='c3', title='Will C beat?', t=5000, best_ask=.30, asks=[[.30, 100.0]])]
bl = R.beat_list(rows, {'e1': 9000, 'e2': 9000, 'e3': 4000}, 200.0)
chk('beat_list keeps only YES token rows under 0.50 (NO token and the 0.62 market excluded)', [b['event'] for b in bl] == ['e1'])
chk('beat_list picks the lowest YES ask minute and sizes depth at asks under 0.50 capped at $200', bl[0]['best_ask'] == .40 and abs(bl[0]['depth_usd_under_thr'] - 200.0) < 1e-6 and bl[0]['hours_to_end'] == round(8000 / 3600, 1))
chk('beat_list ignores rows recorded after the report time (e3 row at t=5000 > end 4000)', 'e3' not in [b['event'] for b in bl])
chk('beat_list: depth limited to $ available when thin (100 sh at .40 = $40)', R.beat_list([dict(oi=0, event='e', cond='c', title='t', t=1, best_ask=.4, asks=[[.4, 100.0], [.55, 100.0]])], {'e': None})[0]['depth_usd_under_thr'] == 40.0)
# end-to-end with a stub scorer
d = tempfile.mkdtemp(); st = os.path.join(d, 'state'); os.makedirs(st); out = os.path.join(d, 'out'); os.makedirs(os.path.join(out, 'earnings_beat'))
stub = '''
KEEP_THRESHOLD = False
GAMMA = 'g'
def wkey(s): return (s or '').lower()
def ts(s): return 2000.0
def fetch(u): return [dict(id=1, kind='x')]
def slim(x): return dict(id=1, title='Event One', fam='f', markets=[dict(cond='c1', word='a', label='A', prices=[1.0, 0.0], closed=True)])
def resolved(e): return True
def win(m): return 1
def start(e): return 100.0
def settled_at(h): return 50.0
def q_for(hist, e, m): return 0.8
'''
open(os.path.join(d, 'stub.py'), 'w').write(stub); json.dump({'h': dict(id=2, fam='f', markets=[dict(label='A', word='a', prices=[1.0, 0.0])])}, open(os.path.join(st, 'events.json'), 'w'))
dec = dict(ts=1500.0, event='1', variant='listing', t_decision=1500.0, cond='c1', word='A', side='YES', fair=.8, limit=.7, fee_rate=.04, take=dict(cost=60.0, size=100.0, avg=.6, levels=[[.60, 100.0]]))
open(os.path.join(out, 'decisions.jsonl'), 'w').write(json.dumps(dec) + '\n')
open(os.path.join(out, 'earnings_beat', 'books.jsonl'), 'w').write(json.dumps(rows[1]) + '\n')
p = subprocess.run([sys.executable, '-I', sys.argv[1], '--scorer', os.path.join(d, 'stub.py'), '--state', st, '--out', out], capture_output=True, text=True)
chk('end to end runs and exits 0', p.returncode == 0)
chk('end to end: one resolved take, FIRST NUMBER line carries n and net (win: 100 - 60 - fee 0.96 = 39.04)', 'FIRST NUMBER: 1 resolved paper takes from 1 logged decisions, net $39.04' in p.stdout)
chk('end to end: off and on rows both printed; sanity says recomputed fair matches the logged .8', 'off (frozen' in p.stdout and 'on (KEEP_THRESHOLD' in p.stdout and 'equals the logged fair on 1 of 1' in p.stdout)
chk('end to end: beat list printed and report file written', 'Will A beat?' in p.stdout and any(f.startswith('REPORT-') for f in os.listdir(os.path.join(out, 'reports'))))
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
