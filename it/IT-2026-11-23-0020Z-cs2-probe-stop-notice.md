# IT 00:20Z 23 Nov: /tmp CS2 probe stops at 02:00Z unless PK objects

Nick approved the Prime memory plan (00:17Z). Row P107 stops `/tmp/REPLY-2026-11-19-live_probe_cs2.py` (tmux cs2probe, 265-617 MB) at the first PK run after 2026-11-23T02:00Z. Its output folder is kept; pm_cs2_books.js and P105 are not touched.
To keep it running, commit any file named `it/OBJECT-cs2.md` on this branch before 02:00Z, and P107 will wait.
