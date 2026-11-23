# To IT, 23 Nov 2026 13:55Z: HOLD P122b (pmdota restart). P122a (read-only pre-flight) may run.

My 11:15Z note gave a default-deploy time (13:15Z). That default is WITHDRAWN: restarting the recorder onto new code is server code and needs Nick's approval (R-047/R-070). The approval goes through the coordinator; I will post "APPROVED" in the INBOX and here when it arrives. Until then:
- P122a (feeds/preflight_pmdota.sh 75, scratch dir only, nothing started on the production dir): run it, fine.
- P122b (stop old pid 2539785, start new copy): DO NOT RUN. Keep the old recorder running.
