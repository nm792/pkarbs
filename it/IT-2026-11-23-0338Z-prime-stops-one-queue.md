# IT note 03:38Z 23 Nov: Prime process stops go through one queue

Reports say Prime's 4 cores are overloaded and several projects plan to clear duplicate or idle jobs. To avoid two projects stopping (or restarting) the same thing:
1. Every stop or restart on Prime runs as a row in trading-test dialogue/OPEN.md. Ask IT on your reviewer branch (one line: what, why, keep or delete files); IT routes it within 15 minutes.
2. Already queued or done: M51 old Nautilus sandbox (stopped 03:24Z); P106e duplicate NBA recorder (PK fix f5be71e7, tests and pre-flight first); P107 /tmp CS2 probe (Nick approved 00:17Z); T61 T45 recorder (v3, fallback v2).
3. A read-only CPU read (P112: load, top CPU by service) runs in the 03:40Z PK run; results in dialogue/status/CPU-23NOV.md. Use it before asking for more stops.
4. Candidates no project has claimed (service map dialogue/status/SERVICE-MAP-23NOV.md): mm-poly-ws, mm-ff300-books, mm-poly-rest, mm-kalshi, mm-ff300-firstseen, c-tokyo-node, paper-rule-c, aurumer-p-df-sim, depth321, kalshi-us-1m, full-books-morning. If one is yours, say so; unclaimed ones go to Nick as one NEEDS-NICK item.
