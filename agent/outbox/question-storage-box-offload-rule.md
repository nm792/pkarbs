# Question to the PK arbs reviewer: what moves to the 1TB box?

## Ask (one decision)
The sports-MECE shadow data volume `/mnt/HC_Volume_107257520` is **100% full (0 B free)**; the shadow logger still writes only on root-reserved blocks (a timer, not a fix). The 1TB Hetzner storage box (SSH/SFTP, 963 GB free, already used via `n218a_partA.sh`/`n218_box_copy.sh` from the temperature project) is reachable.

Name the exact paths/dirs to offload (not "the shadow data" generally), the retention/delete rule, and the sha-verified flow to use. Candidates here, owned by the shadow-side:
- `/mnt/HC_Volume_107257520/pkarbs/...` (94 GB of the 100 GB — data-v2 spool + raw gz chunks)
- `/root/sports-mece-shadow-per-run.csv` (already redirected to root fs)

The server agent will move nothing until this is ruled, then run the named script + three-way sha verify.

## State
- /dev/sdc: 100% used, 0 avail; logger burning root-reserved blocks. /: 8.8 GB free. /dev/sdb: 4.8 GB free. No local 1TB device (the box is SSH/SFTP).

## Trigger
- Dispatch sweeps keep flagging "disk full" with no offload target; seeking the storage policy from the reviewer rather than guessing.