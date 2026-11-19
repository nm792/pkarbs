import os, sys, json, gzip, tempfile, calendar, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compact_goalserve_hours as C
ok = 0
def check(c, m):
    global ok
    if not c: print("FAIL:", m); sys.exit(1)
    ok += 1

def part(n, v, sus=0): return {"name": n, "value_eu": str(v), "suspend": sus}
def ev(h, a, marks): return {"team_info": {"home": {"name": h}, "away": {"name": a}}, "info": {"league": "ITF M25"}, "score": "1-0", "odds": marks}
def mk(name, o1, o2): return {"name": name, "suspend": 0, "participants": {"1": part("A", o1), "2": part("B", o2)}}
def body(t):
    return json.dumps({"bm": "", "events": {"e1": ev("A", "B", {"1": mk("To Win", 1.5 + t / 100, 2.5), "2": mk("Set Winner", 1.7, 2.1), "3": mk("Total Games", 1.9, 1.9)}),
                                           "e2": ev("C", "D", {"1": mk("Home/Away", 1.4, 3.0), "2": mk("Home/Away (map 1)", 1.4, 3.0), "3": mk("Handicap", 1.9, 1.9)})}})
def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

root = tempfile.mkdtemp()
t0 = calendar.timegm((2026, 11, 19, 4, 0, 0))
rows = [{"recv_ns": int((t0 + i) * 1e9), "body": body(i)} for i in range(30)]
rows.append({"recv_ns": int((t0 + 31) * 1e9), "body": "not json"})
rows.append({"recv_ns": int((t0 + 32) * 1e9), "body": json.dumps({"bm": "", "events": []})})
src = os.path.join(root, "tennis_payloads", "tennis_2026111904.jsonl.gz"); write(src, rows)
young = os.path.join(root, "tennis_payloads", "tennis_2026111908.jsonl.gz"); write(young, rows[:3])
now = t0 + 3600 * 4 + 5                      # 08:00:05Z; hour 04 ended 05:00 (3h old), hour 08 is current

# reduce_body keeps only the tennis winner market and leaves everything else
nb, k = C.reduce_body("tennis", body(1)); d = json.loads(nb)
check(list(d["events"]["e1"]["odds"].values())[0]["name"] == "To Win" and len(d["events"]["e1"]["odds"]) == 1, "tennis keeps only To Win")
check(k == 5 and d["events"]["e1"]["score"] == "1-0" and d["events"]["e1"]["team_info"]["home"]["name"] == "A", "dropped 5 markets (2 in e1, 3 in e2 for tennis), event fields kept")
nb2, k2 = C.reduce_body("hockey_nhl", body(1)); d2 = json.loads(nb2)
check(sorted(m["name"] for m in d2["events"]["e2"]["odds"].values()) == ["Home/Away", "Home/Away (map 1)"], "hockey keeps Home/Away (and map variants like signed v2 for esports)")
check(C.reduce_body("tennis", "not json") == ("not json", 0), "bad json unchanged")

# dry run changes nothing; --apply replaces only the old, verified file in place (same name), current hour untouched
before = open(src, "rb").read()
rc = C.main(["--root", root, "--sports", "tennis", "--now", str(now)])
check(rc == 0 and open(src, "rb").read() == before and not os.path.exists(src + ".compacted") and not os.path.exists(src + ".compact.tmp"), "dry run leaves every file as it was")
yb = open(young, "rb").read()
rc = C.main(["--root", root, "--sports", "tennis", "--now", str(now), "--apply"])
check(rc == 0 and open(young, "rb").read() == yb and not os.path.exists(young + ".compacted"), "current hour (younger than 3 h) untouched")
check(os.path.exists(src + ".compacted") and os.path.getsize(src) < len(before), "old hour replaced in place and smaller")
rr = list(C.rows_of(src))
check(len(rr) == 32 and [r["recv_ns"] for r in rr] == [r["recv_ns"] for r in rows], "same rows, same recv_ns, same name")
check(all("Set Winner" not in r["body"] and "Total Games" not in r["body"] for r in rr[:30]) and all("To Win" in r["body"] for r in rr[:30]), "only the winner market remains")
rc = C.main(["--root", root, "--sports", "tennis", "--now", str(now), "--apply"])
check(rc == 0, "second run skips the already compacted file")

# planted faults: verify must fail (and nothing is deleted)
src2 = os.path.join(root, "tennis_payloads", "tennis_2026111903.jsonl.gz"); write(src2, rows)
dst2 = os.path.join(root, "x_2026111903.jsonl.gz"); C.compact_file("tennis", src2, dst2)
check(C.verify("tennis", src2, dst2)[0], "clean file verifies")
def corrupt(mutate):
    rr = list(C.rows_of(dst2)); mutate(rr); write(dst2, rr); r = C.verify("tennis", src2, dst2); C.compact_file("tennis", src2, dst2); return r
def drop_winner(rr):
    d = json.loads(rr[5]["body"]); d["events"]["e1"]["odds"] = {}; rr[5]["body"] = json.dumps(d)
def change_price(rr):
    d = json.loads(rr[6]["body"]); d["events"]["e1"]["odds"]["1"]["participants"]["1"]["value_eu"] = "9.99"; rr[6]["body"] = json.dumps(d)
def change_time(rr): rr[7]["recv_ns"] += 1
def drop_row(rr): rr.pop()
def drop_event_field(rr):
    d = json.loads(rr[8]["body"]); del d["events"]["e1"]["score"]; rr[8]["body"] = json.dumps(d)
for name, f in (("winner market dropped", drop_winner), ("price changed", change_price), ("recv_ns changed", change_time), ("row missing", drop_row), ("event field dropped", drop_event_field)):
    check(corrupt(f)[0] is False, "verify catches: " + name)
shutil.rmtree(root)
print("ALL PASS (%d checks)" % ok)
