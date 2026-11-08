"""Rugby history check: ESPN scoring events vs Polymarket home-win price.

ESPN scoreboard 'details' give each try / conversion / penalty goal / card
with the GAME clock only (seconds), not wall-clock time. So event wall
time is approximated as kickoff + clock (1st half) or kickoff + clock +
an assumed 15 min half-time (2nd half), error about +/- 3 min. That is too
coarse for lag, so this only checks the SIZE of price moves around scores
against the model: pre = median trade 8-3 min before, post = 3-8 min after.
Usage: python3 -m evrules.rugby_hist_check <espn hist dir> <out dir>
"""
import json, glob, sys, os, subprocess, datetime as dt
import numpy as np
from evrules import rugby

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
GAMMA = '/mnt/project-files/rugby/raw'


def get(url):
    o = subprocess.run(['curl', '-sS', '--compressed', '-m', '30', '-A', UA, url], capture_output=True, text=True).stdout
    return json.loads(o)


def trades(cid, out):
    f = f'{out}/trades_{cid[:12]}.json'
    if os.path.exists(f): return json.load(open(f))
    allt, off = [], 0
    while off <= 10000:
        t = get(f'https://data-api.polymarket.com/trades?market={cid}&limit=500&offset={off}')
        if not isinstance(t, list) or not t: break
        allt += t; off += 500
        if len(t) < 500: break
    json.dump(allt, open(f, 'w')); return allt


def main():
    H, OUT = sys.argv[1], sys.argv[2]
    espn = {}
    for f in glob.glob(f'{H}/sb_*.json'):
        for e in json.load(open(f)).get('events', []):
            espn[e['id']] = e
    gam = []
    for f in glob.glob(f'{GAMMA}/tag102193_closedtrue_*.json'):
        gam += [e for e in json.load(open(f)) if e.get('volume', 0) >= 20000 and len(e.get('markets', [])) == 3]
    rows, used = [], []
    for g in gam:
        home, away = g['markets'][0].get('groupItemTitle'), g['markets'][2].get('groupItemTitle')
        day = g['slug'][-10:]
        cand = [e for e in espn.values() if e['date'][:10] == day and
                any(home.split()[0].lower() in c['team']['displayName'].lower() for c in e['competitions'][0]['competitors'] if c['homeAway'] == 'home')]
        if not cand: continue
        e = cand[0]; c = e['competitions'][0]
        hid = [x for x in c['competitors'] if x['homeAway'] == 'home'][0]['team']['id']
        ko = dt.datetime.fromisoformat(e['date'].replace('Z', '+00:00')).timestamp()
        tr = trades(g['markets'][0]['conditionId'], OUT)
        pts = {'try': 5, 'conversion': 2, 'penalty goal': 3, 'drop goal': 3, 'penalty try': 7}
        px = sorted((t['timestamp'], t['price'] if t['outcomeIndex'] == 0 else 1 - t['price']) for t in tr)
        if len(px) < 50: continue
        pt = np.array([a for a, _ in px], float); pp = np.array([b for _, b in px])
        margin = 0; n0 = len(rows)
        for d in c.get('details', []):
            typ = d['type']['text'].lower(); clk = d['clock']['value']
            p = pts.get(typ)
            if p is None: continue
            s = p if d['team']['id'] == hid else -p
            T = ko + clk + (900 if clk > 2400 else 0)
            w0 = (pt >= T - 480) & (pt <= T - 180); w1 = (pt >= T + 180) & (pt <= T + 480)
            if w0.sum() >= 2 and w1.sum() >= 2:
                pre = float(np.median(pp[w0])); post = float(np.median(pp[w1]))
                if 0.03 < pre < 0.97 and clk < 4700:
                    before = (margin, 80 - clk / 60); after = (margin + s, 80 - clk / 60)
                    q = rugby.fair_after(before, after, pre)
                    if q: rows.append(dict(event=g['slug'], type=typ, clock=clk, pre=pre, post=post, pred=q[0]))
            margin += s
        used.append(dict(slug=g['slug'], espn_id=e['id'], trades=len(tr), events=len(rows) - n0))
    r = np.array([(x['pre'], x['post'], x['pred']) for x in rows])
    mv = r[:, 1] - r[:, 0]; pm = r[:, 2] - r[:, 0]; sig = np.abs(mv) > 0.01
    out = dict(matches=used, n_events=len(rows),
               model_abs_err_median=float(np.median(np.abs(r[:, 1] - r[:, 2]))), naive_abs_err_median=float(np.median(np.abs(mv))),
               model_abs_err_mean=float(np.mean(np.abs(r[:, 1] - r[:, 2]))), naive_abs_err_mean=float(np.mean(np.abs(mv))),
               dir_hit_moves_gt_1c=float(np.mean(np.sign(pm[sig]) == np.sign(mv[sig]))),
               slope_realised_on_pred=float(np.polyfit(pm, mv, 1)[0]),
               caveat='event wall time approximated from game clock (+/- ~3 min); size check only, no lag', rows=rows)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'params', 'rugby_hist_check.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
