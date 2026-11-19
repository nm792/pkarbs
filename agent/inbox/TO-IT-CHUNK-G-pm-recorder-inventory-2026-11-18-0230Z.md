# CHUNK G: read-only inventory of Polymarket recorder dirs by sport. Posted 18 Nov 2026 02:30Z. Independent of P18.

**1. Goal.** Find automated prediction-market edges toward $500/day. Nick wants every other Goalserve-covered sport tested in parallel (tennis, hockey, basketball); I need to know which sports the recorder holds markets and books for, and from when.
**2. Position.** Tested on a fake dir here (prints dir, first/last books time, events per sport). No result yet.
**3. One item.** Run, then post the output verbatim under `## G inventory` in agent/status/goalserve.md:
`cd <repo> && git pull -q && df -h / <data volume> && nice -n 19 timeout 1800 python3 -I feeds/pm_recorder_inventory.py <data volume>`
(the data volume is the capture volume; no data on the root disk; read-only, writes nothing).
**Done check:** exit 0 and one `books` line per dir with markets.jsonl. If a sport name does not appear, the recorder holds none.
