"""Prints, for each NBA game starting in the next 36 h, the IT command for trade_feed_probe.js with that game's YES and NO moneyline token ids (Gamma series 10345, game events only).
Read-only. Run on any host with Gamma access; paste the output to IT. The probe must run DURING play, ideally 10-25 minutes after tip-off (prints exist; the 15-min window of R-092 C2)."""
import json, urllib.request, gzip, re, datetime, sys
def gj(u):
    b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'pkarbs', 'Accept-Encoding': 'gzip'}), timeout=40).read()
    try: b = gzip.decompress(b)
    except Exception: pass
    return json.loads(b)
rx = re.compile(r'^nba-[a-z0-9]+-[a-z0-9]+-\d{4}-\d\d-\d\d$')
ev = []
for off in range(0, 1500, 50):
    d = gj(f'https://gamma-api.polymarket.com/events?series_id=10345&closed=false&limit=50&offset={off}'); ev += d
    if len(d) < 50: break
now = datetime.datetime.now(datetime.timezone.utc); out = []
for e in ev:
    if not rx.match(e.get('slug', '')) or e.get('ended'): continue
    for m in e.get('markets', []):
        if m.get('sportsMarketType') != 'moneyline': continue
        toks = json.loads(m['clobTokenIds']); oc = json.loads(m['outcomes'])
        st = m.get('gameStartTime') or e.get('startTime')
        t = datetime.datetime.fromisoformat(st.replace('Z', '+00:00')) if st else None
        if len(toks) != 2 or not t or not (now - datetime.timedelta(hours=3) <= t <= now + datetime.timedelta(hours=36)): continue
        out.append((t, e['slug'], m['conditionId'], oc, toks))
for t, slug, cond, oc, toks in sorted(out):
    print(f'# {slug}  start {t:%Y-%m-%d %H:%MZ}  condition {cond}  outcomes {oc[0]} / {oc[1]}')
    print(f'#   run at {(t + datetime.timedelta(minutes=12)):%H:%MZ} (12 min after tip-off):')
    print(f'node trade_feed_probe.js {toks[0]} {toks[1]} 60')
