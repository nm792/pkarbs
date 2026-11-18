# Reviewer: standing rule for every REPLY (from 17 Nov 2026)

For the project's Claude, not the box agent. Applies to every `REPLY-*.md` answering a Reviewer note, in any branch or folder.

Why: replies so far answer item by item and never say how the project stands against its goal (Nick, 17 Nov 08:44Z). Item fixes that don't move the goal are not progress.

## Every REPLY opens with these three, before any item
1. **Goal**: the project's overall goal, in one sentence.
2. **Where it stands**: the measured position against that goal today, with a cited artifact (file path and commit, or result file). "No measured result yet" is a valid answer if you say what the next measurement is and when it lands.
3. **The one item that matters most**: the single item in the note that matters most for the goal, and why. If none of them matters for the goal, say so.

Item-by-item answers come after that.

## How the Reviewer checks it
A reply without this opening is logged as non-compliant in the register. The second non-compliant reply from the same project is a REPEAT and goes to Nick.
The Reviewer's own notes open the same way: a goal-level assessment before any list.

## STANDING RULE: 15-minute plausibility check on 5-minute markets (Nick, 18 Nov 2026 18:14Z)
Nick: "i already told you I am not waiting hours just to see failed tests over and over when we are working on 5 minute markets with large volumes"
- No run on 5-minute markets waits hours for its first check.
- **Within 15 minutes of start**, check and commit: markets seen per coin (expect every window of every coin in scope: 3 per coin in 15 min), quotes posted per strategy, and fills per strategy against the market's printed volume in the same windows.
- If any figure is implausible (a coin missing, a maker with no quotes on a live book, fills far below what the volume allows), **kill the run, find the cause with file and line, fix and rerun at once** (paper-only, no Nick Go, B7).
- **Never report or relay numbers from a run that has not passed this check.** A report without the committed 15-minute check is INVALID.
- The Reviewer checks this first on every 5-minute run (price-and-plausibility before plumbing).

## STANDING RULE: pre-run gate, no gate no run (Nick, 18 Nov 2026 18:20Z)
Nick: "I told you no more tests that cannot be of any use". Cause: MFW S1-S5 makers could never post (DESIGN.md:31, live_score.py:104-105: bid + 0.01 on a 1-tick book = the ask); the Reviewer never desk-checked it.
- **Before any run**, each rule must be shown on a **recorded live book** (committed snapshot) to: (1) place an order, (2) get a fill from the recorded prints, and (3) be able to fail as well as pass (a planted case where it must not post or must lose).
- The project commits this gate output beside the spec. The **Reviewer desk-checks spec and code against it before clearance**: can every rule post and fill on a real book, and can the test fail?
- **No gate, no run.** A run without a committed, Reviewer-checked gate is INVALID and its numbers are never reported.
- Then the 15-minute plausibility check applies once the run starts.
