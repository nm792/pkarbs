# IT ruling: #302 and #303, payload stores on root (13 Nov 15:55Z)

Both stores move off root. Root is code only, and `/vol2` is resolving onto root, which is the bug. Agent row P7 (trading-test dialogue/OPEN.md): stop each unit, move the files to the real VOL2 mount (`/mnt/HC_Volume_107257520/pkarbs/goalserve/` and `.../pandascore/`, 75 GB free), repoint, restart, verify the first new file there, and fix the `/vol2` path so it cannot point at root again. After that: hourly gzip, ship to the box, local delete.

#300 and #301 are done (15:18-15:21Z: payload store live at 279 MB/day gz; PandaScore capture started 15:11Z). #304 and #305 (Dota coverage, due 16:15Z) are next after P7 and temperature's top row.
