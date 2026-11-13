# Self-test for analyze.py (5 Nov 2026): run from a scratch dir, then: python3 analyze.py tsself tsself/ev.jsonl --label self
# Expected: lead_s +2.0 (feed 2 s before the price) and -10.0 (10 s late), q_at_P 777, placeable True.
# synthetic check: price rises 3c at T=100 s; feed A arrives at 98 s (2 s ahead), feed B at 110 s (10 s late)
import json, os
d = 'tsself'; os.makedirs(d, exist_ok=True)
json.dump(dict(sport='tennis', slug='x', q='Alpha vs Beta', tokens=['TA', 'TB'], outcomes=['Ann Alpha', 'Bea Beta']), open(d + '/markets.jsonl', 'w'))
with open(d + '/books.jsonl', 'w') as f:
    for s in range(0, 200):
        p = 0.50 if s < 100 else 0.53
        for tk, q in (('TA', p), ('TB', 1 - p)):
            f.write(json.dumps(dict(ms=s * 1000, tk=tk, bids=[dict(price=f'{q-0.005:.3f}', size='100'), dict(price=f'{__import__('math').floor(q*0.975*100+1e-9)/100:.2f}', size='777')], asks=[dict(price=f'{q+0.005:.3f}', size='100')])) + '\n')
with open(d + '/ev.jsonl', 'w') as f:
    for R in (98000, 110000):
        f.write(json.dumps(dict(ms=R, ev_ms=R - 500, sport='tennis', teams=['Alpha', 'Beta'], gains=0, kind='point')) + '\n')
