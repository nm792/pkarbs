"""Kalshi: do macro markets trade at the release second? close_time vs release, trades in [R-120, R+300]."""
import json, time, urllib.request, datetime as dt
H = {'User-Agent': 'curl/8.5.0', 'Accept': 'application/json'}
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as f: return json.load(f)
        except Exception as ex: err = ex; time.sleep(2 ** i)
    raise err
K = 'https://api.elections.kalshi.com/trade-api/v2/'
# release seconds from the Polymarket scan (UTC)
REL = {'26SEP': {'CPI': '2026-10-14T12:30', 'JOBS': '2026-10-02T12:30', 'FED': '2026-09-16T18:00'},
       '26AUG': {'CPI': '2026-09-11T12:30', 'JOBS': '2026-09-04T12:30'},
       '26JUL': {'CPI': '2026-08-12T12:30', 'JOBS': '2026-08-07T12:30', 'FED': '2026-07-29T18:00'},
       '26JUN': {'CPI': '2026-07-14T12:30', 'JOBS': '2026-07-02T12:30', 'FED': '2026-06-17T18:00'},
       '26APR': {'FED': '2026-04-29T18:00'}}
FAM = {'KXCPI': 'CPI', 'KXCPIYOY': 'CPI', 'KXCPICORE': 'CPI', 'KXCPICOREYOY': 'CPI', 'KXPAYROLLS': 'JOBS', 'KXU3': 'JOBS', 'KXFEDDECISION': 'FED', 'KXFED': 'FED'}
for s, fam in FAM.items():
    for suf, rel in REL.items():
        if fam not in rel: continue
        R = int(dt.datetime.fromisoformat(rel[fam]).replace(tzinfo=dt.timezone.utc).timestamp())
        try: ms = get(K + 'markets?event_ticker=%s-%s&limit=100' % (s, suf))['markets']
        except Exception as ex: print(s, suf, 'ERR', ex); continue
        if not ms: print(s, suf, 'no markets'); continue
        closes = sorted(set(m['close_time'][:16] for m in ms))
        n_pre = n_post = 0; vol_post = 0.0; last = None
        for m in ms:
            t = get(K + 'markets/trades?ticker=%s&limit=1000&min_ts=%d&max_ts=%d' % (m['ticker'], R - 120, R + 300)).get('trades', [])
            for x in t:
                ts = dt.datetime.fromisoformat(x['created_time'].replace('Z', '+00:00')).timestamp()
                if ts < R: n_pre += 1
                else: n_post += 1; vol_post += float(x['count_fp'])
                last = max(last or 0, ts)
        print('%-14s %s markets=%2d close=%s trades R-120..R=%d R..R+300=%d contracts_post=%.0f last=%s' % (
            s, suf, len(ms), closes, n_pre, n_post, vol_post, dt.datetime.utcfromtimestamp(last).strftime('%H:%M:%S') if last else None), flush=True)
