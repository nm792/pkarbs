# Installing the Cito API key on the server (Nick only)

The Cito key is never pasted into chat, Git, a PR, a Hermes inbox/outbox file, or a message. Only Nick handles it.
Hermes and the logger only ever see the file path `/etc/pkarbs/cito.env`. The key is a data key (no money behind it),
but it is the paid Scale plan, so keep it private.

1. Copy your key from the Cito dashboard (citoapi.com/dashboard, API keys).
2. On the server, over SSH, as root:
```bash
sudo install -d -m 700 -o root -g root /etc/pkarbs
sudo bash -c 'umask 077
read -r -s -p "Cito API key (input hidden): " K; echo
printf "CITO_API_KEY=%s\n" "$K" > /etc/pkarbs/cito.env
unset K'
sudo chmod 600 /etc/pkarbs/cito.env
sudo ls -l /etc/pkarbs/cito.env      # should show: -rw------- 1 root root ...
```
- `read -s` hides the key and keeps it out of shell history. Do not `cat` the file or copy it anywhere else.
- To revoke: rotate the key in the Cito dashboard, then `sudo rm /etc/pkarbs/cito.env`.
