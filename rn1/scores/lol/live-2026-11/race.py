# Race Polymarket sports WS (LoL score string) against Riot livestats frames for one live game.
import websocket, json, time, threading, requests, datetime as dt, sys
GIDS = sys.argv[1].split(','); DUR = float(sys.argv[2]); OUT = sys.argv[3]
out = open(OUT, 'w'); lock = threading.Lock()
def w(o):
    with lock: out.write(json.dumps(o) + '\n'); out.flush()
def wsloop():
    end = time.time() + DUR
    while time.time() < end:
        try:
            ws = websocket.create_connection('wss://sports-api.polymarket.com/ws', header=['User-Agent: Mozilla/5.0'], sslopt={'ca_certs': '/root/.ccr/ca-bundle.crt'})
            while time.time() < end:
                s = ws.recv()
                if s == 'ping': ws.send('pong'); continue
                g = json.loads(s)
                if g.get('leagueAbbreviation') == 'lol': w({'src': 'ws', 'recv': time.time(), **g})
        except Exception as e: w({'src': 'wserr', 'recv': time.time(), 'e': str(e)}); time.sleep(2)
def feedloop():
    s = requests.Session(); s.verify = '/root/.ccr/ca-bundle.crt'; end = time.time() + DUR; seen = set()
    while time.time() < end:
      for GID in GIDS:
          st = int((time.time() - 50) // 10 * 10)
          for k in range(3):
              t = dt.datetime.fromtimestamp(st - 10 * k, dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
              try: r = s.get(f'https://feed.lolesports.com/livestats/v1/window/{GID}', params={'startingTime': t}, timeout=10)
              except Exception: continue
              if r.status_code != 400: break
          rc = time.time()
          if r.status_code == 200 and r.content.strip():
              for f in r.json().get('frames') or []:
                  if (GID, f['rfc460Timestamp']) in seen: continue
                  seen.add((GID, f['rfc460Timestamp']))
                  w({'src': 'feed', 'game': GID, 'recv': rc, 'ts': f['rfc460Timestamp'], 'state': f['gameState'],
                     'bk': f['blueTeam']['totalKills'], 'rk': f['redTeam']['totalKills'], 'bt': f['blueTeam']['towers'], 'rt': f['redTeam']['towers'],
                     'bg': f['blueTeam']['totalGold'], 'rg': f['redTeam']['totalGold']})
      time.sleep(1)
a = threading.Thread(target=wsloop); b = threading.Thread(target=feedloop); a.start(); b.start(); a.join(); b.join()
