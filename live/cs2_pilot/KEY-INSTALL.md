# Installing the Polymarket trading key for the CS2 pilot (Nick only)

The key is never pasted into chat, Git, a PR, a Hermes inbox/outbox file, or a message. Only Nick handles it. Hermes and
the pilot only ever see the file path `/etc/pkarbs/pm-pilot.env`.

## 1. Use a separate Polymarket account just for the pilot (recommended)
Anything running as root on the shared server can read a root-owned file, Hermes included. So the key on the server
should only control the pilot's money.
1. Create a new Polymarket account (a fresh email login) for the pilot.
2. Deposit about **$600** into it: the $500 loss limit plus room for fees/rounding. Do not keep other funds there.
3. In that account, copy the **wallet address** from the profile menu, and export the **private key** from the
   account settings ("Export private key"). Keep both on your own machine only for the next step.

If you would rather use your main account, the steps are the same, but the server then holds a key to all of it.

## 2. Put the key on the server (run these yourself over SSH, as root)
```bash
sudo install -d -m 700 -o root -g root /etc/pkarbs
sudo bash -c 'umask 077
read -r -s -p "Polymarket private key (input hidden): " K; echo
read -r -p "Polymarket wallet address (0x...): " W
printf "POLYMARKET_PRIVATE_KEY=%s\nPOLYMARKET_WALLET_ADDRESS=%s\n" "$K" "$W" > /etc/pkarbs/pm-pilot.env
unset K W'
sudo chmod 600 /etc/pkarbs/pm-pilot.env
sudo ls -l /etc/pkarbs/pm-pilot.env      # should show: -rw------- 1 root root ...
```
- `read -s` hides what you type, and the key never appears on a command line, so it is not saved in shell history.
- The pilot refuses to start in live mode if the file is readable by anyone other than its owner.
- Do not `cat` the file or copy it anywhere else.

## 3. Go live (only after the dry-run report)
Live trading needs all of these; the pilot checks each one at start and stays in dry mode otherwise:
1. The dry-run gates in `agent/tasks/cs2-pilot.md` pass.
2. The server passes Polymarket's region check (`https://polymarket.com/api/geoblock` returns `"blocked": false`).
   If it does not, orders from the server are rejected and the pilot cannot run there.
3. You write the approval file yourself: `sudo touch /root/cs2pilot/out/LIVE_OK`.

## Stopping and revoking
- Stop now (cancels every open order, exits): `sudo touch /root/cs2pilot/out/STOP`.
- If the process dies, Polymarket cancels its open orders by itself within about 10-15 s (order heartbeat).
- To revoke the key completely: withdraw the funds from the pilot account in the Polymarket app, then
  `sudo shred -u /etc/pkarbs/pm-pilot.env`.
