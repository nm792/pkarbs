"""Summaries from /tmp/macro2/days.json (analyse.py). Clean days: pool>0 or notional>=100 (drops mis-matched foreign/partial events)."""
import json, random, statistics as st, datetime as dt
days = json.load(open('/tmp/macro2/days.json'))
core = [d for d in days if d['fam'] in ('CPI', 'JOBS', 'FOMC', 'PPI') and d['notl30'] >= 100]   # same families as the 26 Oct scan
allf = [d for d in days if d['notl30'] >= 100]                                                  # + PCE
def tot(ds, k='pool30'): return sum(d['pool10'] + d['pool11_30'] if k == 'pool' else d[k] for d in ds)
for d in days: d['pool'] = d['pool10'] + d['pool11_30']
def rep(lbl, ds, span):
    pool = sum(d['pool'] for d in ds); n5 = sum(d['net30'] for d in ds); n1 = sum(d['net30f1'] for d in ds)
    top = max(ds, key=lambda d: d['pool'])
    print('%-34s days %2d gross $%6.0f net@5%% $%6.0f net@1%% $%6.0f | /cal-day net5 $%5.1f net1 $%5.1f | ex-top-day(%s %s $%.0f) net5 $%5.1f /day net1 $%5.1f /day' % (
        lbl, len(ds), pool, n5, n1, n5 / span, n1 / span, top['day'], top['fam'], top['pool'], (n5 - top['net30']) / span, (n1 - top['net30f1']) / span))
Y = 365  # 20 Oct 2025 .. 20 Nov 2026 is 396 days; use actual span
first = min(d['day'] for d in allf); last = max(d['day'] for d in allf)
span = (dt.date.fromisoformat(last) - dt.date.fromisoformat('2025-10-20')).days + 1
print('window 2025-10-20 ..', last, 'span', span, 'days; first release day', first)
rep('CORE families (CPI/jobs/FOMC/PPI)', core, span)
rep('+PCE', allf, span)
reg = [d for d in core if d['day'] >= '2026-05-01']; sp2 = (dt.date.fromisoformat(last) - dt.date.fromisoformat('2026-05-01')).days + 1
rep('May-Nov 2026 only (bot era)', reg, sp2)
reg2 = [d for d in core if d['day'] >= '2026-05-01' and d['day'] != '2026-07-29']
rep('May-Nov excl. 29 Jul FOMC', reg2, sp2)
new = [d for d in core if d['day'] >= '2026-10-16']
print('new since 26 Oct scan (days after 15 Oct):', [(d['day'], d['fam'], round(d['pool'])) for d in new], 'sum', round(sum(d['pool'] for d in new)))
# latency cut: gross pool reachable by block-second cutoff, May-Nov, ex 29 Jul
def sb(ds): 
    t = {4: 0, 6: 0, 10: 0, 20: 0, 30: 0}
    for d in ds:
        for k, v in d['sb'].items(): t[int(k)] += v
    return t
for lbl, ds in (('May-Nov all', reg), ('May-Nov ex 29Jul', reg2)):
    t = sb(ds); T = sum(t.values())
    print(lbl, 'gross by block-second bucket', {('<=%d' % k): round(v) for k, v in t.items()}, 'total', round(T),
          '| reachable if first fill lands >%ds: %s' % (4, round(T - t[4])), '>6s:', round(T - t[4] - t[6]), '>10s:', round(t[20] + t[30]))
# bootstrap annual $/day at share s over days, resampling release days (n per year ~ 45)
random.seed(1)
def boot(ds, share, key, nyear=45, B=4000):
    out = []
    for _ in range(B):
        out.append(sum(random.choice(ds)[key] for _ in range(nyear)) * share / 365)
    out.sort(); return out[int(.05 * B)], out[B // 2], out[int(.95 * B)]
for share in (0.1, 0.2, 0.3):
    for key in ('net30', 'net30f1'):
        print('bootstrap 45 release-days/yr, all core days, share %.0f%% %s: 5/50/95 pct $/day = %.1f / %.1f / %.1f' % ((share * 100, key) + boot(core, share, key)))
for share in (0.1, 0.2, 0.3):
    print('bootstrap bot-era days only (n=%d), share %.0f%% net30f1: %.1f / %.1f / %.1f' % ((len(reg), share * 100) + boot(reg, share, 'net30f1')))
