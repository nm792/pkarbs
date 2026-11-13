# Installing the Cito API key on the server (Hermes does it; Nick never runs commands)

Standing rule (Nick 4 Nov): Nick never SSHes into the server. Hermes operates it.

1. Nick sends the Cito key to Hermes in his own direct chat with Hermes. It is never sent in a Claude thread, Git, a PR, or a
   Hermes inbox/outbox/status file.
2. Hermes writes it to `/etc/pkarbs/cito.env` as the single line `CITO_API_KEY=<key>`, without echoing it to logs or
   shell history (e.g. write from its own process, not a command line), then sets `chmod 600`, owner root, with the
   directory `/etc/pkarbs` at mode 700.
3. Hermes never prints, copies, commits or messages the key. Status files say only "key installed: yes/no".
4. To revoke: Nick rotates the key in the Cito dashboard; Hermes deletes `/etc/pkarbs/cito.env`.
