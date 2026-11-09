"""NBA feed-delay capture (read-only, stdlib only). For each live NBA game, polls
  (a) NBA official liveData play-by-play on its S3 origin (every 1 s, ETag conditional GET): each action has timeActual (ms)
  (b) ESPN summary (every 2 s): each play has wallclock (1 s)
and writes one JSONL row per NEW action/play with our receive time. Polymarket sports WS is already logged by the
cs2-ws-logger (it carries NBA frames); prices come from data-api trades afterwards.
Usage: python3 poll.py OUTDIR START_ISO END_ISO"""
import sys, os, json, time, threading, urllib.request, datetime as dt
OUT, START, END = sys.argv[1], sys.argv[2], sys.argv[3]
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
T0, T1 = ts(START), ts(END)
S3 = 'https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/liveData'
ESPN = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba'
UA = {'User-Agent': 'Mozilla/5.0 (pkarbs research)'}
os.makedirs(OUT, exist_ok=True); lock = threading.Lock()
F = {k: open(os.path.join(OUT, f'{k}.jsonl'), 'a') for k in ('nba_actions', 'espn_plays', 'polls', 'log')}
def w(k, row):
    with lock: F[k].write(json.dumps(row) + '\n'); F[k].flush()
def now_ms(): return int(time.time() * 1000)
def get(url, etag=None, timeout=10):
    h = dict(UA)
    if etag: h['If-None-Match'] = etag
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout)
        return r.status, r.headers.get('ETag'), r.headers.get('Last-Modified'), r.read()
    except urllib.error.HTTPError as e: return e.code, None, None, b''
    except Exception as e: return -1, None, None, str(e).encode()[:200]
def nba_game(gid):
    url = f'{S3}/playbyplay/playbyplay_{gid}.json'; etag = None; seen = {}; n = 0
    while time.time() < T1:
        t = time.time(); c, et, lm, body = get(url, etag); rm = now_ms(); n += 1
        if n % 30 == 0 or c not in (200, 304): w('polls', dict(recv_ms=rm, src='nba', gid=gid, code=c, lm=lm))
        if c == 200:
            etag = et
            try: d = json.loads(body)['game']
            except Exception: d = None
            if d:
                for a in d.get('actions', []):
                    key = (a.get('actionNumber'), a.get('scoreHome'), a.get('scoreAway'))
                    if key in seen: continue
                    seen[key] = 1
                    w('nba_actions', dict(recv_ms=rm, lm=lm, gid=gid, n=a.get('actionNumber'), t=a.get('timeActual'), per=a.get('period'), clk=a.get('clock'),
                                         typ=a.get('actionType'), h=a.get('scoreHome'), a=a.get('scoreAway'), ed=a.get('edited')))
                if d.get('gameStatus') == 3 or any(a.get('actionType') == 'game' for a in d.get('actions', [])[-3:]):
                    w('log', dict(recv_ms=rm, msg=f'nba game {gid} final')); return
        time.sleep(max(0, 1.0 - (time.time() - t)))
def espn_game(eid):
    url = f'{ESPN}/summary?event={eid}'; seen = set(); n = 0
    while time.time() < T1:
        t = time.time(); c, _, lm, body = get(url, timeout=15); rm = now_ms(); n += 1
        if n % 30 == 0 or c != 200: w('polls', dict(recv_ms=rm, src='espn', eid=eid, code=c, lm=lm))
        if c == 200:
            try: d = json.loads(body)
            except Exception: d = None
            if d:
                for p in d.get('plays') or []:
                    key = (p.get('id'), p.get('homeScore'), p.get('awayScore'))
                    if key in seen: continue
                    seen.add(key)
                    w('espn_plays', dict(recv_ms=rm, eid=eid, id=p.get('id'), wc=p.get('wallclock'), per=(p.get('period') or {}).get('number'),
                                        clk=(p.get('clock') or {}).get('displayValue'), h=p.get('homeScore'), a=p.get('awayScore'), sc=p.get('scoringPlay')))
                st = (((d.get('header') or {}).get('competitions') or [{}])[0].get('status') or {}).get('type') or {}
                if st.get('completed'): w('log', dict(recv_ms=rm, msg=f'espn game {eid} final')); return
        time.sleep(max(0, 2.0 - (time.time() - t)))
started = set()
while time.time() < T0: time.sleep(5)
w('log', dict(recv_ms=now_ms(), msg='start'))
while time.time() < T1:
    c, _, _, body = get(f'{S3}/scoreboard/todaysScoreboard_00.json')
    if c == 200:
        for g in json.loads(body)['scoreboard']['games']:
            if g.get('gameStatus') == 2 and ('n', g['gameId']) not in started:
                started.add(('n', g['gameId'])); threading.Thread(target=nba_game, args=(g['gameId'],), daemon=True).start()
                w('log', dict(recv_ms=now_ms(), msg=f"nba start {g['gameId']} {g['awayTeam']['teamTricode']}@{g['homeTeam']['teamTricode']}"))
    else: w('log', dict(recv_ms=now_ms(), msg=f'nba scoreboard {c}'))
    c, _, _, body = get(f'{ESPN}/scoreboard')
    if c == 200:
        for e in json.loads(body).get('events', []):
            if e['status']['type'].get('state') == 'in' and ('e', e['id']) not in started:
                started.add(('e', e['id'])); threading.Thread(target=espn_game, args=(e['id'],), daemon=True).start()
                w('log', dict(recv_ms=now_ms(), msg=f"espn start {e['id']} {e['shortName']}"))
    else: w('log', dict(recv_ms=now_ms(), msg=f'espn scoreboard {c}'))
    time.sleep(15)
w('log', dict(recv_ms=now_ms(), msg='end'))
