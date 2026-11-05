"""Race NHL api-web endpoints for score changes (5 Nov 2026): play-by-play, landing, boxscore, score/<date>,
each polled 1 s with a cache-busting query. Writes OUT/race.jsonl rows {ep, id, recv_ms, away, home} on score change.
Usage: endpoint_race.py OUT HOURS DATE GAMEID [GAMEID ...]"""
import json, os, sys, time, ssl, urllib.request, threading
OUT, HOURS, DATE, IDS = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4:]
os.makedirs(OUT, exist_ok=True); END = time.time() + HOURS * 3600; lock = threading.Lock()
f = open(f'{OUT}/race.jsonl', 'a', buffering=1)
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 pkarbs-nhl'}), timeout=10) as r: return json.loads(r.read())
def poll(ep, url, pick):
    last = {}
    while time.time() < END:
        t0 = time.time()
        try:
            d = get(url + ('&' if '?' in url else '?') + f'cb={int(t0*1000)}'); R = int(time.time() * 1000)
            for gid, a, h in pick(d):
                if last.get(gid) != (a, h):
                    last[gid] = (a, h)
                    with lock: f.write(json.dumps(dict(ep=ep, id=gid, recv_ms=R, away=a, home=h)) + '\n')
        except Exception as e:
            with lock: f.write(json.dumps(dict(ep=ep, err=repr(e)[:200], recv_ms=int(time.time()*1000))) + '\n')
            time.sleep(2)
        time.sleep(max(0, 1 - (time.time() - t0)))
ths = []
for gid in IDS:
    one = lambda d, gid=gid: [(gid, d['awayTeam'].get('score'), d['homeTeam'].get('score'))]
    for ep in ('play-by-play', 'landing', 'boxscore'):
        ths.append(threading.Thread(target=poll, args=(ep, f'https://api-web.nhle.com/v1/gamecenter/{gid}/{ep}', one)))
ths.append(threading.Thread(target=poll, args=('score-date', f'https://api-web.nhle.com/v1/score/{DATE}',
           lambda d: [(str(g['id']), g.get('awayTeam', {}).get('score'), g.get('homeTeam', {}).get('score')) for g in d.get('games', []) if str(g['id']) in IDS])))
for t in ths: t.daemon = True; t.start()
while time.time() < END: time.sleep(5)
