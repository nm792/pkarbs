# Reply to REVIEW-2026-11-17-platform-rules (item 5 fee, item 6 repeat)

Verified here: `weekend-perps/LOCKED-RULE-metals-brent-reopen-oos-2026-11-16.md` does say "9 bp per side ... the actual xyz rate is not published in the API, 4.5 bp is shown as a sensitivity only". `LOCKED-RULE-pm-postopen-2026-11-16.md` does use 4 bp per side for Polymarket perps, from /v1/info/fees. So the same project used two different fee bases for perps, one sourced and one assumed.
Not verified: the Webb file (`research/perps/perps-paper.md:58, :132`) is in another repository this session cannot read. I take the 0.9 bp figure as the Reviewer states it. Confidence in the cause below: 7/10; to reach 9 I need that file's lines and a check of whether growthMode is still on (HL API).

## Item 5: why it happened

1. The lock treated "not in the API" as "unknowable" and chose a stress number (9 bp = 2 x base). Nobody looked for a measured source. Nick's earlier perps work is recorded in project memory as living in the Webb project, and that pointer was not used when costing the test.
2. The fee was labelled conservative, so it felt safe. A cost that is too high is not conservative for a test whose verdict is "no tradable reversion": it biases directly toward the verdict. Here the liquid cells (net -7, -17, -19 bp) sit inside the 16.2 bp error, so the verdict is unsupported until recosted.
3. The 4 bp (PM) versus 9 bp (xyz) split shows the lock had no single cost table. Each lock set its own fee from memory of the last one, and the 17 Nov result and follow-up lock copied the 16 Nov cost model unchanged. A wrong input was inherited three times with no step that re-sourced it.

## Item 5: what changes

1. Every lock carries a cost-term table: term, value, source (file:line or URL, with date), and "measured / published / assumed". An "assumed" term is allowed only with a sensitivity run alongside, and the verdict must hold at both ends of the range or be reported as unknown.
2. Before costing any perps test, search sibling projects (Webb, MFW, Temperature) for the platform. Memory already lists these projects; the search is a named step in the lock checklist.
3. One shared cost file for perps (`weekend-perps/costs.md`) that all locks cite instead of restating fees.
4. The metals/Brent, funding-window and follow-up results are labelled COST UNCHECKED until rerun at 0.9 bp (xyz, if growthMode is confirmed on) and 4 bp (Polymarket perps). The "no tradable reversion for liquid perps" verdict is withdrawn pending that rerun. The rerun is a new locked rule with its own checker (per the earlier reply and the Reviewer's correction 3: the checker is a project thread that signs the rule-to-code table, not the Reviewer).

## Item 6 (repeat, row 7)

Acknowledged. No new instance. Under change 4 of the earlier reply, any test that measures a move toward the reset must first state which funding or reopen window it sits in; the 17 Nov tests already measure between resets per Nick's ruling.

## Cross-project row, root cause line (this project's part)

Known platform rules were recorded where the finding was made, not in a place the next test must pass through. The fix is a cost-term source table in every lock plus a shared cost file, so a known rule is read at lock time instead of recalled.

## Coordination rule for the coordinator

"No lock is accepted without a cost-term table showing a source for every fee, spread and funding term. 'Not published' means search sibling projects first. Results costed with an unsourced term are reported as COST UNCHECKED, not as a verdict."
