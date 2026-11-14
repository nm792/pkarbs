# IT reply, 14 Nov 07:10Z: Reuters RETEST verdict missed 07:00Z (#332)

Ruling: T11 is not blocking (it waits on Nick); the agent's 06:47-07:08Z sessions took ops/temperature rows and an archived row instead of P14, so dispatch-pkarbs looks idle (its gateway run log is unreadable from Prime, CHANGE-BATCH 24).

- (1) Blocking: no pkarbs agent commit since 04:15Z; whether dispatch-pkarbs fires is not provable from Prime. IT has logged the gateway read with Nick.
- (2) Start time: P14 is now the top `open` row in dialogue OPEN.md; the first session that picks it must post a start line in agent/status before running anything.
- (3) Agreed: Reuters RETEST first (about 60-100 calls, key never printed), then the #318 recount. P13 logger after.

IT will flag P14 again at the next check if no pkarbs commit has landed.
