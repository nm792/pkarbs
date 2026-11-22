# IT 03:16Z 20 Nov: URGENT, is export_slim_32295_plumb.py TheSports? Reply in one line

Goal: keep your protected recorders running while VOL2 stops filling.

Position: VOL2 free fell from 19.4 GB (02:30Z) to 11.3 GB (03:05Z), about 7 GB/h (data branch status/DISK.tsv); it fills completely around 04:45Z. Prime has 1 GB of RAM available and swap is full (T0h, dialogue c5454da8). The largest process is /root/pkarbs/live/thesports/export_slim_32295_plumb.py at 1.2 GB RSS, writing under pkarbs/thesports/final-topics-32295b.

The one item: Nick, 03:16Z: "I think TheSports data is of no use whatsoever." Your P72 said the same. The temperature job's next session (T0k, first row) will:
- stop thesports-capture-b.service;
- kill export_slim_32295_plumb.py if it involves TheSports or ts_mqtt and does not hold books, markets or trades open for writing;
- if VOL2 is still under 12 GB, ship non-book files in final-topics-32295b older than 2 hours to the box, verify the checksums, and delete only the verified local copies.
The book recorder (books, markets, trades, pmws), CS2 probe, CS2 and Dota books, PandaScore and Goalserve are untouched.

Reply here in one line, as soon as you can:
- (a) export_slim_32295_plumb.py is TheSports and not needed: confirm.
- (b) It feeds the book recorder or a look you use: say which file, and IT pulls the kill.
