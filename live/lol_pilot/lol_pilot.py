"""Capped LoL event-only live pilot (Polymarket), built on the CS2 pilot (live/cs2_pilot/pilot.py, PRs #51/#53).

Rule (= rn1/scores/lol/bidsim/kills_only.py, the backtest of what the free Polymarket sports WS can show):
  After a kill-count change on the Polymarket sports WebSocket (score 'homeKills-awayKills|homeGames-awayGames|BoN'),
  for W=30 s, rest a post-only BUY at the token's book mid x (1 - 0.025), rounded UP to the tick (never below market - 2.5%), on the side whose model
  jump is >= 1c and has not yet shown in the mid since 30 s before the WS update. Never at or above the best ask.
  Place only when fair - bid >= E (fair = base mid + jump). Hold to resolution. Position-taking, not market making.
  Jump: P(home wins game) = sigmoid(logit(base) + 0.284 x net kill change for home), base = mid 30 s before the WS
  update (the WS shows kills ~12 s after the price moves, 4 Nov GEN-LYON measurement, so the base must predate that).
  0.284 = kills beta (logit per kill, mean of leave-one-league-out fits) from out_kills_only.txt.
  Markets: only 'Game k Winner' for the game in play (the backtest traded per-game markets only). Match Winner,
  handicaps and props are not traded. Events: Worlds / MSI titles only (default), volume >= $20k.
  Skipped: net-zero kill changes (trades), anchors outside 3-97c, game-end resets, game-count changes.

Caps (hard, inherited from the CS2 pilot): 5 shares per order (Polymarket minimum), $5 per match, total loss limit
  $20 by default (the CS2 pilot keeps its own $40 on the same $50 account; LoL is sized so both fit), realized P&L
  <= -limit halts. State persists in OUT/state.json. Live needs the trade-only session key, geoblock pass, heartbeat
  and OUT/LIVE_OK written by a person. Logs and report: same format as the CS2 pilot (use ../cs2_pilot/report.py;
  its 'round events' = kill events here).
"""
import argparse, asyncio, json, math, os, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'cs2_pilot'))
import pilot as BASE          # noqa: E402  (CS2 pilot: orders, caps, books, paper fills, markouts, resolution, heartbeat)
import model as MD            # noqa: E402  (score parser + team-name match only)

LOL_SERIES = '10311'
EVENTS = ['worlds', 'msi', 'mid-season invitational']
KILLS_BETA = 0.284            # rn1/scores/lol/bidsim/out_kills_only.txt, event betas['kills']
MAX_KILLS_STEP = 10           # bigger jumps in one WS update are treated as feed glitches
BASE.CFG.update(LOSS_LIMIT_USD=20.0, MATCH_CAP_USD=5.0, SHARE_CAP=5)
BASE.UA = 'Mozilla/5.0 pkarbs-lol-pilot'
CFG = BASE.CFG


def sig(x): return 1 / (1 + math.exp(-x))
def logit(p): return math.log(p / (1 - p))


def kill_event(prev, new):
    """Classify a WS score change. ('kill', k, dk_home) when kills rose inside game k with the game count unchanged and
    the net kill change for home dk_home != 0; ('trade', k, 0) for a net-zero change; ('game_end', k, 0) when the game
    count rises; ('reset', k, 0) when kills go back to 0-0 with games unchanged; (None, None, 0) otherwise."""
    if prev is None or new is None: return None, None, 0
    k = prev['ma'] + prev['mb'] + 1
    dm = (new['ma'] + new['mb']) - (prev['ma'] + prev['mb'])
    if dm > 0: return 'game_end', k, 0
    if dm < 0: return None, None, 0
    if new['ra'] == 0 and new['rb'] == 0 and prev['ra'] + prev['rb'] > 0: return 'reset', k, 0
    dh, da = new['ra'] - prev['ra'], new['rb'] - prev['rb']
    if dh < 0 or da < 0 or dh + da == 0 or dh + da > MAX_KILLS_STEP: return None, None, 0
    if dh == da: return 'trade', k, 0
    return 'kill', k, dh - da


def game_jump(p_home, dk_home):
    """Model change in P(home wins the game) for a net kill change, from base home price p_home."""
    return sig(logit(p_home) + KILLS_BETA * dk_home) - p_home


