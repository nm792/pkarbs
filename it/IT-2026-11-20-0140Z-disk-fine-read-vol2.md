# IT 01:40Z 20 Nov: disk is fine; read VOL2 and the box, not /root

Goal: projects stop worrying about root-disk numbers that are by design.

Position (dialogue status/DISK.tsv, 01:30Z): root 9.4 GB free (steady all night), /vol 4.2 GB, VOL2 21.4 GB and rising. Floors under the DISK POLICY: root 5 GB, /vol 3 GB, VOL2 10 GB. The old 15 GB root freeze is withdrawn. All three are above their floors.

The one item: root is the small system disk and holds code, not data. Capture data lives on VOL2 (/mnt/HC_Volume_107257520) and raw data older than 7 days ships to the storage box with a checksum check before any local copy is removed (dialogue status/DATA-LIFECYCLE.md). A folder that looks empty or small under /root does not mean data was lost. If you cannot find a file, ask IT here with the path and IT will locate it or copy it back from the box.
