"""Alert state machine and log. An alert opens only after the structure has met the threshold on
`polls` consecutive clean polls spanning at least `min_secs`; it closes on the first poll that
fails. Every open/close is appended to a JSONL log with duration and what it would have paid."""
import json

class Tracker:
    def __init__(self, log_path, polls=3, min_secs=120.0):
        self.log_path = log_path; self.polls = polls; self.min_secs = min_secs
        self.streak = {}   # sid -> [first_ts, count, peak]
        self.open = {}     # sid -> record

    def _log(self, rec):
        with open(self.log_path, 'a') as f: f.write(json.dumps(rec) + '\n')

    def update(self, sid, ts, qualifies, snap=None):
        """snap = dict(edge, profit, sets, cost, ret, tradeable). Returns 'open', 'close' or None."""
        if qualifies:
            s = self.streak.setdefault(sid, [ts, 0, None])
            s[1] += 1
            if s[2] is None or snap['profit'] > s[2]['profit']: s[2] = dict(snap, ts=ts)
            if sid in self.open:
                o = self.open[sid]
                if snap['profit'] > o['peak']['profit']: o['peak'] = dict(snap, ts=ts)
                o['last'] = dict(snap, ts=ts)
                return None
            if s[1] >= self.polls and ts - s[0] >= self.min_secs:
                rec = dict(event='open', sid=sid, ts=ts, first_seen=s[0], polls=s[1],
                           peak=s[2], last=dict(snap, ts=ts))
                self.open[sid] = rec; self._log(rec); return 'open'
            return None
        self.streak.pop(sid, None)
        if sid in self.open:
            o = self.open.pop(sid)
            rec = dict(event='close', sid=sid, ts=ts, opened=o['ts'], first_seen=o['first_seen'],
                       duration_s=ts - o['first_seen'], peak=o['peak'], last=o['last'])
            self._log(rec); return 'close'
        return None
