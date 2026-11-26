# IT: run the macro latency table on the 25 Nov PCE capture (coordinator 26 Nov 04:04Z; Nick: why does P&L rise with latency; INSIGHTS I-46 wording). Read only, paper, no orders.
Folder: /mnt/HC_Volume_107257520/pkarbs/pmevent/pce-20261125 (from it/00-URGENT-MACRO-PCE-25NOV-recorder-2026-11-24.md; if P135-macro-pce.md names another folder, use that and say so).
Files (reviewer branch, commit dd7134a6cb plus make_winners.py): it/macro_latency/macro_latency_table.py, macro_pickoff_score.py, test_macro_latency_table.py, test_macro_pickoff_score.py, make_winners.py.
  cd it/macro_latency && python3 -I test_macro_latency_table.py && python3 -I test_macro_pickoff_score.py            # both must print PASS
  D=/mnt/HC_Volume_107257520/pkarbs/pmevent/pce-20261125
  python3 -I make_winners.py $D > winners.json                                   # Gamma outcomePrices; asserts the market ids; unresolved markets omitted
  python3 -I macro_latency_table.py $D 2026-11-25T13:30:00Z winners.json 0.5,2,5 > pce_latency_table.jsonl
Paste pce_latency_table.jsonl (about 42 lines, a few KB) and winners.json in the dialogue reply. Also: (1) paste P158-pce-score.md; (2) say which scorer file and commit produced the P159 numbers (+$29.60 / +$43.12) and the winners file it used; (3) say whether those numbers were `pnl`/`stake` fields of macro_pickoff_score.py (the spec says they are evidence, not results).
Expected write: nothing in the capture folder; winners.json (about 1 KB) and pce_latency_table.jsonl (a few KB) in the working directory. Not a recorder, no start; the two tests are the pre-flight.
Reading rule: a FILLED row at L=5 with available_at_Lmin false = liquidity posted later (the 5 s run bought something a faster bot could not); an AssertionError LOOKAHEAD or row_age_s < 0 = lookahead bug; anything else = other cause, send me the table.
