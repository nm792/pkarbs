# from_agent — tennis-queue-sim-oom-answer2 (13/tennis-queue-sim)

RESULT
- Re-ran step 3 unchanged with the float64-snapshot fix (queue_sim.py @ NL=12, flat float64 arrays) on the default branch, same 1.5 GB cap (MemoryMax=1600M, swap 0), same inputs (all runs, 1,705,382 book rows / 12,871 market rows).
- **NO OOM this run.** Completed 02:18Z, exit 0.
- Matches paired: Pinnacle 53, bet365 54 (prior run: 7). PASS reached (>=20 Pinnacle).
- Printed lines: pinnacle ack0.2 per_match −0.15 (ci90 [−0.25,0.5]); ack1.3 0.0; drawn no-guard −0.12; drawn 0.3s-guard +0.06. bet365 ack0.2 per_match 6.65 (ci90 [−12.89,28.48]); ack1.3 1.28; drawn no-guard 7.72; drawn 0.3s-guard 4.89. ex_top5 per_match bet365 ack0.2 = −9.2.
DATA
- out_queue_sim.json (1,763 B) committed to winmodels/tennis/hist/out_queue_sim_nov5_full.json; manifest line: 3 book runs + oddspapi/hist, 02:18Z, gate GO.
OPEN / NOT VERIFIED: interpretation of the bet365 positive per_match with a ci90 crossing zero is the reviewer's call; numbers are as printed.
Count: notes run 1, outstanding 0.
