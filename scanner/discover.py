"""Discovery: turn Polymarket gamma events into candidate structures (negRisk buy-all sets and
auto time ladders). Cheap screen on gamma bestAsk first; only candidates near $1 go to the hot
list whose books are polled every cycle."""
import json, re
from structures import negrisk_set, ladder

def screen_negrisk(events, max_sum=1.005):
    out = []
    for e in events:
        if not e.get('negRisk'): continue
        ms = [m for m in e.get('markets', []) if not m.get('closed')]
        if len(ms) < 2: continue
        s = sum(float(m.get('bestAsk') or 1) for m in ms)
        if s <= max_sum: out.append((s, negrisk_set(e)))
    return [x[1] for x in sorted(out, key=lambda x: x[0])]

BY = re.compile(r'\bby\b|\bbefore\b', re.I)
def auto_ladders(events, max_gap=0.0):
    """Non-negRisk events whose markets are the same question at different deadlines.
    Flags NO(earlier)+YES(later) when gamma asks already sum <= 1 + max_gap. Unreviewed."""
    out = []
    for e in events:
        if e.get('negRisk'): continue
        ms = [m for m in e.get('markets', []) if not m.get('closed') and BY.search(m.get('question') or '')]
        if len(ms) < 2: continue
        ms.sort(key=lambda m: m.get('endDate') or '')
        for a, b in zip(ms, ms[1:]):
            if (a.get('endDate') or '') >= (b.get('endDate') or ''): continue
            ta = json.loads(a['clobTokenIds']); tb = json.loads(b['clobTokenIds'])
            no_a = 1 - float(a.get('bestBid') or 0); yes_b = float(b.get('bestAsk') or 1)
            if no_a + yes_b <= 1 + max_gap:
                s = ladder(f"pm:ladder:{e['slug']}:{a['id']}<{b['id']}", 'pm:' + ta[1], 'pm:' + tb[0],
                           basis='AUTO, UNREVIEWED: check both markets resolve on the same event and source.')
                s['reviewed'] = False; out.append(s)
    return out
