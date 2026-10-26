"""Share of the 0-30 s pool that comes from prints under $10 notional (what the FOMC re-pull dropped)."""
import json, time, urllib.request
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f: return json.load(f)
        except Exception as ex: err = ex; time.sleep(2 ** i)
    raise err
CASES = {'1791981000': ['1005013', '1005014', '1005015', '1005022'],  # 14 Oct 2026 CPI
         '1789043400': ['844539'],                                     # 10 Sep 2026 PPI
         '1790944200': ['964994', '964993']}                          # 2 Oct 2026 jobs
tot = small = 0.0
for R, eids in CASES.items():
    R = int(R)
    for eid in eids:
        e = get('https://gamma-api.polymarket.com/events?id=' + eid)[0]
        win = {m['conditionId']: json.loads(m['outcomePrices']).index('1') for m in e['markets'] if sorted(json.loads(m.get('outcomePrices') or '[]')) == ['0', '1']}
        cs = ','.join(win); off = 0; rows = []
        while off <= 3000:
            d = get('https://data-api.polymarket.com/trades?limit=500&offset=%d&market=%s' % (off, cs))
            rows += d
            if not d or d[-1]['timestamp'] < R - 60 or len(d) < 500: break
            off += 500
        for r in rows:
            if not 0 <= r['timestamp'] - R <= 30 or r['conditionId'] not in win: continue
            v = 1.0 if r['outcomeIndex'] == win[r['conditionId']] else 0.0
            p, s = float(r['price']), float(r['size'])
            ed = (v - p) * s if r['side'] == 'BUY' else (p - v) * s
            if ed > 0:
                tot += ed
                if p * s < 10: small += ed
        print(eid, e['slug'][:30], len(rows), 'pool so far %.0f, from <$10 prints %.0f' % (tot, small), flush=True)
print('share from prints under $10: %.1f%%' % (100 * small / tot))
