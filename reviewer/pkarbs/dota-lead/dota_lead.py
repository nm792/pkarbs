#!/usr/bin/env python3
"""TheSports Dota 2 events vs Polymarket Dota own-token books: STANDARD v1 s.2-s.3 lead test
(SPEC-dota-thesports-lead-vs-pmdota-2026-11-25, locked 10:20Z). Offline, read-only. Runs on Prime (R-039).

Core is format-agnostic. The raw-file adapters (TheSports box message -> normalized state; pmdota row -> (t, bid, ask))
are filled in once P124b reports the formats, and get their own tests then.

Normalized state per message: dict(t=<receive time, host clock, s>, match=<key>, towers={A:int,B:int}, roshan={A:int,B:int},
barracks={A:int,B:int}, kills={A:int,B:int}), counts cumulative, credited to the team that MADE the event.
Events (fixed before data): tower, roshan, barracks (count +1 for team X), fight (net kill change >= 3 for X within 20 s).
Token = the game-winner token of the team that made the event; direction +1 (its mid should rise).
Onset (STANDARD s.2): base = last mid at or before t-60; onset = first time in [t-60, t+60] with mid - base >= 2c. Lead = onset - t."""
import random, statistics, bisect, zlib

WIN, MOVE, FIGHT_N, FIGHT_S = 60.0, 0.02, 3, 20.0
PLANT_AT, PLANT_C = 5.0, 0.03


def events_from_states(states):
    """states: normalized dicts of ONE match, any order. Returns [(t, type, team)]."""
    s = sorted(states, key=lambda x: x['t'])
    ev = []
    for a, b in zip(s, s[1:]):
        for typ in ('towers', 'roshan', 'barracks'):
            for tm in ('A', 'B'):
                d = b[typ][tm] - a[typ][tm]
                ev += [(b['t'], {'towers': 'tower', 'roshan': 'roshan', 'barracks': 'barracks'}[typ], tm)] * max(0, d)
    kt = [(x['t'], x['kills']['A'] - x['kills']['B']) for x in s]
    last = {'A': -1e18, 'B': -1e18}
    for i, (t, net) in enumerate(kt):
        lo = bisect.bisect_left([u for u, _ in kt], t - FIGHT_S)
        base = min(kt[lo:i + 1], key=lambda x: x[1])[1], max(kt[lo:i + 1], key=lambda x: x[1])[1]
        for tm, sw in (('A', net - base[0]), ('B', base[1] - net)):
            if sw >= FIGHT_N and t - last[tm] > FIGHT_S:
                ev.append((t, 'fight', tm)); last[tm] = t
    return sorted(ev)


class Mid:
    def __init__(self, rows):   # rows: (t, bid, ask) of ONE token's own book
        r = sorted((t, (b + a) / 2) for t, b, a in rows if b is not None and a is not None)
        self.t = [x[0] for x in r]; self.m = [x[1] for x in r]

    def at(self, t):
        i = bisect.bisect_right(self.t, t) - 1
        return self.m[i] if i >= 0 else None

    def onset(self, t, sign=1):
        base = self.at(t - WIN)
        if base is None:
            return None
        i = bisect.bisect_right(self.t, t - WIN)
        while i < len(self.t) and self.t[i] <= t + WIN:
            if sign * (self.m[i] - base) >= MOVE - 1e-12:
                return self.t[i]
            i += 1
        return None


def lead(mid, t, sign=1):
    o = mid.onset(t, sign)
    return None if o is None else o - t


def planted(rows, times, delta=PLANT_C, at=PLANT_AT):
    """MC type 2: copy of (t, bid, ask) rows with a +delta step from t+at onward (until t+at+WIN), plus a row at each t+at."""
    def sh(x): return sum(delta for t in times if t + at <= x < t + at + WIN)
    out = [(t, None if b is None else b + sh(t), None if a is None else a + sh(t)) for t, b, a in rows]
    base = {x[0]: x for x in rows}
    for t in times:
        tt = t + at
        prev = max((r for r in rows if r[0] <= tt), key=lambda r: r[0], default=None)
        if prev is not None and tt not in base:
            out.append((tt, prev[1] + sh(tt), prev[2] + sh(tt)))
    return sorted(out)


def placebo_times(ev_times, span, k=10, seed=0):
    """MC type 1: k random times in span=(t0, t1) with no event within +-WIN."""
    rng, out, tries = random.Random(seed), [], 0
    while len(out) < k and tries < 10000:
        tries += 1
        t = rng.uniform(span[0] + WIN, span[1] - WIN)
        if all(abs(t - e) > WIN for e in ev_times):
            out.append(t)
    return out


