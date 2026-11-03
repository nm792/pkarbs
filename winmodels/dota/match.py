"""Match Polymarket Dota 2 game-winner markets to OpenDota pro matches (team names + time + game number)."""
import json, gzip, re, datetime as dt, collections
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower().replace('team', ''))
def sim(a, b):
    a, b = norm(a), norm(b)
    return bool(a) and bool(b) and (a in b or b in a or a[:5] == b[:5])
ev = json.load(gzip.open('gamma_dota_events.json.gz')); od = json.load(gzip.open('opendota_promatches.json.gz'))
od.sort(key=lambda x: x['start_time'])
out = []; nomatch = 0
for e in ev:
    for m in e['markets']:
        if m.get('sportsMarketType') != 'child_moneyline' or not m.get('closed'): continue
        k = re.search(r'Game (\d+) Winner', m['question'])
        if not k: continue
        k = int(k.group(1)); oc = json.loads(m['outcomes']); op = json.loads(m['outcomePrices'])
        if '1' not in op: continue
        gst = dt.datetime.fromisoformat(m['gameStartTime'].replace('+00', '+00:00')).timestamp()
        c = [x for x in od if gst - 3600 <= x['start_time'] <= gst + 6 * 3600 and
             ((sim(oc[0], x['radiant_name']) and sim(oc[1], x['dire_name'])) or (sim(oc[0], x['dire_name']) and sim(oc[1], x['radiant_name'])))]
        if len(c) < k: nomatch += 1; continue
        x = c[k - 1]; o0_rad = sim(oc[0], x['radiant_name'])
        w0 = op[0] == '1'; ok = (x['radiant_win'] == o0_rad) == w0
        out.append(dict(cond=m['conditionId'], q=m['question'], k=k, gst=gst, match_id=x['match_id'], start=x['start_time'], dur=x['duration'],
                        o0_rad=o0_rad, win0=w0, agree=ok, vol=float(m.get('volume') or 0), league=x['league_name'], fee=m.get('feeSchedule')))
print('matched', len(out), 'nomatch', nomatch, 'winner agree', sum(r['agree'] for r in out))
json.dump(out, open('matched.json', 'w'))
