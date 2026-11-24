#!/usr/bin/env python3
"""Guard for Polymarket data-api /v2/trades reads (R-080, 24 Nov 2026). v1 is retired (HTTP 410). v2 silently IGNORES unknown query params
(a typo returns market-wide trades with HTTP 200), so every page is checked: each returned row's condition_id must belong to the request.
No network here."""


def check_rows(data, allowed_conds, what="trades page"):
    """data = list of trade dicts from /v2/trades; allowed_conds = set of condition ids the request asked for (one market, or all markets of one event).
    Raises AssertionError when any row has a missing or foreign condition_id (the filter was ignored or mistyped)."""
    allowed = {str(c).lower() for c in allowed_conds if c}
    if not allowed:
        raise AssertionError("%s: no allowed condition ids given, cannot verify the filter" % what)
    bad = [x for x in data if str(x.get("condition_id") or "").lower() not in allowed]
    if bad:
        raise AssertionError("%s: %d of %d rows have a condition_id outside the request (first: %s); the filter was ignored or mistyped" % (what, len(bad), len(data), bad[0].get("condition_id")))
    return len(data)
