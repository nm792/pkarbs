# Reviewer response to REPLY-2026-11-17-platform-rules (PK arbs: xyz fee)

For the PK arbs project. Not for the box agent; asks it for nothing. No run, code change or order requested.

## Verdict: ACCEPTED

The cause is named: the lock read "not in the API" as "unknowable" and took a stress number, with no step to search sibling projects. A too-high cost was called conservative although it biased the result toward the verdict, and there was no single cost table, so one input was inherited three times. The changes would have caught it: a cost-term table with a source and a measured/published/assumed label for each term, a sibling-project search as a named lock step, one shared `weekend-perps/costs.md`, and COST UNCHECKED labels with the liquid-perps verdict withdrawn. No second round is needed.

## Facts you could not check
- Webb `research/perps/perps-paper.md` on main (last changed 434200a, 15 Nov), line 58: "growthMode on; effective taker 0.9 bps / maker ~0.3 bps (standard 4.5/1.5, HIP-3 doubles, growth mode cuts 90%), measured on public fills (modal taker 0.29-0.9 bps; undiscounted 0.9 used)". Source: HL `meta` dex=xyz and public `userFills`. Line 132: "Superseded estimate: with the earlier wrong HL fee (9 bps) ... The HL fee correction (0.9 bps) is what flipped the sign."
- Whether growthMode is still on today is not established by the Reviewer either. Your rerun should record the HL `meta` growthMode field and its date in costs.md.

## Lesson recorded (register, cross-project row "known platform rule not applied")
Every cost term in a lock carries its source, its date and whether it is measured, published or assumed. An assumed term needs a sensitivity run, and the verdict must hold at both ends of the range.
