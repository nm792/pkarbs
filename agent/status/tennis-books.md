# status: tennis-books (restarted on /vol2 per pause-lift priority #3)

state: RUNNING (tennis-books-v2, since 15:10:36Z, timeout 22800s ~21:30Z stop)
- Restarted on /vol2: /mnt/HC_Volume_107257520/pkarbs/tennis/2026-11-05 (off root/HC, per reviewer priority list). disk_gate GO.
- unit tennis-books-v2, MemoryMax 500M, MemorySwapMax 0. data books/markets/probe/log + share/.
- Prior HC run (tennis-books-hc) stopped 13:14Z; its 236M stays on HC (kept, not deleted). Earlier root run data kept.
- stop by 21:30Z so 22:00Z LoL capture starts clean. size guards: kill+keep committed if dir >2 GB OR /vol2 free <10 GB OR / free <6 GB.
- Raw ships to box hourly; git manifest only (charter 383). Never commit raw books.
Last heartbeat: 2026-11-05T15:10Z UTC
