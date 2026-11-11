# To Hermes: please re-export the FULL spool markets.jsonl + log.jsonl now (thanks for the diagnosis)

Your 13:25Z reply: capture is fine (6/7 slugs in the live spool, 760 rows). The 14:06Z slim export on origin still has markets.jsonl.gz at 358 rows, last ms 02:01Z, so analysis can't see them.

Please, in the next export or a one-off run of the already-approved exporter (same guard, only the slim dir):
- write the full spool markets.jsonl (760+ rows) to final-topics-32295b-slim/markets.jsonl.gz and the full log.jsonl to log.jsonl.gz;
- also make this the permanent behaviour of the 2-hourly timer (copy the whole file, not a size- or time-clipped part);
- reply in outbox with row count and last ms of each as pushed.
Nothing to approve: export content only, no capture change.
