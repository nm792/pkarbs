# Two additions to the TheSports / disk task (11 November 2026)

From the coordinator, on Nick's behalf. Please do both and report both by 09:45Z on 11 November, in agent/outbox.

1. Stop the shadow logger, which has been running since 3 November. Stop the unit and disable it so it does not restart. Then confirm it is stopped: show the unit state (inactive and disabled), that no process is left, and that its output file has stopped growing over at least two minutes. If stopping it needs a tapped card, raise the card yourself.

2. Hash-check the 85 moved files (37 GB) against their originals. Do NOT compare sizes. Compute a content hash (sha256) of each moved file and of its original, and list any file where the two differ or where an original is missing. Do not delete any original until every hash matches. Report: files checked, files matching, files differing, and the command used.

Still open from the earlier note (thesports-ts-mqtt-gap-2026-11-11): the ts_mqtt and books_mid export for final-topics-32295b-slim has not landed since 00:22Z on 11 November. Please export now and say why it stalled.
