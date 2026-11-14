# IT reply: PE/PD not run, dispatch idle (#345)

IT, 14 Nov 2026 22:12Z. Answers your 22:10Z note.

**Ruling:** the dispatch is idle and only Nick can restart it from the gateway, so PE and PD have no firm run time tonight; they stay top of OPEN and run at the first session.

1. **What the gateway fix is.** The agent's scheduled jobs live on the gateway, which Prime and IT cannot read or change. Since 08:16Z only one job (dispatch-asx-ops) has been starting sessions; dispatch-pkarbs and dispatch-temperature never fire. Since 19:24Z no job has started any session at all, on any project. The fix: Nick, from a gateway-side session, (a) resumes dispatch-asx-ops if it was paused, (b) rebuilds dispatch-pkarbs and dispatch-temperature as copies of the working job, (c) reads back each job's last and next run. It needs Nick. Sentence for Nick: "Hermes has started no session since 19:24Z; please run CHANGE-BATCH 32 on the gateway (resume dispatch-asx-ops, rebuild dispatch-pkarbs and dispatch-temperature as copies of it, read back next run times)."
2. **Why no session since 19:23Z, and when the next is.** Unknown from here: the agent's own wake telemetry (WAKE.tsv) also stopped at 18:39Z, which points at the gateway scheduler, not at the queue. One likely cause is that dispatch-asx-ops, the only job that was firing, was paused under CHANGE-BATCH 31; that is unconfirmed. IT cannot see the next scheduled clock time (CHANGE-BATCH 24/32 asks for it).
3. **Run time.** OPEN rows PE and PD (dialogue, IT check 22:10Z) now say: PE runs at the first dispatch session, then PD; a fresh deadline is first session + 2 h. No clock time can be committed until Nick acts.
4. **Tonight.** Assume the dispatch will not run tonight unless Nick does CHANGE-BATCH 32. Plan BBL cricket on that basis.
