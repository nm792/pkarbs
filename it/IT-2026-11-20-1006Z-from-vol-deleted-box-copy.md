# IT 10:06Z 20 Nov: pkarbs/from-vol was deleted from VOL2; box copy has every file

Goal: tell you plainly what happened to your data, and how to get it back if you need it.

Position: at 09:22Z an agent session (MFW dispatch, acting on IT's disk-cleanup row X1) ran rm -rf on /mnt/HC_Volume_107257520/pkarbs/from-vol (dialogue status/X3-from-vol.md, 5253b2a0). It read an early "0 differences" line in the ship log and missed a later failed checksum. That is IT's error: the row's wording allowed it.

The box holds vol2-archive/pkarbs-from-vol-20261119 with all 871,508 files. Its byte total is 4.56 GB against the 6.83 GB IT measured locally. The local figure was disk usage (du -B1, 4 KB blocks), which over 871k small files adds roughly that much, so the content is very likely whole. That is not yet proven file by file.

The one item: do you need from-vol back on local disk? If yes, reply here and IT copies it back from the box when VOL2 has room. The delete rule is now strict: no local delete without a completed checksum run that exits 0.
