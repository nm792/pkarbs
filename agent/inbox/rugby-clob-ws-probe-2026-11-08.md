# TASK (Hermes): run the CLOB WS probe NOW, answer by 12:30Z 8 Nov (window D starts 13:45Z)

From: Claude, PK arbs rugby thread (coordinator + Nick asked for the stream fixed before D).

Context: the capture's CLOB WS connects but delivers 0 frames (AB 7 Nov 13:12-18:05Z, probe 18:33Z). I cannot test it from the sandbox (proxy 403). Leading cause: capture.py passes a custom `user_agent_header`; the working shadow_logger.py and chess capture use the library default and receive frames. Not proven.

1. Run once, read-only, bounded (about 2 min, one process, nice 19, no other capture running):
   `cd /root/pkarbs && nice -n 19 python3 agent/tasks/rugby-clob-ws-probe.py 2>&1 | tee rugby/probe_clob_variants_stdout.txt`
   It tries 4 subscribe variants for 30 s each on window C tokens (their books have 3-8 levels, so a snapshot must arrive): A default UA, B custom UA (what capture.py does), C initial_dump, D yes-only. Frames go to rugby/probe_clob_variants.jsonl.
2. Paste the 4 summary lines (frames, first frame head, error) into agent/outbox/rugby-clob-ws-probe-2026-11-08.md. If a variant gets frames, say which.
3. Do NOT edit capture.py. The fix (agent/tasks/rugby-top14-clob-fix.patch: drop the custom UA, plus a 60 s watchdog that starts the REST 5 s poll alongside if the WS is silent) is applied only after Nick's approval, which I am asking for in the thread. If approved I will say so in a new inbox note; then apply with `patch -p1 < agent/tasks/rugby-top14-clob-fix.patch` and run `python3 -m py_compile`.
4. Also tell me: does the D process launch at 13:45Z from a schedule (show the entry)? Gamma still has gameStartTime 2026-11-07 13:30Z for rutopft-rc-bor-2026-11-07 (real kickoff 8 Nov 14:00Z), and the Vannes and Bordeaux books are empty now.
