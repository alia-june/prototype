from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=subprocess.run([sys.executable,str(ROOT/"runner"/"analyze_coverage.py")],capture_output=True,text=True)
assert p.returncode==0,p.stdout+p.stderr
r=json.loads((ROOT/"coverage"/"coverage-report.json").read_text(encoding="utf-8"))
assert r["fixture_count"]==74,r["fixture_count"]
assert r["dimensions"]["failure_classes"]["total_items"]==12
unc={x["item"]:x for x in r["dimensions"]["uncertainty_states"]["items"]}
for k in ("CONFLICTED","NOT_APPLICABLE","CANNOT_INFER","UNRESOLVED","NO_LINEAR_READING_ORDER"):
    assert unc[k]["status"]=="COVERED",(k,unc[k])
assert r["dimensions"]["source_realism"]["items"][0]["item"]=="synthetic_text"
print("coverage-test: PASS")
