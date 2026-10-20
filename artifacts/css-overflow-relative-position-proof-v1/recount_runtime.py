#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parent
rows=[]
for directory,count,changed,kept,existing_count in [
    ("native-runtime",140,30,110,35),("rtl-runtime",280,60,220,61)]:
    subtests=[];files=[]
    for variant in ["baseline","candidate"]:
        sub={};ends={}
        for line in (ROOT/directory/variant/"raw.json").read_text().splitlines():
            event=json.loads(line)
            if event.get("action")=="test_status" and "relative-position-overflow-continuations" in event["test"]:
                key=(event["test"],event["subtest"])
                assert key not in sub
                sub[key]=event["status"]
            if event.get("action")=="test_end" and "relative-position-overflow-continuations" not in event["test"]:
                assert event["test"] not in ends
                ends[event["test"]]=event["status"]
        assert len(sub)==count,(directory,len(sub))
        assert len(ends)==existing_count,(directory,len(ends))
        subtests.append(sub);files.append(ends)
    assert subtests[0].keys()==subtests[1].keys()
    transitions=Counter((subtests[0][k],subtests[1][k]) for k in subtests[0])
    assert transitions=={("FAIL","PASS"):changed,("PASS","PASS"):kept}
    assert files[0]==files[1]
    by_phase=Counter(k[1].split(":",1)[0] for k,v in subtests[0].items() if v=="FAIL")
    rows.append({"directory":directory,"subtests":count,"fixed":changed,"preserved":kept,
                 "baseline_failure_phases":dict(by_phase),"unchanged_existing_files":dict(Counter(files[0].values()))})
print(json.dumps(rows,indent=2))
