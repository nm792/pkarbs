"""Live cricket test: ESPN ball-by-ball (our receive time) vs Polymarket trades.

Inputs: logger jsonl (evrules/live_pbp_logger.py) and data-api v2 trades.
1. Signed lag (as rn1/scores/cs2/live/signed_lag.py): for each wicket or
   boundary received at R, find the 2c move nearest R within +/-120 s,
   measured from the last trade at or before R-120 s. Lag = trade time - R.
   Negative = the price moved before ESPN showed the ball to us.
2. Model check: pre = last trade at or before R-5 s, post = median of trades
   R+20..R+120 s, pred = cricket.fair_after(state before ball, state after, pre).
Usage: python3 -m evrules.eval_cricket_live <jsonl> <trades_v2.json> <home_outcome_index> [fmt]
"""
import json, sys
import numpy as np
from evrules import cricket


def parse(s):
    if '/' in s:
        r, w = s.split('/'); return int(r), int(w)
    return int(s), 0


def balls(over):
    o = int(over); b = round((over - o) * 10)
    return o * 6 + b


def main():
    jl, tf, home_idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rows = [json.loads(l) for l in open(jl)]
    rows = [r for r in rows if not r.get('first_poll')]          # skip the backfill batch
    tr = json.load(open(tf)); tr = tr['data'] if isinstance(tr, dict) else tr
    px = sorted((t['timestamp'], t['price'] if t['outcome_index'] == home_idx else 1 - t['price']) for t in tr)
    pt = np.array([a for a, _ in px], float); pp = np.array([b for _, b in px])
    allrows = [json.loads(l) for l in open(jl)]
    first_total = None
    for r in allrows:
        if r['inn'] == 1: first_total = parse(r['home'])[0]
    lag, model = [], []
    prev_state = {}
    for r in allrows:
        inn = r['inn']; bat_home = inn == 1
        runs, w = parse(r['home'] if bat_home else r['away'])
        b = balls(r['over'])
        st = dict(innings=inn, runs=runs, wkts=w, balls=b, target=(first_total + 1) if inn == 2 else None)
        before = prev_state.get(inn)
        prev_state[inn] = st
        if r.get('first_poll') or r['play'] not in ('out', 'four', 'six') or before is None:
            continue
        R = r['recv_ms'] / 1000.0
        # expected direction for the home (batting-first) team price
        good_for_bat = r['play'] in ('four', 'six')
        sign = (1 if good_for_bat else -1) * (1 if bat_home else -1)
        base_i = np.searchsorted(pt, R - 120, side='right') - 1
        if base_i >= 0:
            base = pp[base_i]
            w = np.where((pt >= R - 120) & (pt <= R + 120) & (np.abs(pp - base) >= 0.02))[0]
            if len(w):
                j = w[np.argmin(np.abs(pt[w] - R))]
                lag.append(dict(play=r['play'], over=r['over'], inn=inn, lag=float(pt[j] - R), dir_ok=bool(np.sign(pp[j] - base) == sign)))
            else:
                lag.append(dict(play=r['play'], over=r['over'], inn=inn, lag=None, dir_ok=None))
        i0 = np.searchsorted(pt, R - 5, side='right') - 1
        w1 = (pt >= R + 20) & (pt <= R + 120)
        if i0 >= 0 and w1.sum() >= 1 and 0.03 < pp[i0] < 0.97:
            pre = float(pp[i0]); post = float(np.median(pp[w1]))
            try:
                pred = cricket.fair_after(before, st, pre)
            except Exception:
                continue
            model.append(dict(play=r['play'], over=r['over'], inn=inn, pre=pre, post=post, pred=float(pred)))
    L = [x['lag'] for x in lag if x['lag'] is not None]
    out = dict(events=len(lag), with_move=len(L),
               lag_s=dict(median=float(np.median(L)), p25=float(np.percentile(L, 25)), p75=float(np.percentile(L, 75)),
                          share_price_first=float(np.mean(np.array(L) < 0))) if L else None,
               dir_ok=float(np.mean([x['dir_ok'] for x in lag if x['dir_ok'] is not None])) if L else None,
               trades_total=len(px))
    if model:
        m = np.array([(x['pre'], x['post'], x['pred']) for x in model])
        mv = m[:, 1] - m[:, 0]; pm = m[:, 2] - m[:, 0]
        out['model'] = dict(n=len(m), model_abs_err_median=float(np.median(np.abs(m[:, 1] - m[:, 2]))),
                            naive_abs_err_median=float(np.median(np.abs(mv))),
                            mean_pred_move=float(np.mean(np.abs(pm))), mean_realised_in_pred_dir=float(np.mean(np.sign(pm) * mv)),
                            slope=float(np.polyfit(pm, mv, 1)[0]) if len(m) > 2 else None)
    out['lag_rows'] = lag; out['model_rows'] = model
    print(json.dumps({k: v for k, v in out.items() if not k.endswith('_rows')}, indent=1))
    return out


if __name__ == '__main__':
    o = main()
    if len(sys.argv) > 4:
        json.dump(o, open(sys.argv[4], 'w'), indent=1)