_aget0 = BASE.aget
RTT = {}                       # last round-trip (s) per host, for the speed report


async def _aget_timed(url, body=None):
    t0 = time.time()
    try: return await _aget0(url, body)
    finally:
        RTT[url.split('/')[2]] = round(time.time() - t0, 3)
BASE.aget = _aget_timed        # base methods call BASE.aget at runtime, so they are timed too


class Pilot(BASE.Pilot):
    """Speed measurement (Nick 5 Nov 02:20Z, dry only until he sees it): every book poll is saved to OUT/books.jsonl
    (top 10 bids of each token = full ladder at 1 s, plus the poll round trip), so each paper bid's queue ahead and
    later fills can be rebuilt; every window/order row carries ws_recv, decided and poll RTT timestamps."""
    def __init__(s, a):
        super().__init__(a)
        s.bookf = open(os.path.join(s.out, 'books.jsonl'), 'a', buffering=1)

    async def manage(s, m, T):
        if m.book:
            row = dict(t=round(T, 3), gid=m.gid, kind=m.kind, rtt=RTT.get('clob.polymarket.com'), mid=m.mid())
            for i, b in m.book.items():
                bb, ba, lv = b
                row[f'b{i}'] = sorted(((p, q) for p, q in (lv or {}).items()), reverse=True)[:10]
                row[f'ask{i}'] = ba
            s.bookf.write(json.dumps(row) + '\n')
        w = m.window
        if w is not None and 'first_manage' not in w:
            w['first_manage'] = T
            s.log('decision', eid=w['eid'], kind=m.kind, ws_recv=w['R'], first_book_after_ws=round(T - w['R'], 3),
                  rtt_clob=RTT.get('clob.polymarket.com'))
        await super().manage(m, T)

    async def discover(s):
        smin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(BASE.now() - 14 * 86400)); evs = []
        for off in range(0, 1000, 100):
            q = urllib.parse.urlencode(dict(series_id=LOL_SERIES, closed='false', start_date_min=smin, limit=100, offset=off))
            try: page = await BASE.aget(f'{BASE.GAMMA}/events?{q}')
            except Exception as e: s.log('error', where='discover', err=repr(e)); return
            evs += page or []
            if not page or len(page) < 100: break
        horizon = BASE.now() + 3600; n_new = 0
        for ev in evs:
            gid = ev.get('gameId')
            if not gid or int(gid) in s.games: continue
            st = ev.get('startTime') or ''
            try: st_t = time.mktime(time.strptime(st[:19], '%Y-%m-%dT%H:%M:%S')) - time.timezone
            except Exception: continue
            if st_t > horizon or st_t < BASE.now() - 8 * 3600: continue
            title = ev['title'].lower(); vol = float(ev.get('volume') or 0)
            if not any(k in title for k in EVENTS) or vol < CFG['MIN_EVENT_VOL']: continue
            g = BASE.Game(int(gid), ev); s.games[int(gid)] = g; n_new += 1
            s.log('discover', gid=int(gid), title=ev['title'], vol=round(vol), start=st)
        if n_new: s.log('discover_done', tracked=len(s.games))

    def attach_markets(s, g):
        for m in g.ev.get('markets') or []:
            t = m.get('groupItemTitle') or ''
            kind = None
            if t.startswith('Game ') and t.endswith(' Winner') and t[5:-7].isdigit(): kind = 'game' + t[5:-7]
            if not kind or kind in g.markets or not m.get('clobTokenIds'): continue
            mk = BASE.Market(g.gid, kind, m, g.home); g.markets[kind] = mk
            s.log('market', gid=g.gid, kind=kind, cond=mk.cond, outcomes=mk.outcomes, o0_home=mk.o0_home, ok=mk.ok,
                  home=g.home, away=g.away, tick=mk.tick, min_size=mk.min_size, reb=mk.reb)

    async def refresh_markets(s, g):
        """Game 4/5 markets can be listed after discovery: re-read the event and attach new game markets."""
        try: evs = await BASE.aget(f"{BASE.GAMMA}/events?slug={g.slug}")
        except Exception as e: s.log('error', where='refresh', err=repr(e)); return
        if evs: g.ev = evs[0]; s.attach_markets(g)

    async def ws_loop(s):
        import websockets
        while not s.stop:
            try:
                async with websockets.connect(BASE.SPORTS_WS, ssl=BASE._ctx(), user_agent_header=BASE.UA, open_timeout=20,
                                              ping_interval=None, max_size=2 ** 22) as ws:
                    s.log('ws_open')
                    while not s.stop:
                        msg = await asyncio.wait_for(ws.recv(), 60)
                        if msg == 'ping': await ws.send('pong'); continue
                        try: d = json.loads(msg)
                        except Exception: continue
                        if d.get('leagueAbbreviation') == 'lol': s.on_score(d, BASE.now())
            except Exception as e:
                s.log('ws_error', err=repr(e)); await asyncio.sleep(1)

    def on_score(s, d, R):
        gid = d.get('gameId'); g = s.games.get(gid)
        if g is None: return
        g.last_ws = R; g.live = bool(d.get('live'))
        if g.home is None:
            g.home, g.away = d.get('homeTeam'), d.get('awayTeam'); s.attach_markets(g)
        new = MD.parse(d.get('score'))
        if new is None or (g.state and new == g.state['raw']): return
        s.log('ws_score', gid=gid, score=d.get('score'), period=d.get('period'), status=d.get('status'))
        prev = g.state['s'] if g.state else None
        kind, k, dk = kill_event(prev, new)
        g.state = dict(s=dict(prev) if kind == 'reset' else dict(new), raw=new)
        if kind != 'kill':
            if kind: s.log('event_skip', gid=gid, kind=kind, map=k)
            if kind in ('game_end', 'reset'): asyncio.ensure_future(s.refresh_markets(g))
            return
        mk = g.markets.get(f'game{k}')
        s.nid += 1; eid = f'{gid}-{s.nid}'
        s.log('event', eid=eid, gid=gid, map=k, prev=prev, new=new, dk_home=dk)
        if mk is None:
            s.log('window_skip', eid=eid, kind=f'game{k}', why='no market for this game'); asyncio.ensure_future(s.refresh_markets(g)); return
        if not mk.ok: s.log('window_skip', eid=eid, kind=mk.kind, why='team names do not match outcomes'); return
        base = mk.mid_at(R - CFG['PRE'])
        if base is None:
            s.log('window_skip', eid=eid, kind=mk.kind, why='no mid history'); return
        ph = base if mk.o0_home else 1 - base
        if not (0.03 < ph < 0.97):
            s.log('window_skip', eid=eid, kind=mk.kind, base=base, why='anchor outside 3-97c'); return
        jh = game_jump(ph, dk); j = jh if mk.o0_home else -jh       # j in token-0 price space, like the CS2 pilot
        s.pending.append((R + 60, 'feed_delay', dict(eid=eid, kind=mk.kind, gid=gid, R=R, j=j)))
        if abs(j) < CFG['MINJ']:
            s.log('window_skip', eid=eid, kind=mk.kind, j=round(j, 4), base=base, why='small jump'); return
        mk.window = dict(eid=eid, R=R, j=j, base=base, end=R + CFG['W'], tok=0 if j > 0 else 1)
        s.log('window', eid=eid, gid=gid, kind=mk.kind, cond=mk.cond, j=round(j, 4), base=base, mid=mk.mid(), tok=mk.window['tok'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['dry', 'live'], default='dry')
    ap.add_argument('--out', default=os.path.expanduser('~/lolpilot/out'))
    ap.add_argument('--hours', type=float, default=8.0)
    ap.add_argument('--share-cap', type=float, default=CFG['SHARE_CAP'])
    ap.add_argument('--match-cap', type=float, default=CFG['MATCH_CAP_USD'])
    ap.add_argument('--loss-limit', type=float, default=CFG['LOSS_LIMIT_USD'])
    a = ap.parse_args(); CFG['HOURS'] = a.hours
    CFG['LOSS_LIMIT_USD'] = a.loss_limit; CFG['SHARE_CAP'] = a.share_cap; CFG['MATCH_CAP_USD'] = min(a.match_cap, a.loss_limit)
    asyncio.run(Pilot(a).main())
