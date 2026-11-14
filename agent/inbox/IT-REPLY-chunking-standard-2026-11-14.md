# Task chunking standard (IT, 14 Nov 2026). Applies to every project from now on.

Why: on 14 Nov the agent made about 3,900 model calls, each re-sending about 96k tokens, and finished almost nothing. Every extra call re-sends the whole session. A task written so that the agent explores, searches and codes costs dozens to hundreds of calls. A task written as one bounded run costs a handful.

## Each task the agent receives must be ONE chunk:
1. **Exact inputs:** file paths, codes, dates, URLs, unit names. No "find", "look around" or "search for".
2. **Exact action:** a command or a script that already exists in your repo. **You write and test the script; the agent only runs it.** No coding by the agent (Nick: it is slow and makes bad mistakes).
3. **Exact output:** file path, columns and format, and the commit message.
4. **Done check:** one line the agent can verify (row count, sha256, `systemctl is-active`, first-row time).
5. **Size:** should take 15 tool calls or fewer. If it needs more, split it into numbered chunks (A, B, C), each its own task, each committed on its own.

## Not acceptable as a task
- Open-ended research or web scans. Give the exact URLs or queries, or keep the research in your own chat.
- "Investigate why X": give the agent the specific read-only commands whose output you need, and do the diagnosis yourself.
- Bundles of several unrelated asks in one task.

## The agent's side
If a task does not meet this standard, the agent runs the first well-defined step only, commits it, and writes one line "NEEDS CHUNKING: <what is missing>" in the project's channel. It does not explore to fill the gap.
