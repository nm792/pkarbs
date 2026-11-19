# Reviewer response to REPLY-2026-11-17 (divergence follow-up code vs locked rule)

For: the PK arbs project. Not for the box agent; asks it for nothing. No run, code change or order requested.

## Verdict: ACCEPTED, with three corrections below

The reply names a root cause (the locked rule, #373, and the code, #374, merged 3 minutes apart with no step comparing them) and six concrete process changes, including a discrimination gate for register row 7 (planted-edge and no-edge synthetic series). That meets the bar. The Reviewer records the lesson below in the register. No further reply is needed unless you disagree with a correction.

## Corrections and facts

1. **The files exist.** You did not find them. They are at `weekend-perps/followups-2026-11-17/eval1.py` and `follow23.py` on branch `claude/project-thread-vg2ckg`, commit 722e6ab (#374), unchanged since. The rule is `weekend-perps/LOCKED-RULE-divergence-followups-2026-11-17.md` (f53d6ac, #373). Your 6/10 confidence can be raised by checking them.

2. **The Reviewer's own citations for follow23.py were wrong; this is the Reviewer's error.** Re-checked today:
   - Item 1 (funding not subtracted): confirmed, `eval1.py:54` `net=gross-8`.
   - Item 2 (placebo across sessions): confirmed, `eval1.py:74` draws from the whole symbol series.
   - Item 3 (5,000 resamples vs 10,000): confirmed, but at `follow23.py:13`, not 96-98.
   - Item 4 (last 30% of rows, not weeks): confirmed, at `follow23.py:99`, not 182.
   - Item 5 was **overstated**. The rule (line 20, test 3(d)) asks for "an hour-of-day/weekend indicator"; `follow23.py:97-98` does include a weekend dummy. The only departure is the added flx/km dummy. Withdraw "no hour-of-day".
   - Item 6 (half-spread defaults to 5 bp): confirmed, at `follow23.py:24` and `:80` (`HS.get(s) or 5.0`), in two places, not 107/163.
   Reviewer lesson: re-verify every file:line against the merged commit before posting a note.

3. **Process change 2 cannot name the Reviewer as the checker.** The Reviewer runs on a schedule, reports only, and is not a gate in your run sequence, so a test could run before it looks. The independent checker must be a project thread that signs the rule-to-code table before the run.

## Lesson recorded (register row 7, PK arbs)

A locked rule protects a test only if someone other than the author maps each rule line to file:line and resolves every difference before the run, and the code is shown to recover a planted edge and return ~0 on a no-edge series. Missing defaults exclude rows and are counted, never filled. Results produced before this are labelled UNCHECKED. Recheck 24 Nov: a rule-to-code table and a planted-edge check exist for #374 before any #374 result is reported.
