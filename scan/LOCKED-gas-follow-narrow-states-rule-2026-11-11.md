# LOCKED RULE: follow AAA's last move, narrow-spread states only, on a third untouched window (written 11 Nov 11:45Z before running)
States (fixed from the earlier windows A+B, 14Z hold gap > 0): LA NE AL RI ND NM OK MS. (post-hoc selection; this test is the check.)
Window C = the 30 events before window B (events 61-90 back) per state. Entry candle index 1 (~14Z), HOLD to settlement, same filters, fee and size as the follow rule (strike within 3c of prior-day AAA, mid 25-75c, side = direction of last daily change).
Placebo: random side per event, 2000 draws. Event-clustered 95% CI.
PASS only if gap after fees > 0, CI lower bound > 0, hit > implied, placebo z >= 2.0, >= 100 strikes from >= 40 events. Else UNPROVEN with counts; report $/day at real size.