def boot_ci(per_match, nb=5000, seed=11):
    """per_match: {match: (real_leads, placebo_leads)} -> 95% CI of median(real)-median(placebo), resampled by match."""
    rng, keys, st = random.Random(seed), list(per_match), []
    for _ in range(nb):
        pick = [rng.choice(keys) for _ in keys]
        r = [x for k in pick for x in per_match[k][0]]; p = [x for k in pick for x in per_match[k][1]]
        if r and p:
            st.append(statistics.median(r) - statistics.median(p))
    st.sort()
    return (st[int(.025 * len(st))], st[int(.975 * len(st)) - 1]) if st else (None, None)


def bar(per_match):
    """STANDARD v1 s.3. per_match {match: (real_leads, placebo_leads)} for ONE event type (or pooled)."""
    real = [x for r, _ in per_match.values() for x in r]; plc = [x for _, p in per_match.values() for x in p]
    n = len(real)
    if n < 30:
        return dict(verdict='unknown (n<30)', n=n)
    d = statistics.median(real) - (statistics.median(plc) if plc else 0.0)
    lo, hi = boot_ci(per_match)
    after = sum(1 for x in real if x > 0) / n
    ok = d >= 2.0 and lo is not None and lo > 0 and after >= 0.60
    return dict(verdict='PASS (pending s.4 audit)' if ok else 'no lead', n=n, median_real_minus_placebo_s=d, ci95=(lo, hi), share_price_after=after)


def run(matches, plant=False, seed=1):
    """matches: {key: dict(states=[...], books={'A': rows, 'B': rows})}. Returns per-type and pooled results; plant check void flag."""
    rng = random.Random(seed)
    by_type, chosen_ok = {}, []
    for mk, M in matches.items():
        ev = events_from_states(M['states'])
        if not ev:
            continue
        times = [t for t, _, _ in ev]
        span = (min(s['t'] for s in M['states']), max(s['t'] for s in M['states']))
        books = dict(M['books'])
        pl_ev = set()
        if plant:
            pl_ev = {i for i in range(len(ev)) if rng.random() < .5}
            for tm in ('A', 'B'):
                books[tm] = planted(books[tm], [ev[i][0] for i in pl_ev if ev[i][2] == tm])
        mids = {tm: Mid(books[tm]) for tm in ('A', 'B')}
        pt = placebo_times(times, span, seed=zlib.crc32(str(mk).encode()))
        prng = random.Random(zlib.crc32(str(mk).encode()))
        plc = [l for l in (lead(mids[prng.choice('AB')], t, prng.choice((1, -1))) for t in pt) if l is not None]
        for i, (t, typ, tm) in enumerate(ev):
            l = lead(mids[tm], t)
            if plant and i in pl_ev:
                base_l = lead(Mid(M['books'][tm]), t)
                if base_l is None or base_l > PLANT_AT:
                    chosen_ok.append(l is not None and abs(l - PLANT_AT) <= 1.0)
            if l is None:
                continue
            r, p = by_type.setdefault(typ, {}).setdefault(mk, ([], plc))
            r.append(l)
    res = {typ: bar(pm) for typ, pm in by_type.items()}
    if by_type and all(v.get('n', 0) >= 30 for v in res.values()):
        pooled = {}
        for pm in by_type.values():
            for mk, (r, p) in pm.items():
                pooled.setdefault(mk, ([], p))[0].extend(r)
        res['pooled'] = bar(pooled)
    if plant:
        res['plant_ok'] = bool(chosen_ok) and all(chosen_ok)
    return res


# ---- pmdota adapter (P124b, 25 Nov 22:2xZ: books.YYYYMMDDHH.jsonl.gz rows with recv_ms, token, outcome, q, cond, bid, ask, bids, asks) ----
def load_pmdota(paths):
    """-> {cond: dict(q=question, tokens={outcome_label: [(t_s, bid, ask)]})}. Each token keeps ONLY its own rows (SETTLED A1);
    rows with a missing side keep None for that side (Mid skips them). recv_ms is our host clock."""
    import gzip, json
    out = {}
    for p in paths:
        op = gzip.open if p.endswith('.gz') else open
        with op(p, 'rt') as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                c = out.setdefault(r['cond'], dict(q=r.get('q'), tokens={}, token_ids={}))
                lab = r.get('outcome')
                c['token_ids'].setdefault(lab, r['token'])
                if c['token_ids'][lab] != r['token']:
                    raise ValueError('two token ids for one outcome label in %s' % r['cond'])
                f2 = lambda v: None if v in (None, '') else float(v)
                c['tokens'].setdefault(lab, []).append((r['recv_ms'] / 1000.0, f2(r.get('bid')), f2(r.get('ask'))))
    return out
