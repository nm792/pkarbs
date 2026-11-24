#!/usr/bin/env python3
"""Tests for it/ll_capture_wd.py watchdog (R-094). The module needs the PandaScore token and websockets at import,
so the pure watchdog pieces are extracted by AST and exec'd. Run: python3 it/test_ll_capture_wd.py"""
import ast, sys, os, json, time, difflib, io, contextlib, threading
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "ll_capture_wd.py")).read()

def load(src):
    tree = ast.parse(src); keep = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in ("wd_decide", "wd_thread"): keep.append(n)
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("WD_LOOP_S", "WD_DATA_S", "WD_DISC_FAILS") for t in n.targets): keep.append(n)
    ns = {"time": time, "os": os, "json": json}
    exec(compile(ast.Module(keep, []), "wd", "exec"), ns); return ns

def mk(now, beat=0, fail=0, live=(), last=None):
    return {"beat_ns": now - int(beat * 1e9), "disc_fail": fail, "live": set(live),
            "last_msg_ns": {m: now - int(a * 1e9) for m, a in (last or {}).items()}}

def run_tests(src=SRC):
    ns = load(src); d = ns["wd_decide"]; now = time.time_ns(); bad = []
    def chk(name, got, want):
        if (got[0] if got else None) != want: bad.append((name, got, want))
    chk("healthy idle night (no match)", d(now, mk(now, beat=5)), None)
    chk("frozen loop -> 5", d(now, mk(now, beat=ns["WD_LOOP_S"] + 5)), 5)
    chk("14 discovery fails ok", d(now, mk(now, fail=ns["WD_DISC_FAILS"] - 1)), None)
    chk("15 discovery fails -> 4", d(now, mk(now, fail=ns["WD_DISC_FAILS"])), 4)
    chk("live match, data 10 min ago ok", d(now, mk(now, live=["a"], last={"a": 600})), None)
    chk("live match, silent 16 min -> 6", d(now, mk(now, live=["a"], last={"a": ns["WD_DATA_S"] + 60})), 6)
    chk("one of two live sockets recent -> ok", d(now, mk(now, live=["a", "b"], last={"a": 2000, "b": 30})), None)
    chk("silent old match NOT live -> ok (no subscription)", d(now, mk(now, live=[], last={"a": 5000})), None)
    chk("subscribed but never any message -> ok (not yet judged)", d(now, mk(now, live=["a"], last={})), None)
    # wd_thread: stale beat must call exit_fn(5) and print a watchdog_exit line
    st = mk(time.time_ns(), beat=1000); got = []; ev = threading.Event()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        t = ns["wd_thread"](st, interval=0.05, exit_fn=lambda c: (got.append(c), ev.set(), sys.exit()) )
        ev.wait(3)
    if got != [5]: bad.append(("wd_thread exit code", got, [5]))
    if '"watchdog_exit"' not in buf.getvalue(): bad.append(("wd_thread log", buf.getvalue(), "watchdog_exit line"))
    # wd_thread must NOT exit on a healthy state
    st = {"beat_ns": 0, "disc_fail": 0, "live": set(), "last_msg_ns": {}}; got2 = []
    st["beat_ns"] = time.time_ns() + 10**13
    ns["wd_thread"](st, interval=0.05, exit_fn=lambda c: got2.append(c)); time.sleep(0.3)
    if got2: bad.append(("wd_thread false exit", got2, []))
    return bad

def main():
    bad = run_tests(); print("real:", "PASS" if not bad else bad)
    ok = not bad
    # structural: the live file still has the capture it replaced (diff vs floor_env is additive: no removed capture lines of substance)
    base = open(os.path.join(HERE, "ll_capture_floor_env.py")).read().splitlines()
    new = SRC.splitlines(); ast.parse(SRC)
    removed = [l for l in difflib.unified_diff(base, new, lineterm="", n=0) if l.startswith("-") and not l.startswith("---")]
    print("lines removed vs floor_env:", len(removed)); [print("  ", r) for r in removed[:12]]
    if len(removed) > 12: print("  too many removals"); ok = False
    for needle in ("await discovery_nb()", "wd_thread(state)", "asyncio.create_task(heartbeat())", 'state["live"].add', 'state["live"].discard', 'version="v4-watchdog"'):
        if needle not in SRC: print("MISSING", needle); ok = False
    # mutants must fail
    muts = {"threshold ignored": SRC.replace("> wd_loop_s", "> wd_loop_s * 1e9"),
            "live never checked": SRC.replace("if live and (now_ns", "if False and (now_ns"),
            "disc never counted": SRC.replace('st_["disc_fail"] >= wd_disc', 'st_["disc_fail"] > 10**9'),
            "wrong exit zero": SRC.replace("(exit_fn or os._exit)(d[0])", "(exit_fn or os._exit)(0)")}
    for name, m in muts.items():
        if m == SRC: print("MUTANT NOT APPLIED", name); ok = False; continue
        r = run_tests(m); print("mutant %-20s %s" % (name, "caught" if r else "SURVIVED")); ok &= bool(r)
    print("ALL OK" if ok else "FAIL"); sys.exit(0 if ok else 1)
main()
