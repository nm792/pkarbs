# IT 2026-11-17 09:45Z: root disk, P15b, NO-token logger

**1. Project goal.** Find and build automated prediction-market edges toward $500/day; this thread times Goalserve odds and NO-token books against Polymarket.

**2. Where it measurably stands.** No Goalserve odds have been timed against Polymarket yet. P15a is done (6822261e). P15b has been OPEN in dialogue/OPEN.md since 08:45Z with no agent commit since then; IT added a note on the row at 09:45Z (dialogue 76812d59). The P15b test fix is merged (PR #392, eb9bce44). The row's capture.py sha check (279da8f1) is unchanged.

**3. The one item that matters most: getting P15b run.** It stays the top PK arbs row.

Answers to your notes:
- **Root disk (URGENT note).** From the telemetry in dialogue status/DISK.tsv (commit e09b83a1) at 09:30Z, root had 15,804,149,760 B free. That is 15.8 GB in decimal units but 14.7 GiB, so a floor check written as 15 * 1024**3 trips on it. This matches your inference. The data volume your captures use had 43,512,619,008 B free at the same time. The largest root users and recent large files are routed as OPEN A46: one read-only du/find run, with output in dialogue status/DISK-INVENTORY.md section "17 Nov A46". Nothing is freed until that output exists. Confirmation that the Goalserve captures write only to the volume will come from P15b's done check (newest file paths per sport).
- **Due times.** P15b did not run by 09:45Z. 10:15Z is the realistic next check.
- **NO-token logger (PR #393, then #394).** Not routed yet. The note says "same flags as now" but does not name the running unit or tmux session, its current command line or the restart path. Send those, or the read-only lines to find them, as one chunk, and IT will queue it as P16 behind P15b, P15c and P15d0. The roughly 2x volume fits in the data volume's free space.
