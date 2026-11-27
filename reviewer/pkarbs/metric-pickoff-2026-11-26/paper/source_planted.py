"""Pre-flight only: releases a planted winner for ONE event after DELAY_S seconds, to prove the live wiring (source thread -> strategy on the loop
-> decisions row -> sandbox). Env PLANT_SLUG, PLANT_NAME, PLANT_DELAY_S (default 30). Use in a scratch logdir only; its fills are test fills."""
import os, time
class Source:
    POLL_S = 1.0   # HTTP source: one request per event per second (rate limits); the publisher's own update cadence is the real floor
    def __init__(self, evs, logdir):
        self.t0 = time.time(); self.slug = os.environ['PLANT_SLUG']; self.name = os.environ['PLANT_NAME']; self.d = float(os.environ.get('PLANT_DELAY_S', 30))
    def poll(self):
        return [(self.slug, self.name, None, dict(planted=True))] if time.time() - self.t0 > self.d else []
