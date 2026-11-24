"""Offline checks. Run: python3 -I test_mentions_pm_ws_paper.py <mentions_pm_ws_paper.py>"""
import sys, importlib.util, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
sp = importlib.util.spec_from_file_location('w', sys.argv[1]); W = importlib.util.module_from_spec(sp); sys.modules['w'] = W; sp.loader.exec_module(W)
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
b = W.Book(); b.snapshot({'asks': [{'price': '0.3', 'size': '100'}, {'price': '0.9', 'size': '5'}], 'bids': [{'price': '0.2', 'size': '50'}]}, 1.0)
chk('snapshot builds asks and bids', b.asks == {.3: 100., .9: 5.} and b.bids == {.2: 50.})
b.change('SELL', .3, 40, 2.0); b.change('SELL', .9, 0, 2.0); b.change('SELL', .35, 10, 2.0)
chk('price_change SELL updates the ask side, size 0 deletes the level', b.asks == {.3: 40., .35: 10.})
b.change('BUY', .2, 0, 3.0)
chk('price_change BUY touches only bids', b.bids == {} and b.asks == {.3: 40., .35: 10.})
t = W.take([(.30, 100), (.40, 1000), (.80, 500)], .5, 200.)
chk('take walks .30 x100 then .40 to $200 and never touches .80', abs(t['cost'] - 200) < 1e-6 and abs(t['size'] - (100 + 170 / .4)) < 1e-6 and not t['partial'])
chk('take partial when depth is short', W.take([(.3, 100)], .5, 200.)['partial'])
chk('take respects the 5c floor', W.take([(.03, 1000)], .5, 200.)['size'] == 0)
chk('resting bid: print below our price fills without queue', abs(W.resting_fill(.30, 100, 500, [(.29, 40)]) - 40) < 1e-9)
chk('resting bid: print at our price first consumes the queue (500 ahead)', W.resting_fill(.30, 100, 500, [(.30, 300), (.30, 150)]) == 0 and abs(W.resting_fill(.30, 100, 500, [(.30, 300), (.30, 350)]) - 100) < 1e-9)
chk('resting bid: print above our price never fills', W.resting_fill(.30, 100, 0, [(.31, 1000)]) == 0)
T = 1_800_000_000.0; sl = W.slots(T - 100000, T)
chk('slots: 13 listing + 4 point variants + 72 during', len(sl) == 13 + 4 + 72 and ('T-1h', T - 3600) in sl)
ok_, missed = W.due([('T-1h', 100.), ('T-6h', 10.), ('T-15m', 500.)], 105., set())
chk('due: on-time slot taken, 95 s late slot missed, future slot waits', ok_ == [('T-1h', 100.)] and missed == [('T-6h', 10.)])
runs = [dict(t=1000 - 60 * i, accepting_tokens=100, books_received=100, connected=True, last_msg_age_s=3, errors_new=0) for i in range(15)][::-1]
ok2, miss2 = W.due([('T-1h', 100.), ('T-6h', 10.)], 105., set(), since=50.)
chk('due: slots before the process start are ignored, not counted missed', ok2 == [('T-1h', 100.)] and miss2 == [])
chk('health PASS with 15 heartbeats, 100% books', W.health_eval(runs, 1000)[0])
chk('health FAIL at 90% books', not W.health_eval([dict(r, books_received=90) for r in runs], 1000)[0])
chk('health FAIL on an error', not W.health_eval(runs[:-1] + [dict(runs[-1], errors_new=1)], 1000)[0])
chk('health FAIL when heartbeats stop (3 in window)', not W.health_eval(runs[-3:], 1000)[0])
chk('health FAIL when the stream is silent 120 s', not W.health_eval(runs[:-1] + [dict(runs[-1], last_msg_age_s=120)], 1000)[0])
import tempfile
good = dict(expected_tokens=100, tokens_subscribed=100, books_received=100, msgs=500, seconds=62, lines_written=900, second_copy_refused=True, health_ok=True)
chk('preflight PASS on a good run', W.preflight_eval(good)[0])
chk('preflight FAIL on 0 tokens', not W.preflight_eval(dict(good, expected_tokens=0, tokens_subscribed=0))[0])
chk('preflight FAIL when subscribed != expected', not W.preflight_eval(dict(good, tokens_subscribed=90))[0])
chk('preflight FAIL with no live data written', not W.preflight_eval(dict(good, msgs=0, lines_written=0))[0])
chk('preflight FAIL under 60 s', not W.preflight_eval(dict(good, seconds=40))[0])
chk('preflight FAIL when a second copy was not refused', not W.preflight_eval(dict(good, second_copy_refused=False))[0])
chk('preflight FAIL when the health checker lacks the mode', not W.preflight_eval(dict(good, health_ok=False))[0])
d = tempfile.mkdtemp(); l1 = W.acquire_lock(d)
chk('single-instance lock: first taken, second refused, retaken after release', l1 is not None and W.acquire_lock(d) is None and (l1.close() or True) and W.acquire_lock(d) is not None)
d2 = tempfile.mkdtemp(); json.dump({'7': [['S-5h', 500.0], ['S-30m', 900.0]], '8': [['x', 1.0]]}, open(d2 + '/extra_slots.json', 'w'))
evx = {'7': dict(slots=[('T-1h', 700.0)])}; W.merge_extra(evx, d2)
chk('extra slots: merged and sorted for a known event, unknown event ignored', evx['7']['slots'] == [('S-5h', 500.0), ('T-1h', 700.0), ('S-30m', 900.0)] and '8' not in evx)
chk('extra slots: no file = unchanged', W.merge_extra({'7': dict(slots=[('a', 1.0)])}, tempfile.mkdtemp())['7']['slots'] == [('a', 1.0)])
class _Sc:
    GAMMA = 'g'
    def __init__(self, pages): self.pages = pages; self.calls = []
    def fetch(self, u):
        self.calls.append(u); k = len(self.calls) - 1
        return self.pages[k] if k < len(self.pages) else []
