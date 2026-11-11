# LOCKED RULE: follow AAA's last daily change on state gas markets (written 11 Nov 09:10Z before any data for these states was looked at)
Trigger: the reverse test on 8 other states lost 39c/$ (hit 29.5% vs 43.5% implied). That data is NOT used here; this is a fresh-state test of the opposite side, one rule, no variants.
States (fixed, never used in any gas test so far): AK AL AR AZ CO CT DE HI IA ID KS KY LA MA MD ME MN MO MS MT ND NE NH NM NV OK OR RI SC SD TN UT VT WV WY.
For each state daily series KXAAAGASD<ST>, last 30 days of events with a prior-day change: strikes within 3c of prior-day AAA, YES mid between 25c and 75c at hour 1; if AAA's last change was up buy YES at the ask, if down buy NO; skip zero change.
Fee 0.07p(1-p). Size = 10% x 0.5 x $ traded hours 1-2. Pooled over all states. Split by close date: first half train, second half TEST (headline); also report pooled.
Placebo: random side per event, 2000 draws. Event-clustered bootstrap 95% CI.
PASS only if TEST pooled gap > 0 with CI lower bound > 0, hit rate > implied, placebo z >= 2.0, >= 100 TEST strikes from >= 40 events. Report $/day at real size either way.
