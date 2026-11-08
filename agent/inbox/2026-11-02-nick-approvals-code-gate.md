# Inbox: Nick's approvals for the Rugbyrama poll code change and the AB window (2 Nov 2026)

Quoted from project chat, so the code-change gate can clear without a direct message from Nick.

1. Rugbyrama 15 s poll, added as a fourth async task in capture.py (code change), approved 15:44:04Z. Nick's reply to the question "should we add the Rugbyrama 15-second poll to the server's 7-8 Nov Top 14 capture now, before we've confirmed it updates live?" was: "yes".

2. Window AB as one 5 h process, approved 15:50:19Z. Nick's reply to the question "Can this one run longer, with the same memory cap?" was: "yes, so long as we are not putting intense loads on the compute capacity".
   - Run it at low CPU priority (nice -n 19). Keep the 600M memory cap.
   - Keep the poll intervals as written in the task.

Fixture conflict: settled by the coordinator (2 Nov 15:47Z). Window A now covers Toulouse v Clermont at 13:30 UTC, and window D covers Vannes v Bordeaux at 14:00 UTC on 8 Nov.

Windows now: AB (7 Nov 13:15-18:05 UTC), D (8 Nov 13:45-16:30 UTC), C (8 Nov 19:50-22:35 UTC). Run them in that order, one at a time.

Reply in agent/outbox/ once you've read this.
