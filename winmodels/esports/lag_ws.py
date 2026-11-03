"""Score feed lag vs price, using our own server logger of the Polymarket sports websocket (recv time = when WE saw it).
For each score change: signed move of the match-winner price (sign = side that scored) in 5 s slices, -60..+60 s around recv.
Score orientation (which number is the logger 'home' team) is checked against final results."""
import sys, os, json, gzip, re, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C
G = json.load(gzip.open(f'{C.RAW}/esports/gamma_events_2026-11-02_03.json.gz'))
CH = collections.defaultdict(list)
for l in gzip.open('/home/user/pkarbs/rn1/scores/cs2/server-2026-11/cs2_changes.jsonl.gz', 'rt'):
    d = json.loads(l)
    if 'gameId' in d: CH[d['gameId']].append(d)
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
def parse(sp, s):
    if s is None: return None
    if sp in ('cs2', 'dota2'):
        p = s.split('|')
        try:
            if len(p) >= 2: r = [int(x) for x in p[0].split('-')]; mp = [int(x) for x in p[1].split('-')]; return (mp[0], mp[1], r[0], r[1])
            return None
        except Exception: return None
    try: a, b = [int(x) for x in s.split('-')[:2]]; return (0, 0, a, b)
    except Exception: return None
def ml_market(e):
    for m in e['markets']:
        if m.get('sportsMarketType') == 'moneyline' and m.get('closed'): return m
def setup(sp, e):
    m = ml_market(e); ch = sorted(CH.get(int(e['gameId']), []), key=lambda d: d['recv_ms'])
    if not m or len(ch) < 3: return None
    fn = f"{C.RAW}/esports/trades/{m['conditionId']}.json.gz"
    if not os.path.exists(fn): return None
    oc = json.loads(m['outcomes']); op = json.loads(m['outcomePrices'])
    h = norm(ch[-1]['home']); o0_home = norm(oc[0])[:6] in h or h[:6] in norm(oc[0])
    pr = C.prints(json.load(gzip.open(fn)))
    return dict(m=m, ch=ch, o0_home=o0_home, win0=op[0] == '1', M=C.Mid(pr), pr=pr)
def orient_check(sp):
    ok = bad = 0
    for e in G[sp]:
        s = setup(sp, e)
        if not s: continue
        last = parse(sp, s['ch'][-1]['score'])
        if not last: continue
        a, b = (last[0], last[1]) if sp != 'nba' else (last[2], last[3])
        if a == b: continue
        first_wins = a > b; home_won = s['win0'] == s['o0_home']
        ok += first_wins == home_won; bad += first_wins != home_won
    return ok, bad
if __name__ == '__main__':
    out = {}
    for sp in ('nba', 'cs2', 'dota2'):
        ok, bad = orient_check(sp); flip = bad > ok
        print(sp, 'orientation check (first number = logger home): agree', ok, 'disagree', bad, flush=True)
        sl = np.arange(-60, 61, 5); acc = np.zeros(len(sl) - 1); n = 0
        for e in G[sp]:
            s = setup(sp, e)
            if not s: continue
            prev = None
            for d in s['ch']:
                cur = parse(sp, d['score'])
                if cur is None: continue
                if prev is not None and cur != prev:
                    if sp == 'nba': dh = (cur[2] - prev[2]) - (cur[3] - prev[3])
                    else: dh = 10 * ((cur[0] - prev[0]) - (cur[1] - prev[1])) + ((cur[2] - prev[2]) - (cur[3] - prev[3]))
                    if dh != 0 and abs(dh) < 50:
                        t = d['recv_ms'] / 1000; sg = np.sign(dh) * (1 if s['o0_home'] else -1) * (-1 if flip else 1)
                        pts = [s['M'].at(t + x) for x in sl]
                        if all(p is not None for p in pts) and 0.1 < pts[0] < 0.9: acc += sg * np.diff(pts); n += 1
                prev = cur
        cum = np.cumsum(acc) / max(n, 1) * 100
        out[sp] = dict(events=n, slices=sl[1:].tolist(), cum_c=cum.round(3).tolist())
        print(sp, 'score changes', n, ' cumulative signed move (c) at', ' '.join(f'{a}s:{c:.2f}' for a, c in zip(sl[1:], cum) if a % 10 == 0), flush=True)
    json.dump(out, open('out_lag_ws.json', 'w'), indent=1)
