import json, datetime as dt, sys
fr = json.load(open(sys.argv[1]))
def P(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
t0 = P(fr[0]['rfc460Timestamp'])
prev = None
rows = []
pairs = [('bk','blue kills'),('rk','red kills'),('bt','blue towers'),('rt','red towers'),('bd','blue dragons'),('rd','red dragons'),('bb','blue barons'),('rb','red barons'),('bi','blue inhibitors'),('ri','red inhibitors')]
for f in fr:
    b, r = f['blueTeam'], f['redTeam']
    cur = {'bk': b['totalKills'], 'rk': r['totalKills'], 'bt': b['towers'], 'rt': r['towers'], 'bd': len(b['dragons']), 'rd': len(r['dragons']), 'bb': b['barons'], 'rb': r['barons'], 'bi': b['inhibitors'], 'ri': r['inhibitors'], 'bg': b['totalGold'], 'rg': r['totalGold']}
    if prev:
        for k, lab in pairs:
            if cur[k] != prev[k]:
                rows.append((f['rfc460Timestamp'], round((P(f['rfc460Timestamp']) - t0).total_seconds(), 1), lab, prev[k], cur[k], cur['bg'] - cur['rg']))
    prev = cur
print('utc_frame,game_s,event,before,after,gold_diff_blue_minus_red')
for r in rows: print(','.join(str(x) for x in r))
