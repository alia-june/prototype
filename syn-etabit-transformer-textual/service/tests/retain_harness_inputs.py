"""Recover this development run's inputs by seed, verifying every recorded hash.

Normal harness runs now save inputs before execution. This bounded utility only
adds an index and inputs for an earlier run whose functional checks completed;
it never changes outcomes, original journals, or the saved failure artifacts.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from docstream_cpu.harness.core import RUNS_ROOT, encoded, save
from docstream_cpu.harness.generate import case, generate


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("run_id")
    args=parser.parse_args()
    root=(RUNS_ROOT/args.run_id).resolve()
    if not root.is_relative_to(RUNS_ROOT.resolve()) or not (root/"summary.json").is_file():
        raise ValueError("completed managed run required")
    summary=json.loads((root/"summary.json").read_text())
    index=[]
    for mode in summary["modes"]:
        if mode["mode"] not in ("rigid","fuzzy","torture"):
            continue
        folder=root/mode["mode"]/"recovered-inputs"
        folder.mkdir(exist_ok=False)
        generated=list(generate(summary["seed"],summary["limits"]["generated_cases"])) if mode["mode"]=="fuzzy" else []
        for number,item in enumerate(mode["cases"]):
            name=item["name"]
            if mode["mode"]=="fuzzy":
                value=generated[int(name.split("-")[-1])]
            elif mode["mode"]=="rigid":
                if item["kind"]=="regression":
                    data={"test_id":name.removeprefix("regression-")}
                else:
                    data={}
                value=case(item["kind"],data,summary["seed"])
            else:
                data={"cycles":summary["limits"]["crash_cycles"]} if name=="crash_recovery" else {"requests":summary["limits"]["torture_loop_requests"]} if name=="network_load" else {}
                value=case(item["kind"],data,summary["seed"])
            actual=sha256(encoded(value)).hexdigest()
            if actual!=item["input_sha256"]:
                raise RuntimeError("recovered input differs: "+name)
            target=folder/f"{number:04d}-{actual[:12]}.json"
            save(target,value)
            index.append({"mode":mode["mode"],"name":name,"input_sha256":actual,"input_file":str(target)})
    save(root/"RECOVERED_INPUTS.json",{"method":"deterministic seed regeneration; every original input_sha256 matched; results unchanged","cases":index})
    print(json.dumps({"verified_inputs":len(index),"root":str(root)}))


if __name__=="__main__":
    main()
