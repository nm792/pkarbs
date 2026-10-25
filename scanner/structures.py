"""Build MECE structures. Leg ids: 'pm:<clob token id>' (YES or NO token), 'k:<ticker>:yes|no'."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

def _pm(t): return 'pm:' + t
def _ins(name, legs): return dict(name=name, legs=legs)
def _venues(buckets):
    return sorted({l.split(':')[0].replace('k', 'kalshi') for b in buckets for i in b['instruments'] for l in i['legs']})

def _mk(sid, typ, buckets, complete=True, divergence=False, basis='', notes=''):
    return dict(id=sid, type=typ, buckets=buckets, complete=complete, venues=_venues(buckets),
                divergence_loses_both=divergence, basis=basis, notes=notes)

def senate_structures(path=os.path.join(HERE, 'map_senate.json')):
    m = json.load(open(path)); pm = m['pm']; k = m['kalshi']; b = m['basis']
    def pm_side(s):
        return [_ins(n, [_pm(x['yes']) for x in legs]) for n, legs in pm[s].items()]
    # 'not D' on the main market pays on R or Other; 'not R' pays on D or Other.
    notR = _ins('pm main R NO (D or Other)', [_pm(pm['notR_main']['no'])])
    notD = _ins('pm main D NO (R or Other)', [_pm(pm['notD_main']['no'])])
    out = []
    # Polymarket only: {R} + {D or Other} and {D} + {R or Other}. Fully MECE incl. Other.
    out.append(_mk('pm:senate:R+notR', 'synthetic_cover',
                   [dict(name='R', instruments=pm_side('R')), dict(name='D or Other', instruments=[notR])],
                   basis=b['pm'], notes='Combos vs main market; same venue, same Senate wording.'))
    out.append(_mk('pm:senate:D+notD', 'synthetic_cover',
                   [dict(name='D', instruments=pm_side('D')), dict(name='R or Other', instruments=[notD])],
                   basis=b['pm']))
    # Cross-venue (alert-only until Kalshi is tradeable). Basis divergence loses both legs.
    xb = 'PM: ' + b['pm'] + ' | Kalshi: ' + b['kalshi'] + ' | Divergence: ' + b['divergence']
    # Kalshi side of each pair uses disjoint ladders (D YES = D's NO bids, R NO = R's YES bids, ...)
    # and the Polymarket side uses disjoint tokens, so the two pairs never count the same liquidity.
    out.append(_mk('xv:senate:K-D+PM-notD', 'cross_venue',
                   [dict(name='D (Kalshi)', instruments=[_ins('k D YES', [f"k:{k['D']}:yes"]), _ins('k R NO', [f"k:{k['R']}:no"])]),
                    dict(name='R or Other (PM)', instruments=pm_side('R') + [notD])],
                   divergence=True, basis=xb))
    out.append(_mk('xv:senate:K-R+PM-notR', 'cross_venue',
                   [dict(name='R (Kalshi)', instruments=[_ins('k R YES', [f"k:{k['R']}:yes"]), _ins('k D NO', [f"k:{k['D']}:no"])]),
                    dict(name='D or Other (PM)', instruments=pm_side('D') + [notR])],
                   divergence=True, basis=xb))
    return out

def race_structures(path=os.path.join(HERE, 'map_races.json')):
    out = []
    for r in json.load(open(path)):
        b = r['basis']
        out.append(_mk('xv:race:' + r['id'], 'cross_venue',
                       [dict(name=r['candidate'], instruments=[_ins('pm YES', [_pm(r['pm_yes'])]), _ins('k YES', [f"k:{r['kalshi']}:yes"])]),
                        dict(name='not ' + r['candidate'], instruments=[_ins('pm NO', [_pm(r['pm_no'])]), _ins('k NO', [f"k:{r['kalshi']}:no"])])],
                       divergence=True, basis='Kalshi: ' + b['kalshi'] + ' | PM: ' + b['pm'] + ' | ' + b['divergence']))
    return out

def negrisk_set(event):
    """Buy-all-YES set for a Polymarket negRisk event (gamma JSON). Every open market counts,
    placeholders and 'Other' included; if any of them has no asks the set is incomplete and the
    scanner will not alert on it (the AL-04 phantom)."""
    ms = [m for m in event.get('markets', []) if not m.get('closed')]
    legs = []; complete = True
    for m in ms:
        t = json.loads(m['clobTokenIds'])[0]
        legs.append((m.get('groupItemTitle') or m.get('question'), t))
        if not m.get('acceptingOrders'): complete = False
    buckets = [dict(name=n, instruments=[_ins('pm YES', [_pm(t)])]) for n, t in legs]
    return _mk('pm:set:' + event['slug'], 'negrisk_set', buckets, complete=complete and len(legs) >= 2,
               basis='Single negRisk event; exactly one market resolves YES (augmented events add Other).')

def ladder(sid, earlier_no, later_yes, basis=''):
    """Time ladder: 'by date A' implies 'by date B' (A < B). NO(by A) + YES(by B) pays >= $1 in
    every state (pays $2 if it happens between A and B)."""
    return _mk(sid, 'time_ladder',
               [dict(name='happens by B', instruments=[_ins('YES by B', [later_yes])]),
                dict(name='not by A', instruments=[_ins('NO by A', [earlier_no])])], basis=basis)
