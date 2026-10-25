"""Can pre-game information pick the busiest third of matches in the 12-hour shadow?

Inputs: reports/sports-mece/hours/*/per-run-*.csv (gap runs) and evmeta-93-matches.json
(gamma /events for the 93 matches, pulled 25 Oct 2026 via TinyFish). Run from the repo root.
"""
import json, csv, glob, collections, random, statistics as st, datetime as dt

meta = {m['id']: m for m in json.load(open('reports/news-feeds/scripts/evmeta-93-matches.json'))}
rows = [r for f in glob.glob('reports/sports-mece/hours/*/per-run-*.csv') for r in csv.DictReader(open(f))]
d0 = [r for r in rows if r['delay'] == '0']
d1 = {(r['event'], r['side'], r['t0']): r for r in rows if r['delay'] != '0'}
runs = collections.Counter(r['event'] for r in d0)
pnl = collections.Counter()
for r in d0:
    k = (r['event'], r['side'], r['t0'])
    if k in d1:
        pnl[r['event']] += float(d1[k]['pnl_usd'])
ids = list(meta)
tot = sum(runs.values())
busy = set(sorted(ids, key=lambda i: -runs[i])[:31])
W0 = dt.datetime(2026, 10, 24, 21, tzinfo=dt.timezone.utc)
W1 = W0 + dt.timedelta(hours=12)
vol = {i: meta[i]['volume'] or 0 for i in ids}
gmed = st.median(vol.values())


def minutes_in_window(i):
    a = dt.datetime.fromisoformat(meta[i]['start'].replace('Z', '+00:00'))
    b = a + dt.timedelta(minutes=115)
    return max(0, (min(b, W1) - max(a, W0)).total_seconds() / 60)


def league_prior(i):
    other = [vol[j] for j in ids if j != i and meta[j]['series'] == meta[i]['series']]
    return st.median(other) if other else gmed


def show(name, key):
    pick = set(sorted(ids, key=key)[:31])
    print(f"{name:40s} overlap {len(pick & busy):2d}/31  runs {sum(runs[i] for i in pick) / tot:4.0%}  "
          f"pnl at 1 s ${sum(pnl[i] for i in pick):7.1f}")


show('pre-game: minutes inside the window', lambda i: -minutes_in_window(i))
show('pre-game: league prior (leave-one-out)', lambda i: -league_prior(i))
show('pre-game: league prior x minutes', lambda i: -league_prior(i) * minutes_in_window(i))
show('hindsight: total match volume', lambda i: -vol[i])
show('hindsight: busiest third itself', lambda i: -runs[i])
random.seed(1)
sims = [random.sample(ids, 31) for _ in range(10000)]
ov = sorted(len(set(p) & busy) for p in sims)
sh = sorted(sum(runs[i] for i in p) / tot for p in sims)
print(f"random pick: overlap mean {st.mean(ov):.1f}, 95th pct {ov[9500]}; runs mean {st.mean(sh):.0%}, 95th pct {sh[9500]:.0%}")
