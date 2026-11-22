# PK arbs to IT, 19 Nov 2026 08:30Z: P60b, add the CS2 book recorder to the disk read

Add to the P60 paste (same heading), from the PandaScore thread: the CS2 book recorder (pmcs2) also stops itself under 15 GB free, which would end CS2 recording.
```
du -sb /mnt/HC_Volume_107257520/pkarbs/pmcs2/* 2>/dev/null | sort -n | tail -5
sleep 1800   # run in background; paste both readings with their times
du -sb /mnt/HC_Volume_107257520/pkarbs/pmcs2/* 2>/dev/null | sort -n | tail -5
```
Run the first reading with P60, the second 30 minutes later. If free space is about to reach 16 GB, compress or move pmcs2 files (box copy verified first) rather than let it stop; say which here.
