# IT to PK arbs, 19 Nov 2026 05:15Z: server changes today, and what they mean for you

1. **Goal:** the shared agent and server do your work quickly and cheaply, and never damage your repo.
2. **Where it stands:** agent spend was $7.47 on 17 Nov and is running at about $3-4 a day today (usage CSVs). Sessions now average about 43 model requests, down from about 90.
3. **The one item that matters most:** anything that runs more than once must be a script that you write and test. The agent installs it once in the Prime crontab and is never woken to repeat it.

Standing changes (all in the agent's queue header, dialogue OPEN.md):
- **Routine = script:** as above. Send the script with exact inputs, output and a done check (dialogue status/CHUNKING.md).
- **Disk policy:** root holds the OS and code only, and data, venvs and caches go to VOL2 or the storage box. The floors are root 5 GB, /vol 3 GB and VOL2 10 GB, and nothing above them is frozen. Raw data older than 7 days ships to the box.
- **No per-task repo copies:** tasks use the one existing checkout and write to their own output folder.
- **Push guard:** a git hook on Prime refuses any push that deletes files or a branch (dialogue status/hooks/pre-push).
- **Data branch:** temperature's script data is moving from dialogue to a `data` branch. Your data stays in your own repo, so nothing changes for you.
