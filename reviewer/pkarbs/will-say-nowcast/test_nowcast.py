import unittest, nowcast as N

TOK = 'Y'


def w(tw, sf='earnings'):
    return dict(yes_token=TOK, t_w=tw, cond='c', subfam=sf)


def tr(ts, p, s=10, side='BUY', tok=TOK):
    return dict(asset=tok, side=side, price=p, size=s, ts=ts)


class T(unittest.TestCase):
    def test_bracket(self):
        t = [tr(995, .40), tr(1004, .60), tr(1008, .70), tr(1012, .99)]
        m = N.measure(t, w(1000), 0.0)
        self.assertEqual(m['W_ub'], 12); self.assertEqual(m['W_lb'], 8)
        self.assertEqual(m['usd'][5], 7.0)    # only the 1008 print is at or after 1005.25
        self.assertEqual(m['usd'][2], 13.0)   # 1004 and 1008 are after 1002.25

    def test_hold_boundary(self):
        t = [tr(1005, .60)]
        self.assertEqual(N.measure(t, w(1000), 0.0)['usd'][5], 0.0)     # 1005 < 1005.25
        t = [tr(1005.25, .60)]
        self.assertEqual(N.measure(t, w(1000), 0.0)['usd'][5], 6.0)

    def test_leak(self):
        m = N.measure([tr(980, .99), tr(1003, .50)], w(1000), 0.0)
        self.assertTrue(m['leak']); self.assertEqual(m['W_lb'], 0.0)

    def test_fee_threshold(self):
        self.assertTrue(N.cheap(.97, 0.0)); self.assertFalse(N.cheap(.97, 0.5))   # .97+.5*.97*.03=.9846

    def test_sells_and_other_tokens_ignored(self):
        t = [tr(1010, .50, side='SELL'), tr(1010, .50, tok='N')]
        m = N.measure(t, w(1000), 0.0)
        self.assertEqual(m['usd'][1], 0.0); self.assertIsNone(m['W_ub'])

    def test_plant_stale_recovered(self):
        words = [w(1000 + 1000 * i) for i in range(10)]
        ok, why = N.plant_check([], words, 0.0, 3.0)
        self.assertTrue(ok, why)
        pt, ch = N.plant([], words)
        for i in ch:
            m = N.measure(pt, words[i], 0.0)
            self.assertTrue(2.75 <= m['W_lb'] <= 3.25); self.assertEqual(m['usd'][1], 50.0); self.assertEqual(m['usd'][5], 0.0)

    def test_plant_hold_gives_zero(self):
        words = [w(1000 + 1000 * i) for i in range(10)]
        pt, ch = N.plant([], words, dt_lift=0.25)
        for i in ch:
            self.assertEqual(N.measure(pt, words[i], 0.0)['usd'][1], 0.0)
        self.assertTrue(N.plant_check([], words, 0.0, 0.25)[0])

    def test_plant_check_can_fail(self):
        broken = N.HOLD
        N.HOLD = 0.0                                      # a scorer that ignores the hold must fail the hold plant
        try:
            words = [w(1000 + 1000 * i) for i in range(10)]
            ok, why = N.plant_check([], words, 0.0, 1.1)   # lift at t_w+1.1: real scorer excludes it at L=1 (1.25), broken one counts it
            self.assertFalse(ok)
        finally:
            N.HOLD = broken

    def test_verdict_room_noroom_inconclusive(self):
        room = [dict(W_lb=8, W_ub=20, usd={1: 0, 2: 0, 5: 80, 10: 0, 30: 0}, placebo=[{5: 10}]) for _ in range(20)]
        self.assertEqual(N.verdict(room)['verdict'], 'ROOM')
        no = [dict(W_lb=0, W_ub=1, usd={1: 0, 2: 0, 5: 0, 10: 0, 30: 0}, placebo=[{5: 0}]) for _ in range(20)]
        self.assertEqual(N.verdict(no)['verdict'], 'NO ROOM')
        self.assertEqual(N.verdict(room[:19])['verdict'], 'INCONCLUSIVE')
        flow = [dict(r, placebo=[{5: 500}]) for r in room]              # post-word $ no bigger than ordinary flow
        self.assertEqual(N.verdict(flow)['verdict'], 'INCONCLUSIVE')

    def test_run_no_pooling_and_void(self):
        words = [w(1000 + 10000 * i, 'earnings') for i in range(20)] + [w(500000 + 10000 * i, 'trump') for i in range(3)]
        t = []
        for x in words:
            t += [tr(x['t_w'] + 6, .5, 60), tr(x['t_w'] + 9, .5, 60), tr(x['t_w'] + 15, .99)]
        r = N.run(t, words, lambda c: 0.0)
        self.assertEqual(set(r), {'earnings', 'trump'})
        self.assertEqual(r['earnings']['verdict'], 'ROOM'); self.assertEqual(r['trump']['verdict'], 'INCONCLUSIVE')


if __name__ == '__main__':
    unittest.main()
