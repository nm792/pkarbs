import json, gzip, collections, re, sys, datetime as dt
sys.path.insert(0, '..'); sys.path.insert(0, '../..')
import bo3_pull as b
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
ms = json.load(gzip.open('../../raw/bo3/matches_2026-09-01_2026-11-04.json.gz'))
G = json.load(gzip.open('../../raw/esports/gamma_cs2_2026-11-02_04.json.gz'))['cs2']
CH = collections.defaultdict(list)
for l in gzip.open('/home/user/pkarbs/rn1/scores/cs2/server-2026-11/cs2_changes.jsonl.gz', 'rt'):
    d = json.loads(l)
    if '|Bo' in (d.get('score') or ''): CH[d['gameId']].append(d)
titles = json.load(open('../out_cs2_maps.json'))['matches']
rows = []
for e in G:
    if e['title'][:48] not in titles: continue
    ch = sorted(CH[int(e['gameId'])], key=lambda d: d['recv_ms'])
    tn = [norm(t['name']) for t in e['teams']]; st = ts(e['startTime'])
    cand = [m for m in ms if abs(ts(m['start_date']) - st) < 6 * 3600 and any(x[:5] in norm(m['slug']) for x in tn if len(x) >= 3)]
    cand = [m for m in cand if sum(x[:5] in norm(m['slug']) for x in tn) == 2] or cand
    if not cand: print('NO MATCH', e['title'][:50]); continue
    m = cand[0]; gs = b.games(m['id'])
    home = ch[-1]['home'] if ch else None
    # WS: per map index -> list of (recv_s, total_rounds)
    ws = collections.defaultdict(dict)
    for x in ch:
        p = x['score'].split('|')
        try: r = [int(v) for v in p[0].split('-')]; mp = [int(v) for v in p[1].split('-')]
        except Exception: continue
        k = mp[0] + mp[1] + 1; n = r[0] + r[1]
        if n not in ws[k]: ws[k][n] = x['recv_ms'] / 1000
    for g in sorted(gs, key=lambda g: g['number']):
        rs = sorted(g['game_rounds'], key=lambda r: r['round_number'])
        if not rs or not g.get('begin_at'): continue
        t = ts(g['begin_at']); cum = 0
        for r in rs:
            cum += r['round_duration'] / 1e9
            w = ws.get(g['number'], {}).get(r['round_number'])
            rows.append((m['slug'][:30], g['number'], r['round_number'], round(cum), None if w is None else round(w - t)))
json.dump(rows, open('chk_overlap.json', 'w'))
for r in rows: print(*r)
