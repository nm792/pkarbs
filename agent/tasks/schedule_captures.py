#!/usr/bin/env python3
"""Install one systemd timer per scheduled capture, firing at kickoff minus lead (default 15 min). Stdlib only.
  python3 schedule_captures.py                    # DRY RUN: print the systemd-run commands for future entries
  python3 schedule_captures.py --install          # run them (needs Nick's approval: it changes the server)
  python3 schedule_captures.py --list             # show pkarbs-cap-* timers
  python3 schedule_captures.py --run-due          # NO systemd needed: call this from any recurring round (Hermes' ~15 min loop);
                                                  # it launches every entry whose fire time has passed (and kickoff+30 min has not), once.
Schedule file: agent/tasks/captures-schedule.json  {"entries": [{"name","kind":"rugby"|"chess","window","kickoff_utc","lead_min","hours"}]}
Rugby entries can omit kickoff_utc: it is the earliest kickoffUTC of that window in the rugby config.
Re-running is safe: an existing unit with the same name is skipped. Entries in the past are skipped."""
import argparse, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.environ.get("PKARBS_ROOT", "/root/pkarbs")
def parse(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true"); ap.add_argument("--list", action="store_true"); ap.add_argument("--run-due", action="store_true")
    ap.add_argument("--schedule", default=f"{HERE}/captures-schedule.json")
    ap.add_argument("--config", default=f"{HERE}/rugby-top14-config-2026-11-07.json")
    ap.add_argument("--now", default=None, help="test only: pretend now is this ISO time")
    a = ap.parse_args()
    if a.list:
        os.system("systemctl list-timers 'pkarbs-cap-*' --all --no-pager"); return
    now = parse(a.now) if a.now else datetime.now(timezone.utc)
    cfg = json.load(open(a.config)) if os.path.exists(a.config) else {}
    for e in json.load(open(a.schedule)).get("entries", []):
        ko = e.get("kickoff_utc")
        if not ko and e["kind"] == "rugby":
            ko = min(ev["kickoffUTC"] for ev in cfg[e["window"]])
        if not ko: print("SKIP (no kickoff)", e["name"]); continue
        fire = parse(ko) - timedelta(minutes=int(e.get("lead_min", 15)))
        if a.run_due:
            marker = f"{ROOT}/schedule/launched-{e['name']}"
            if fire <= now < parse(ko) + timedelta(minutes=30) and not os.path.exists(marker):
                os.makedirs(f"{ROOT}/schedule", exist_ok=True)
                largs = ["rugby", "--window", e["window"]] if e["kind"] == "rugby" else ["chess", "--hours", str(e.get("hours", 6))]
                print("LAUNCH", e["name"], flush=True)
                rc = subprocess.run([sys.executable, f"{HERE}/capture_launcher.py", *largs], check=False).returncode
                if rc == 0: open(marker, "w").write(now.isoformat() + "\n")   # on FAIL the next round retries (until kickoff+30 min); the capture flock stops a double start
                else: print("launcher rc", rc, "- will retry next round", e["name"])
            else:
                print("not due / already launched", e["name"])
            continue
        if fire <= now: print("SKIP (past)", e["name"], fire.isoformat()); continue
        args = ["rugby", "--window", e["window"]] if e["kind"] == "rugby" else ["chess", "--hours", str(e.get("hours", 6))]
        cmd = ["systemd-run", f"--unit=pkarbs-cap-{e['name']}", f"--on-calendar={fire.strftime('%Y-%m-%d %H:%M:%S')} UTC",
               "--timer-property=AccuracySec=1s", sys.executable, f"{HERE}/capture_launcher.py", *args]
        print(("RUN " if a.install else "DRY ") + " ".join(cmd))
        if a.install:
            if subprocess.run(["systemctl", "is-active", "--quiet", f"pkarbs-cap-{e['name']}.timer"]).returncode == 0:
                print("  exists, skipped"); continue
            subprocess.run(cmd, check=False)
main()
