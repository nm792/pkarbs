import unittest, dota_lead as D


def st(t, tw=(0, 0), ro=(0, 0), ba=(0, 0), k=(0, 0)):
    return dict(t=t, match='m', towers=dict(A=tw[0], B=tw[1]), roshan=dict(A=ro[0], B=ro[1]), barracks=dict(A=ba[0], B=ba[1]), kills=dict(A=k[0], B=k[1]))


def flat(t0, t1, mid=.5, step=1.0):
    out, t = [], t0
    while t <= t1:
        out.append((t, mid - .01, mid + .01)); t += step
    return out


class T(unittest.TestCase):
    def test_events(self):
        s = [st(0), st(10, tw=(1, 0)), st(20, tw=(1, 0), ro=(0, 1)), st(30, tw=(1, 0), ro=(0, 1), ba=(1, 0))]
        self.assertEqual(D.events_from_states(s), [(10, 'tower', 'A'), (20, 'roshan', 'B'), (30, 'barracks', 'A')])

    def test_fight_rule(self):
        s = [st(0), st(5, k=(2, 0)), st(15, k=(3, 0))]          # +3 within 20 s
        self.assertEqual(D.events_from_states(s), [(15, 'fight', 'A')])
        s = [st(0), st(5, k=(2, 0)), st(30, k=(3, 0))]          # +3 over 30 s: not a fight
        self.assertEqual(D.events_from_states(s), [])
        s = [st(0), st(5, k=(1, 0)), st(10, k=(4, 0))]          # single kills alone never count
        self.assertEqual([e[1] for e in D.events_from_states(s)], ['fight'])

    def test_onset_and_lead_sign(self):
        rows = flat(0, 300) ; rows = [(t, b + (.03 if t >= 160 else 0), a + (.03 if t >= 160 else 0)) for t, b, a in rows]
        m = D.Mid(rows)
        self.assertEqual(D.lead(m, 150), 10)       # price after feed: positive
        self.assertEqual(D.lead(m, 170), -10)      # price before feed: negative
        self.assertIsNone(D.lead(m, 150, -1))      # wrong direction: no onset
        self.assertIsNone(D.lead(D.Mid(flat(0, 300)), 150))

    def test_own_book_only(self):
        A = [(t, b + (.05 if t >= 160 else 0), a + (.05 if t >= 160 else 0)) for t, b, a in flat(0, 300)]
        M = {'m': dict(states=[st(0), st(150, tw=(0, 1)), st(400, tw=(0, 1))], books={'A': A, 'B': flat(0, 500)})}
        self.assertNotIn('tower', D.run(M))      # B's event is never priced from A's book move

    def test_plant_recovered(self):
        states = [st(0)] + [st(200 * i, tw=(i, 0)) for i in range(1, 41)] + [st(8400, tw=(40, 0))]
        M = {'m': dict(states=states, books={'A': flat(0, 8500), 'B': flat(0, 8500)})}
        r = D.run(M, plant=True)
        self.assertTrue(r['plant_ok'])

    def test_plant_check_can_fail(self):
        states = [st(0)] + [st(200 * i, tw=(i, 0)) for i in range(1, 41)] + [st(8400, tw=(40, 0))]
        M = {'m': dict(states=states, books={'A': flat(0, 8500), 'B': flat(0, 8500)})}
        old = D.PLANT_AT
        try:
            D.PLANT_AT = 8.0                       # scorer expecting +5 s but plant at +8 s must fail
            pl = D.planted(M['m']['books']['A'], [200.0], at=8.0)
            D.PLANT_AT = old
            self.assertFalse(abs(D.lead(D.Mid(pl), 200.0) - D.PLANT_AT) <= 1.0)
        finally:
            D.PLANT_AT = old

    def test_bar(self):
        pm = {i: ([5.0] * 3, [0.0] * 3) for i in range(12)}
        self.assertTrue(D.bar(pm)['verdict'].startswith('PASS'))
        self.assertEqual(D.bar({0: ([5.0] * 29, [0.0])})['verdict'], 'unknown (n<30)')
        pm2 = {i: ([-5.0] * 3, [0.0] * 3) for i in range(12)}
        self.assertEqual(D.bar(pm2)['verdict'], 'no lead')
        pm3 = {i: ([5.0, 5.0, -1.0] if i % 2 else [-1.0, -1.0, 5.0], [0.0]) for i in range(12)}   # 50% after
        self.assertEqual(D.bar(pm3)['verdict'], 'no lead')

    def test_placebo_event_free(self):
        pt = D.placebo_times([500.0, 1000.0], (0, 2000), k=10)
        self.assertEqual(len(pt), 10)
        self.assertTrue(all(abs(t - e) > D.WIN for t in pt for e in (500.0, 1000.0)))


if __name__ == '__main__':
    unittest.main()
