#!/usr/bin/env python3
"""Offline test for bookmaker_dictionary.py: local HTTP server stands in for Goalserve. Prints PASS/FAIL, exit 0 only if all pass."""
import sys, os, gzip, threading, tempfile, http.server, subprocess, re
here = os.path.dirname(os.path.abspath(__file__))
FAKEKEY = "k" * 32
XML = {
 "tennis_10": '<scores sport="soccer"><category><match><odds><type><bookmaker name="bwin" stop="False" ts="1" id="2"/><bookmaker name="Pinnacle" stop="False" ts="1" id="16"/><bookmaker name="bet365" id="105"/></type></odds></match></category></scores>',
 "esports_10": '<scores><bookmaker name="bwin" id="2"/><bookmaker name="bwin" id="2"/></scores>',
 "cricket_10": '<scores></scores>',
}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        assert FAKEKEY in self.path
        if "pregame_bookmakers" in self.path:
            body = b'<bookmakers><bookmaker name="bwin" id="2"/></bookmakers>'
        else:
            m = re.search(r"cat=(\w+)", self.path)
            if m.group(1) == "darts_10":
                self.send_response(500); self.end_headers(); return
            body = XML.get(m.group(1), "<scores><bookmaker name=\"bwin\" id=\"2\"/></scores>").encode()
        body = gzip.compress(body)
        self.send_response(200); self.send_header("Content-Encoding", "gzip"); self.end_headers(); self.wfile.write(body)
srv = http.server.HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
tmp = tempfile.mkdtemp()
env = os.path.join(tmp, "e.env"); open(env, "w").write(f"GOALSERVE_USER=u\nGOALSERVE_KEY={FAKEKEY}\n")
out = os.path.join(tmp, "o.md")
r = subprocess.run([sys.executable, "-I", os.path.join(here, "bookmaker_dictionary.py"), "--out", out, "--env", env,
                    "--base", f"http://127.0.0.1:{srv.server_address[1]}", "--cats", "tennis,esports,cricket,darts"],
                   capture_output=True, text=True)
fails = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: fails.append(n)
check("script exits 0", r.returncode == 0)
t = open(out).read() if os.path.exists(out) else ""
check("tennis: Pinnacle yes (id 16)", "PINNACLE tennis: yes (id 16)" in t)
check("esports: Pinnacle no", "PINNACLE esports: no" in t)
check("cricket: empty feed -> NOT CHECKED, not 'no'", "PINNACLE cricket: NOT CHECKED" in t)
check("darts: HTTP 500 -> NOT CHECKED with reason", "PINNACLE darts: NOT CHECKED" in t)
check("esports duplicate bookmaker counted as 2 rows, 1 distinct", "distinct bookmakers: 1" in t and "bwin (id 2): 2 market rows" in t)
check("key never in output file", FAKEKEY not in t)
check("key never in stdout/stderr", FAKEKEY not in r.stdout and FAKEKEY not in r.stderr)
check("dictionary call recorded", "tennis_scores/pregame_bookmakers" in t and "bytes" in t)
print("ALL PASS" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
