import gzip, json, os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); F = []
def chk(n, c): print(("PASS " if c else "FAIL ") + n); (F.append(n) if not c else None)
def ev(h, a, v, lg, extra=None):
    e = {"info": {"league": lg}, "team_info": {"home": {"name": h}, "away": {"name": a}}, "odds": {"9": {"name": "Home/Away", "participants": {"0": {"name": h, "value_eu": v}, "1": {"name": a, "value_eu": 2}}}, "8": {"name": "Total", "x": 1}}}
    return e
with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, "esports_2026112000.jsonl.gz")
    with gzip.open(p, "wt") as f:
        n = 0
        for v in (1.5, 1.5, 1.6, 1.7, 1.8):      # A-B: 4 distinct changes (the repeat is dropped)
            f.write(json.dumps({"recv_ns": n, "body": json.dumps({"events": {"1": ev("a", "b", v, "Counter-Strike - X"), "2": ev("c", "d", 2.0, "Dota 2 - Y")}})}) + "\n"); n += 1
    out = os.path.join(t, "o")
    r = subprocess.run([sys.executable, "-I", os.path.join(H, "export_goalserve_sample.py"), "--out", out, "--files", p, "--sport", "esports", "--game", "cs2", "--n", "3"], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-800:])
    rows = [json.loads(l) for l in gzip.open(os.path.join(out, "sample-esports-cs2.jsonl.gz"), "rt")]
    chk("cs2 only, 4 distinct changes (repeat dropped, Dota excluded)", len(rows) == 4 and {x["eid"] for x in rows} == {"1"})
    chk("only the winner market kept (Total dropped)", all(list(x["event"]["odds"].keys()) == ["9"] for x in rows))
    chk("odds values and times preserved in order", [x["event"]["odds"]["9"]["participants"]["0"]["value_eu"] for x in rows] == [1.5, 1.6, 1.7, 1.8] and [x["recv_ns"] for x in rows] == [0, 2, 3, 4])
    idx = json.load(open(os.path.join(out, "index-esports-cs2.json")))
    chk("index lists the match", idx["matches"][0]["home"] == "a" and idx["matches"][0]["n_changes"] == 4)
print("ALL PASS" if not F else "FAILED: " + ", ".join(F)); sys.exit(1 if F else 0)
