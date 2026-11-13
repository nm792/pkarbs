# Pre-game team strength: game-level Elo from official series scores (getSchedule), 2024-01 onward.
# Each series counts as gameWins wins/losses applied at the series start; rating used for a game
# is the one BEFORE its series (no leakage). Regional offset learned via international events.
import json, math
K = 24; HOME = 0
def run(matches):
    R = {}; pre = {}
    for m in sorted(matches, key=lambda x: x['start']):
        tid = list(m.get('team_ids', {}).items())
        codes = [c for c, _ in m['teams']]
        # key teams by code+league is fragile; use esports ids when known, else code
        keys = [c for c in codes]
        if m.get('team_ids'):
            inv = {v: k for k, v in m['team_ids'].items()}; keys = [inv.get(c, c) for c in codes]
        a, b = keys; wa, wb = [w or 0 for _, w in m['teams']]
        ra, rb = R.get(a, 1500.0), R.get(b, 1500.0)
        pre[m['match_id']] = {a: ra, b: rb}
        for res in [1] * wa + [0] * wb:
            e = 1 / (1 + 10 ** ((rb - ra) / 400))
            ra += K * (res - e); rb -= K * (res - e)
        R[a], R[b] = ra, rb
    return pre, R
if __name__ == '__main__':
    import sys
    M = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'raw/matches.json'))
    pre, R = run(M)
    json.dump(pre, open('elo_pre.json', 'w'))
    print(len(pre), 'matches rated')
