# CHUNK G2: Polymarket recorder inventory WITHOUT a pull (replaces the run command of chunk G). Posted 18 Nov 2026 05:30Z.

**1. Goal.** Find automated prediction-market edges toward $500/day; to test tennis, hockey and basketball in parallel I need to know which sports the Polymarket recorder holds markets and books for, and from when.
**2. Position.** Chunk G stopped because `git pull` failed on the dirty checkout (P16s stash is IT's; do not stash). The script is read-only and standalone, so it needs no pull. Tested here on a fake directory.
**3. One item.** Run exactly this, then paste the full output under `## G inventory (18 Nov)` in agent/status/goalserve.md:
```
V=/mnt/HC_Volume_107257520; D=$V/pkarbs/scratch/g2-inventory; mkdir -p $D
git -C <repo> fetch -q origin claude/project-thread-vg2ckg && git -C <repo> show origin/claude/project-thread-vg2ckg:feeds/pm_recorder_inventory.py > $D/pm_recorder_inventory.py
df -B1 --output=avail $V | tail -1
nice -n 19 timeout 1800 python3 -I $D/pm_recorder_inventory.py $V; echo exit=$?
```
`<repo>` is the checkout you already use. `fetch` and `show` do not touch the working tree, so the dirty checkout does not matter. The script writes nothing except the one copied file above (about 2 KB).
**Done check:** `exit=0` and one `books` line per directory that holds markets.jsonl. A sport that does not appear is not recorded.
