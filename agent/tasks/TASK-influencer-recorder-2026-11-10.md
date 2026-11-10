# TASK: influencer view-count recorder (paper test of a momentum model). Pre-authorised routine capture, no orders.

Requested via the project coordinator, 10 Nov 2026 ~03:55Z (Nick: "$10k open counts"). Read-only HTTP GETs, no keys, no wallet.

## Question
For each new MrBeast / MrBeast Gaming upload, how well does views-so-far at hour h predict the 24 h (day 1) and 7 d (week 1) view count, and how late does the Polymarket bracket price learn it? Needs minute-level view counts plus the book, recorded from upload.

## Step 1: probe (2 min, run first)
`python3 agent/tasks/influencer-recorder.py --out /vol2/pkarbs/influencer --probe`
PASS: prints, for both channels, a latest video id, `watch_views` as a number (not None), and open events with a book sample.
If `watch_views` is None or a host is blocked: stop, write the error to `agent/outbox/influencer-probe-2026-11-10.md`, no further steps.

## Step 2: run (only if probe passes)
`systemd-run --scope -p MemoryMax=300M -p MemorySwapMax=0 python3 agent/tasks/influencer-recorder.py --out /vol2/pkarbs/influencer --max-wait-hours 72`
One process, stdlib only, writes small JSONL under /vol2 (no PK arbs data on the root disk, charter 383). Expected output: about 1.5 MB per tracked video per day. It waits for a new upload on either channel (MrBeast Gaming's last upload was 23 Oct; the main channel posts about every Fri/Sat 16:00-18:00Z), then tracks that video for 7 days. Exits by itself 72 h after start if nothing is uploaded.

## Reporting
Each round: `agent/outbox/influencer-recorder-status.md` with `uploads.jsonl` line count, rows per views_* file, last row timestamp, and `ps`/`free -m`. After the day-1 window of the first tracked video, commit the compressed files to `data/influencer/` (or tell the coordinator the /vol2 path).
Label: everything the recorder writes is measured. No P&L is computed on the server.

## Cleanup
On finish or kill: confirm the process is gone (`ps`), delete temp files, say so in the report.
