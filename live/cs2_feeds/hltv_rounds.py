"""HLTV scorebot round scores vs Polymarket sports WS round scores (MEIA NOITE vs Damajuana, 4 Nov 2026).
Usage: python3 hltv_rounds.py <hltv raw dir> <cs2_frames.jsonl.gz from rn1/scores/cs2/server-2026-11>
Prints, for each score both feeds show, HLTV first-seen time minus PM WS first-seen time (s). Mac clock checked
against Polymarket book timestamps (median +0.24 s); server clock NTP-synced."""
import gzip, json, sys, os, statistics as st
H = {}
for l in gzip.open(os.path.join(sys.argv[1], 'scorebot.jsonl.gz'), 'rt'):
    d = json.loads(l)
    if d['hltv_id'] != 2400076 or d['ev'] != 'scoreboard' or not d['data'].get('live'): continue
    s = d['data']; sc = {s['terroristTeamName']: s['terroristScore'], s['ctTeamName']: s['counterTerroristScore']}
    H.setdefault((s['mapName'], sc.get('MEIA NOITE'), sc.get('DAMAJUANA')), d['recv_ms'] / 1000)
W = {}
for l in gzip.open(sys.argv[2], 'rt'):
    d = json.loads(l)
    if d.get('homeTeam') != 'MEIA NOITE' or d.get('awayTeam') != 'Damajuana': continue
    sc = d['score'].split('|')[0]
    if '-' not in sc or sc.startswith('000'): continue
    a, b = map(int, sc.split('-')); mp = {'1/3': 'de_inferno', '2/3': 'de_nuke'}.get(d.get('period'))
    W.setdefault((mp, a, b), d['recv_ms'] / 1000)
diffs = [(k, H[k] - W[k]) for k in sorted(H) if k in W]
for k, v in diffs: print(k, round(v, 1))
v = [x for _, x in diffs]
print('n', len(v), 'median', round(st.median(v), 1), 'quartiles', [round(x, 1) for x in st.quantiles(v, n=4)], 'min', round(min(v), 1))
