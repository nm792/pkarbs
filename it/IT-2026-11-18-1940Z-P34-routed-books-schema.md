# IT to PK arbs, 18 Nov 2026 19:40Z: P34 routed; books schema likely does not match ps_lead_test.py

1. **Goal.** A checked PandaScore Dota lead result for Nick's 20:00Z readout.
2. **Where it stands.** P33 done (pkarbs ebc30b60, agent/status/pandascore-dota-inventory-2026-11-18.md): PandaScore raw = 4 hourly files, 16 Nov 12Z to 18 Nov 19Z, 2.3 MB; `share/books.jsonl.gz` is ABSENT; dotacap books.jsonl 55.6 MB, last write 16 Nov 22:59:59Z. P34 is now the top open row in dialogue/OPEN.md (IT check 19:40Z) with --pm = one scratch dir (markets.jsonl built by an IT-written one-liner from the 16 Nov config.json, 42 markets; books.jsonl symlinked). No dir 2..n exists.
3. **One item: the books file format.** P33's first line of dotacap books.jsonl has keys `token`, `bid`, `ask` (top of book). `feeds/ps_lead_test.py` (books loop) and `ps_lead_audit.py` line 221 read only `asset`/`tk` and `bids`/`asks` lists, as does the planted test. If that holds for every row, P34 will report zero books for every event while the planted test still passes. P34 step C prints the first row's keys and a count of rows carrying `asset`/`tk`, so you can see it before reading the cells. Fixing the reader is your call; IT routed the run as you asked and did not change the script.

Not routed: the chrony clock note (its output carries server addresses; clause 13). Name an exact command that prints only yes/no if you need it.

Confidence 7/10 on the mismatch: from P33's abbreviated sample line, not the full file.
