# Fit win-probability models on rows.csv.gz; out-of-sample by match (5-fold GroupKFold).
import pandas as pd, numpy as np, json, sys
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import brier_score_loss, log_loss
BASE = ['gd','kd','td','ihd','bnd','dd','eld','soul','bbuf','lvd','csd']
def lin_feats(D):
    X = D[BASE].copy(); s = np.sqrt(D.t.clip(1,None))
    for c in ['gd','kd','td','ihd','dd','lvd','csd']: X[c+'_t'] = D[c] * D.t / 30   # effect grows with time
    X['gd_s'] = D.gd / s
    if 'elo' in D: X['elo'] = D.elo; X['elo_t'] = D.elo * D.t / 30
    return X
def models():
    return {'gold_only': (lambda D: D[['gd']].assign(gd_t=D.gd*D.t/30), lambda: LogisticRegression(max_iter=2000)),
            'logit': (lin_feats, lambda: LogisticRegression(C=1.0, max_iter=5000)),
            'gbm': (lambda D: D[BASE+['t']+(['elo'] if 'elo' in D else [])], lambda: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200))}
def cv(R, k=5):
    out = {}; P = {}
    gk = GroupKFold(n_splits=k)
    for name, (fx, mk) in models().items():
        p = np.zeros(len(R))
        for tr, te in gk.split(R, R.y, R.match):
            m = mk().fit(fx(R.iloc[tr]), R.y.iloc[tr]); p[te] = m.predict_proba(fx(R.iloc[te]))[:,1]
        P[name] = p
        out[name] = dict(brier=round(brier_score_loss(R.y, p),4), logloss=round(log_loss(R.y, p),4))
    p0 = np.full(len(R), R.y.mean())
    out['constant'] = dict(brier=round(brier_score_loss(R.y,p0),4), logloss=round(log_loss(R.y,p0),4))
    return out, P
if __name__ == '__main__':
    R = pd.read_csv('rows.csv.gz', dtype={'gid':str,'match':str}); R = R[R.t >= 0.5]
    print('games', R.gid.nunique(), 'matches', R.match.nunique(), 'rows', len(R))
    out, P = cv(R)
    print(json.dumps(out, indent=1))
    R = R.assign(**{f'p_{k}':v for k,v in P.items()})
    # by game-time bucket
    R['tb'] = pd.cut(R.t, [0,5,10,15,20,25,30,35,60])
    tab = R.groupby('tb', observed=True).apply(lambda g: pd.Series({'n':len(g), **{k: brier_score_loss(g.y, g['p_'+k]) for k in P}})).round(4)
    print(tab)
    # calibration of best
    R['pb'] = pd.cut(R.p_gbm, np.linspace(0,1,11))
    cal = R.groupby('pb', observed=True).agg(n=('y','size'), pred=('p_gbm','mean'), obs=('y','mean')).round(3)
    print(cal)
    cal2 = R.assign(pb=pd.cut(R.p_logit, np.linspace(0,1,11))).groupby('pb', observed=True).agg(n=('y','size'), pred=('p_logit','mean'), obs=('y','mean')).round(3)
    print(cal2)
    R[['gid','match','t','y']+[f'p_{k}' for k in P]].to_csv('oos_preds.csv.gz', index=False)
    json.dump(out, open('cv_scores.json','w'), indent=1)
