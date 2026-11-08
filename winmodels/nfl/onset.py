"""Price-move time for a scoring play: within [anchor-W0, anchor+W1], find the 30 s window with the largest mid change
in the expected direction (sign), then onset = first print that covers 20% of that move. Returns (onset_ts, move)."""
import bisect
def onset(pr, M, anchor, sign, W0=300, W1=120):
    best = (0, None)
    for t in range(int(anchor - W0), int(anchor + W1)):
        a, b = M.at(t - 15), M.at(t + 15)
        if a is None or b is None: continue
        mv = (b - a) * sign
        if mv > best[0]: best = (mv, t)
    if best[1] is None or best[0] < 0.01: return None, 0
    t = best[1]; a = M.at(t - 15); b = M.at(t + 15); tt = [p[0] for p in pr]
    for q in pr[bisect.bisect_left(tt, t - 15):bisect.bisect_right(tt, t + 15)]:
        if (q[2] - a) / (b - a) >= 0.2: return q[0], best[0]
    return t, best[0]