r2 = _Sc([[1] * 50, [2] * 50, [3] * 7]); out2 = W.fetch_open(r2)
chk('fetch_open pages at limit=50 with offsets 0,50,100 and stops on a short page', len(out2) == 107 and all('limit=50' in u for u in r2.calls) and ['offset=0' in r2.calls[0], 'offset=50' in r2.calls[1], 'offset=100' in r2.calls[2]] == [True] * 3 and len(r2.calls) == 3)
chk('fetch_open returns None (not an empty list) when ANY page fails (HTTP 406 case)', W.fetch_open(_Sc([[1] * 50, None])) is None and W.fetch_open(_Sc([None])) is None)
class _Sc2(_Sc):
    def fetch(self, u): return None
json.dump({}, open(d + '/events.json', 'w'))
try: W.universe(_Sc2([]), d, 0.0); raised = False
except RuntimeError: raised = True
except Exception: raised = False
chk('universe raises RuntimeError on a failed read instead of returning an empty universe', raised)
old = ({'e': 1}, {'t1': 1}); new = ({}, {})
chk('keep_or_replace keeps the old universe when the new one is empty', W.keep_or_replace(old, new) is old and W.keep_or_replace(old, ({'f': 1}, {'t2': 1}))[1] == {'t2': 1} and W.keep_or_replace(({}, {}), new) is new)
bk = W.Book(); bk.snapshot({'asks': [{'price': '0.4', 'size': '10'}, {'price': '0.5', 'size': '20'}], 'bids': [{'price': '0.3', 'size': '5'}]}, 100.0)
br = W.beat_row(103.0, 'tk', ('e1', 'c1', 0, 'Will Dell (DELL) beat quarterly earnings?'), bk)
chk('beat_row logs own-token best ask/bid, full ask $ and the ladder', br['best_ask'] == .4 and br['best_bid'] == .3 and abs(br['ask_usd'] - 14.0) < 1e-9 and br['age_s'] == 3.0 and br['asks'][1] == [.5, 20.0])
class _Sb:
    GAMMA = 'g'
    def fetch(self, u): return [{'id': 9, 'title': 'Will Dell (DELL) beat quarterly earnings?', 'markets': [{'conditionId': 'c', 'acceptingOrders': True, 'clobTokenIds': json.dumps(['y', 'n'])}]}, {'id': 8, 'title': 'Dell earnings call words', 'markets': [{'conditionId': 'd', 'acceptingOrders': True, 'clobTokenIds': json.dumps(['a', 'b'])}]}]
chk('beat_universe keeps only beat markets (both tokens), not other earnings events', set(W.beat_universe(_Sb())) == {'y', 'n'})
class _Sb2(_Sb):
    def fetch(self, u): return None
chk('beat_universe returns None on a failed read (caller keeps the old set)', W.beat_universe(_Sb2()) is None)
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
