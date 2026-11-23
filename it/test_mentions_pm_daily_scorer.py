"""Offline checks (no network) for mentions_pm_daily_scorer.py. Each check can fail. Run: python3 -I test_mentions_pm_daily_scorer.py <path to scorer>"""
import sys, importlib.util, json, math
spec = importlib.util.spec_from_file_location('sc', sys.argv[1]); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
ok = 0; N = 0
def chk(name, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', name)
T0 = 1_800_000_000.0
def mk(cond, word, yes, closed=True, start=T0, ct=T0 + 5000, fee=.04):
    pr = [1.0, 0.0] if yes else [0.0, 1.0]
    return dict(cond=cond, word=sc.norm(word), label=word, prices=pr, toks=['y' + cond, 'n' + cond], closed=closed, start=sc.dt.datetime.fromtimestamp(start, sc.dt.timezone.utc).isoformat(), closedTime=sc.dt.datetime.fromtimestamp(ct, sc.dt.timezone.utc).isoformat(), fee=fee)
def ev(i, words, yes, start=T0, ct=None, closed=True, title='What will Trump say?'):
    return dict(id=i, title=title, fam=sc.fam(title), closed=closed, markets=[mk(f'{i}{w}', w, y, closed, start, ct if ct else start + 5000) for w, y in zip(words, yes)])
W = ['a', 'b', 'c']
# history: 'a' wins 0/3 times in 3 earlier events (all settled before the forward event starts)
hist = [ev(f'h{i}', W, [0, 1, 1], start=T0 - 86400 * (i + 2), ct=T0 - 86400 * (i + 2) + 5000) for i in range(3)]
fwd = ev('f1', W, [1, 1, 1], start=T0, closed=True)
trades = {'f1a': [(T0 + 60, 'BUY', .50, 20, 0)], 'f1b': [(T0 + 90, 'BUY', .90, 5, 0)], 'f1c': [(T0 + 99, 'BUY', .90, 5, 1)]}
fz = T0 - 10
rows = sc.run(hist + [fwd], [], trades, None, fz, T0 + 7200)
r = rows[0]
# q for word 'a': wins 0, n 3, gp = 6/9 -> (0+2*.667)/5 = .267 ; edge YES at .50 = -.23 no bet. word b: wins 3,n 3 -> (3+1.333)/5=.867, edge vs .90 = -.03 no bet. NO print of c at .90: (1-.867)-.9 <0.
chk('no qualifying print -> no bet', r['bet'] is None)
trades2 = dict(trades); trades2['f1b'] = [(T0 + 90, 'BUY', .70, 5, 0)]   # q .867 - .70 = .167 >= .10 -> bet
r = sc.run(hist + [fwd], [], trades2, None, fz, T0 + 7200)[0]
chk('qualifying YES print -> bet on word b at .70 x5', r['bet'] and r['bet']['word'] == 'b' and r['bet']['price'] == .70 and r['bet']['size'] == 5)
exp = (1 - .70) * 5 - 5 * .04 * .70 * .30
chk('net pnl = gross - taker fee (%.4f)' % exp, abs(r['bet']['pnl_net'] - exp) < 1e-3)
# threshold edge: print at .78 gives edge .087 < .10 -> must NOT bet
trades3 = dict(trades); trades3['f1b'] = [(T0 + 90, 'BUY', .78, 5, 0)]
chk('edge .087 < 10c -> no bet', sc.run(hist + [fwd], [], trades3, None, fz, T0 + 7200)[0]['bet'] is None)
# window: print after 1 h ignored; print outside 5c..95c ignored; SELL ignored
trades4 = {'f1b': [(T0 + 3700, 'BUY', .70, 5, 0), (T0 + 10, 'BUY', .97, 5, 0), (T0 + 20, 'SELL', .70, 5, 0)]}
chk('late / out-of-range / SELL prints ignored', sc.run(hist + [fwd], [], trades4, None, fz, T0 + 7200)[0]['bet'] is None)
# causal history: a historical event that settles AFTER the forward start must not count
late = ev('late', W, [1, 1, 1], start=T0 - 3600, ct=T0 + 100)
rl = sc.run(hist + [late, fwd], [], trades2, None, fz, T0 + 7200)
chk('event settled after forward start excluded from history', rl[0]['hist_events'] == 3)
# open event: resolved() needs closed flag even if price is 0.995
op = ev('o1', W, [1, 1, 1], start=T0, closed=False)
for m in op['markets']: m['prices'] = [.995, .005]
chk('live price .995 without closed flag is NOT resolved', not sc.resolved(op))
# pending event: bet recorded, P&L is a mark, not counted as realised
op2 = ev('o2', W, [1, 1, 1], start=T0, closed=False)
for m in op2['markets']: m['prices'] = [.9, .1]
tr = {'o2b': [(T0 + 90, 'BUY', .70, 5, 0)]}
rr = sc.run(hist + [op2], [], tr, None, fz, T0 + 7200)
s = sc.summarize(rr, T0 + 7200, sc.dt.datetime.fromtimestamp(fz, sc.dt.timezone.utc).isoformat())
chk('pending bet counted as pending, realised P&L 0', s['pending_bets'] == 1 and s['net_pnl'] == 0 and s['pending_mark'] > 0)
# window still open (event <1h old) -> no bet decided yet
chk('event younger than 1h: window not done, no bet', sc.run(hist + [fwd], [], trades2, None, fz, T0 + 600)[0]['bet'] is None)
# book re-pricing uses OWN token only
entry = (T0 + 90, 'f1b', 0, .70, 5, .867, 'b', 'b', .04, [])
chk('book: no own-token snapshot -> status says so, no invented fill', sc.book_fill(entry, {'f1b': [(T0, 1, [(.5, 100)])]})['status'].startswith('no book'))
bf = sc.book_fill(entry, {'f1b': [(T0, 0, [(.50, 3), (.60, 100), (.80, 100)])]})
chk('book: walks asks under limit (.767): 3@.50 + 2@.60', bf['status'] == 'filled' and abs(bf['avg'] - (3 * .5 + 2 * .6) / 5) < 1e-9)
# summary: 100-event gate text
chk('verdict undefined below 100 bets', 'not yet defined' in s['verdict'])
def _gm(title, win):
    return {'id': 1, 'title': 'x', 'markets': [{'conditionId': 'c', 'groupItemTitle': title, 'question': title, 'outcomePrices': json.dumps([1.0 if win else 0.0, 0.0 if win else 1.0]), 'clobTokenIds': json.dumps(['a', 'b'])}]}
def _w(title, win): return sc.slim(_gm(title, win))['markets'][0]['word']
_old = sc.KEEP_THRESHOLD
sc.KEEP_THRESHOLD = False
chk('R-064 2a PLANTED: frozen rule pools "AI 5+ times" and "AI 50+ times" under one word (the bug)', _w('AI 5+ times', 1) == _w('AI 50+ times', 0) == 'aitimes')
chk('R-064 2a planted: a plain 1+ word never pools with a count market', _w('AI', 1) == 'ai')
sc.KEEP_THRESHOLD = True
chk('R-064 2a fix: KEEP_THRESHOLD separates thresholds', _w('AI 5+ times', 1) == 'ai5times' and _w('AI 50+ times', 0) == 'ai50times')
chk('R-064 2a fix: bracket spelling "Iran (5+ times)" equals "Iran 5+ times"', _w('Iran (5+ times)', 1) == _w('Iran 5+ times', 1) == 'iran5times')
_h = [dict(markets=[dict(word=_w('AI 5+ times', 1), prices=[1.0, 0.0])]), dict(markets=[dict(word=_w('AI 50+ times', 0), prices=[0.0, 1.0])])]
chk('R-064 2a fix: q for AI 50+ uses only its own history (2 pooled wins would give a higher q)', sc.q_for(_h, None, dict(word=_w('AI 50+ times', 0))) < sc.q_for(_h[:1] + [dict(markets=[dict(word=_w('AI 5+ times', 1), prices=[1.0, 0.0])])], None, dict(word=_w('AI 5+ times', 1))))
sc.KEEP_THRESHOLD = _old
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
