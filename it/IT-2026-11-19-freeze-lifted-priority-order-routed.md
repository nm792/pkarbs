# IT to PK arbs, 19 Nov 2026 03:15Z: freeze lifted; PRIORITY ORDER routed as P44-P48

1. **Goal.** Find a tradeable PK arbs edge on paper (Goalserve/PandaScore leads, CS2/Dota books, perp vs Polymarket open contracts).
2. **Where it stands.** Deleted files restored (#438 6c9fc055, #439 44254baf); the deletion guard is in the /root/pkarbs common git dir at the required SHA-256 (P43, dialogue 2fb6c0bb). The freeze is lifted (dialogue 8a183be2). None of your five jobs has run yet.
3. **Most important item.** Your 03:15Z PRIORITY ORDER (03ad7047) is routed in its order: P44 Goalserve live probe (open), P45 CS2 book recorder, P46 CS2 probe launch (sleeps to 08:50Z), P47 esports look 1 rerun, P48 open-contract recorder (before 06:00Z). P44-P46 are chained in one session; P47-P48 follow in the next.

Items:
1. Routed close-outs: P44b (FINAL at launch +95 min) and P46b (08:52Z lines). The 30-minute interim pastes for job 1 and the 30-minute size appends for job 2 are NOT routed: each would wake the paid agent (cost rule). If you need sizes, ask for one timed check row with a time.
2. P41 (#422 rerun) is closed as dropped per your 0250Z note. The checker's 0245Z "rerun P21b" note is covered by P47 (job 4). P21b daily looks resume 20 Nov after 00:30Z.
3. P37, P31, P32, P36 now wait after P48.
4. **/root/pkarbs is damaged:** P43's `git status` printed `fatal: unable to read 9726e3941a97de7134396adb506ac4d0d2f8e391` (dialogue/status/T0d-hooks.md, 2fb6c0bb). Until that is fixed, any status commit there that hits this error goes to dialogue/from_agent/pkarbs/<same file name> instead. NEEDS CHUNKING: if you want the checkout repaired, send exact commands (no deletion of untracked data; the 1.98 GB untracked from P16s is still unruled) with a one-line done check.
5. Your 0230Z rule (never commit from /root/pkarbs with -A; named files only, `git diff --cached --stat` check) is in the queue header.
