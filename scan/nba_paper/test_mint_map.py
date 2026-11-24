import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
import mint_map as M
bad = []
A, B = 'A', 'B'
def chk(name, cond):
    if not cond: bad.append(name)
# planted same-token SELL print at or below our bid fills; BUY print does not
chk('same-token SELL fills', M.oracle_fills(0.50, 100, M.map_ticks([{'token': A, 'price': 0.49, 'size': 60, 'side': 'SELL', 'ts_event': 1}], A, B)) == 60)
chk('same-token BUY does not fill', M.oracle_fills(0.50, 100, M.map_ticks([{'token': A, 'price': 0.49, 'size': 60, 'side': 'BUY', 'ts_event': 1}], A, B)) == 0)
chk('same-token SELL above our bid does not fill', M.oracle_fills(0.50, 100, M.map_ticks([{'token': A, 'price': 0.51, 'size': 60, 'side': 'SELL', 'ts_event': 1}], A, B)) == 0)
# planted other-token BUY: B bought at 0.52 => A tick at 0.48 SELL: fills our A bid at 0.50 with mapping ON, nothing with mapping OFF
pr = [{'token': B, 'price': 0.52, 'size': 40, 'side': 'BUY', 'ts_event': 2}]
chk('other-token BUY fills with mapping on', M.oracle_fills(0.50, 100, M.map_ticks(pr, A, B, True)) == 40)
chk('other-token BUY gives no fill with mapping off', M.oracle_fills(0.50, 100, M.map_ticks(pr, A, B, False)) == 0)
chk('other-token BUY at 0.40 (A 0.60) does not fill a 0.50 bid', M.oracle_fills(0.50, 100, M.map_ticks([{'token': B, 'price': 0.40, 'size': 40, 'side': 'BUY', 'ts_event': 2}], A, B)) == 0)
chk('other-token SELL is never mapped', len(M.map_ticks([{'token': B, 'price': 0.52, 'size': 40, 'side': 'SELL', 'ts_event': 2}], A, B)) == 0)
# mapped ticks never reach pricing
tk = M.map_ticks(pr, A, B)
chk('mapped tick is fill_only', len(tk) == 1 and tk[0].fill_only)
chk('mapped tick never reaches pricing', M.pricing_view(tk) == [])
# de-dup: same trade on both feeds => counted once
both = pr + [{'token': A, 'price': 0.48, 'size': 40, 'side': 'SELL', 'ts_event': 2}]
tk2 = M.map_ticks(both, A, B)
chk('de-dup keeps one tick', len(tk2) == 1 and not tk2[0].fill_only)
chk('de-dup fills once (40, not 80)', M.oracle_fills(0.50, 100, tk2) == 40)
# different ts_event is NOT a duplicate
chk('different ts_event not de-duplicated', len(M.map_ticks(pr + [{'token': A, 'price': 0.48, 'size': 40, 'side': 'SELL', 'ts_event': 3}], A, B)) == 2)
# post-only at or above the real ask must be rejected (FAIL if accepted)
chk('post-only below ask accepted', M.post_only_ok(0.501, 0.52))
chk('post-only at ask rejected', not M.post_only_ok(0.52, 0.52))
chk('post-only above ask rejected', not M.post_only_ok(0.53, 0.52))
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (15 checks)'); sys.exit(1 if bad else 0)
