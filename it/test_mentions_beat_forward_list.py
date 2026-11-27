"""Offline checks. Run: python3 -I test_mentions_beat_forward_list.py <mentions_beat_forward_list.py>"""
import sys, importlib.util
sp = importlib.util.spec_from_file_location('b', sys.argv[1]); B = importlib.util.module_from_spec(sp); sys.modules['b'] = B; sp.loader.exec_module(B)
ok = N = 0
def chk(n, c):
    global ok, N; N += 1; ok += bool(c); print('check', N, 'ok' if c else 'FAIL', n)
c, s = B.depth_under([(.40, 100.), (.49, 1000.), (.55, 500.)], .5, 200.)
chk('depth walks .40 x100 then .49 up to $200 and never touches .55', abs(c - 200) < 1e-9 and abs(s - (100 + 160 / .49)) < 1e-9)
chk('depth is only what exists when thin ($40)', B.depth_under([(.4, 100.), (.6, 100.)], .5, 200.) == (40.0, 100.0))
chk('an ask exactly at the threshold is NOT under it', B.depth_under([(.5, 100.)], .5, 200.) == (0.0, 0.0))
chk('empty book gives zero', B.depth_under([], .5, 200.) == (0.0, 0.0))
print(f'{"PASS" if ok == N else "FAIL"} ({ok} of {N} checks)'); sys.exit(0 if ok == N else 1)
