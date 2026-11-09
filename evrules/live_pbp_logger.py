"""Live logger for ESPN cricket ball-by-ball and rugby scoring events.

ESPN's public site API gives cricket commentary ball by ball
(/sports/cricket/<any league>/playbyplay?event=<cricinfo id>) and rugby
scoring events (scoreboard 'details'), but with no wall-clock time per
ball or score. So we poll and stamp our own receive time, which is what a
live trading feed needs anyway.

Bounded run: one process, polls every --every seconds, stops after
--minutes. Writes jsonl to --out (scratch), and copies it to --share every
10 min.
  python3 -m evrules.live_pbp_logger cricket 1558591 --minutes 240
  python3 -m evrules.live_pbp_logger rugby 270559 --minutes 150   (league id)
"""
import argparse, json, os, shutil, subprocess, time

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
API = 'https://site.api.espn.com/apis/site/v2/sports'


def get(url):
    r = subprocess.run(['curl', '-sS', '--compressed', '-m', '15', '-A', UA, url], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def cricket_items(ev):
    first = get(f'{API}/cricket/8039/playbyplay?event={ev}')
    if not first or 'commentary' not in first: return []
    pc = first['commentary'].get('pageCount', 1) or 1
    last = first if pc == 1 else get(f'{API}/cricket/8039/playbyplay?event={ev}&page={pc}')
    items = (last or {}).get('commentary', {}).get('items', [])
    if pc > 1 and len(items) < 6:   # page just rolled over: include the previous page too
        prev = get(f'{API}/cricket/8039/playbyplay?event={ev}&page={pc - 1}')
        items = (prev or {}).get('commentary', {}).get('items', []) + items
    return [dict(id=x.get('id'), seq=x.get('sequence'), over=(x.get('over') or {}).get('overs'),
                 inn=x.get('period'), home=x.get('homeScore'), away=x.get('awayScore'),
                 play=(x.get('playType') or {}).get('description'), score_value=x.get('scoreValue'),
                 text=x.get('shortText')) for x in items]


def rugby_items(league):
    d = get(f'{API}/rugby/{league}/scoreboard')
    out = []
    for e in (d or {}).get('events', []):
        c = e['competitions'][0]; st = e['status']
        if st['type']['state'] != 'in': continue
        sc = {x['homeAway']: x.get('score') for x in c['competitors']}
        out.append(dict(id=f"{e['id']}|{sc.get('home')}-{sc.get('away')}|{len(c.get('details', []))}", event=e['id'],
                        name=e['name'], home=sc.get('home'), away=sc.get('away'), clock=st.get('displayClock'),
                        period=st.get('period'), n_details=len(c.get('details', [])),
                        last=(c.get('details') or [{}])[-1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sport', choices=['cricket', 'rugby'])
    ap.add_argument('ids', nargs='+', help='cricinfo match ids (cricket) or ESPN league ids (rugby)')
    ap.add_argument('--minutes', type=float, default=240)
    ap.add_argument('--every', type=float, default=5)
    ap.add_argument('--out', default='.')
    ap.add_argument('--share', default='/mnt/project-files/ev-rules/raw/live')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.share, exist_ok=True)
    fn = os.path.join(a.out, f"{a.sport}_{'_'.join(a.ids)}_{time.strftime('%Y%m%dT%H%MZ', time.gmtime())}.jsonl")
    seen = set(); end = time.time() + a.minutes * 60; last_copy = 0; polls = fails = 0
    with open(fn, 'a') as f:
        while time.time() < end:
            for i in a.ids:
                t0 = time.time()
                items = cricket_items(i) if a.sport == 'cricket' else rugby_items(i)
                polls += 1; fails += (not items)
                for x in items:
                    k = (i, x['id'])
                    if k in seen: continue
                    seen.add(k)
                    x.update(src_id=i, recv_ms=int(t0 * 1000), recv_iso=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(t0)) + f'.{int(t0 * 1000) % 1000:03d}Z',
                             first_poll=len(seen) <= len(items))
                    f.write(json.dumps(x) + '\n')
                f.flush()
            if time.time() - last_copy > 600:
                shutil.copy(fn, a.share); last_copy = time.time()
            time.sleep(max(0.0, a.every - (time.time() - t0)))
    shutil.copy(fn, a.share)
    print(json.dumps(dict(file=fn, polls=polls, empty_polls=fails, rows=len(seen))))


if __name__ == '__main__':
    main()
