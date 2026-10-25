"""Phantom filters, applied before a structure may count toward an alert."""

def check(struct, books, now, max_age=90.0):
    """Returns a list of reasons the structure is not alertable right now (empty = clean)."""
    bad = []
    if not struct.get('complete', True):
        bad.append('incomplete: not every outcome is covered (placeholder/Other leg missing or unpriced)')
    legs = {l for b in struct['buckets'] for i in b['instruments'] for l in i['legs']}
    for l in sorted(legs):
        bk = books.get(l)
        if bk is None: bad.append(f'missing {l}'); continue
        if bk.crossed(): bad.append(f'crossed {l}')
        t = bk.ts if bk.ts is not None else bk.fetched
        if t is None or now - t > max_age: bad.append(f'stale {l}')
        if bk.fetched is not None and now - bk.fetched > max_age: bad.append(f'stale fetch {l}')
    return bad

def tradeable(struct, venues_ok):
    legs_venues = set(struct.get('venues', []))
    return legs_venues <= set(venues_ok)
