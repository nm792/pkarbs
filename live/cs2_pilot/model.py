"""CS2 round model for the event-only pilot (same maths as winmodels/esports/cs2_maps.py and bo3/bo3bt.py, 4 Nov 2026).

pmap(a, b, q): P(team A wins the map | A has a rounds, B has b rounds), MR12 (first to 13), crude lead rule in overtime.
q_from(p):     per-round win rate q that makes pmap(0, 0, q) = p (pre-map price).
series(ma, mb, w): P(A wins a Bo3 | maps ma-mb, A wins the current map with prob w).
Betas (price move over 60 s per unit model move) fitted on the training half of 241 tier-1 matches (out_bo3bt_xfit.json).
"""
import functools, re

BETA_MAP = 0.5703     # out_bo3bt_xfit.json beta.maps
BETA_MATCH = 0.5575   # out_bo3bt_xfit.json beta.match


@functools.lru_cache(maxsize=None)
def pmap(a, b, q):
    if a >= 12 and b >= 12:
        return min(max(0.5 + 0.22 * (a - b), 0.03), 0.97)
    if a >= 13: return 1.0
    if b >= 13: return 0.0
    return q * pmap(a + 1, b, q) + (1 - q) * pmap(a, b + 1, q)


def q_from(p):
    lo, hi = 0.3, 0.7
    for _ in range(30):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if pmap(0, 0, round(m, 3)) < p else (lo, m)
    return round(lo, 3)


def series(ma, mb, w):
    def rest(x, y):
        if x >= 2: return 1.0
        if y >= 2: return 0.0
        return 0.5 * rest(x + 1, y) + 0.5 * rest(x, y + 1)
    return w * rest(ma + 1, mb) + (1 - w) * rest(ma, mb + 1)


def parse(score):
    """'7-4|1-0|Bo3' -> dict(ra=7, rb=4, ma=1, mb=0, bo=3); first number of each pair = home team. None if unparseable."""
    try:
        p = (score or '').split('|')
        r = [int(x) for x in p[0].split('-')]; m = [int(x) for x in p[1].split('-')]
        bo = int(re.sub(r'[^0-9]', '', p[2]) or 0) if len(p) > 2 else 0
        return dict(ra=r[0], rb=r[1], ma=m[0], mb=m[1], bo=bo)
    except Exception:
        return None


def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def same_team(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b) and (a[:5] in b or b[:5] in a)


def round_event(prev, new):
    """Classify a score change. Returns ('round', k) for 1-3 rounds won inside map k with maps unchanged,
    ('map_end', k) when the map count rises, ('reset', k) when rounds go back to 0-0 with maps unchanged (map over,
    winner not shown yet), or (None, None) for anything else. Map-end updates reach the WS minutes late (4 Nov logs:
    12-6 at 10:53, 0-0 at 10:56, maps 1-0 at 10:59), so the pilot trades only 'round' events."""
    if prev is None or new is None: return None, None
    k = prev['ma'] + prev['mb'] + 1
    dm = (new['ma'] + new['mb']) - (prev['ma'] + prev['mb'])
    dr = (new['ra'] + new['rb']) - (prev['ra'] + prev['rb'])
    if dm > 0: return 'map_end', k
    if dm < 0: return None, None
    if new['ra'] == 0 and new['rb'] == 0 and (prev['ra'] + prev['rb']) > 0: return 'reset', k
    if 1 <= dr <= 3 and new['ra'] >= prev['ra'] and new['rb'] >= prev['rb']: return 'round', k
    return None, None


def map_move(prev, new, q):
    """Model change in P(home wins current map) for a within-map round event."""
    return pmap(new['ra'], new['rb'], q) - pmap(prev['ra'], prev['rb'], q)


def match_move(prev, new, q_match=0.5):
    """Model change in P(home wins the match) for a within-map round event. Bo3 uses series(); Bo1 = map model."""
    if prev['bo'] == 1:
        return pmap(new['ra'], new['rb'], q_match) - pmap(prev['ra'], prev['rb'], q_match)
    if prev['bo'] != 3: return None
    return (series(new['ma'], new['mb'], pmap(new['ra'], new['rb'], 0.5))
            - series(prev['ma'], prev['mb'], pmap(prev['ra'], prev['rb'], 0.5)))
