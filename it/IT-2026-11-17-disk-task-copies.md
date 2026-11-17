# IT to PK arbs, 17 Nov 2026 15:15Z: task copies of the repo filled /vol

1. **Goal:** find and test the PK arbs edges without starving the shared server.
2. **Where it stands:** two of your task runs created full copies of the pkarbs repo on /vol: pkarbs-p15a-20261117 and p15d1-wt, 435k files and 3.4 GB each. They dropped /vol from 7.5 GB to 3.9 GB free (DISK.tsv 12:30Z and 13:30Z rows). The agent moved both to /vol2 at 14:09Z (A47, from_agent/A47-vol-move-2026-11-17.md, da9e7033); /vol2 fell by about 6.8 GB.
3. **The one item that matters most:** no more per-task clones or worktrees. Tasks must use the one existing checkout and write to their own output folder. This is now a standing rule in the agent's queue.

Next: IT is checking whether the two copies are clean and fully pushed (A48). If they are, IT will ask Nick to approve deleting them, which frees about 6.8 GB on /vol2. If your scripts create a worktree, change them to write output only.
