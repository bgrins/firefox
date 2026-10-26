import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
sys.dont_write_bytecode=True
import ast,copy,importlib.util,json
from pathlib import Path
here=Path(__file__).resolve().parent
for name in ["run.py","cleanup.py","validate.py"]:ast.parse((here/name).read_text())
spec=importlib.util.spec_from_file_location("cost_validation",here/"validate.py");v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
c=json.loads((here/"CONFIG.json").read_text());v.validate_config(c);configs=v.configurations(c);rows=[]
for round_no in range(c["measured_rounds"]):
    for slot in range(len(configs)):
        ordinal=(slot+round_no+c["warmup_rounds"])%len(configs);kind,state,count=configs[ordinal]
        hot=[]
        for bucket in ["hotSame","hotCycle"]:
            q,r=divmod(c["hot_reads"],count)
            index_sum=c["hot_reads"]*(count-1) if bucket=="hotSame" else q*count*(count-1)//2+r*(r-1)//2
            hot.append({"bucket":bucket,"reads":c["hot_reads"],"elapsedMs":2,"checksum":132*c["hot_reads"]+32*index_sum,"mismatches":0,"firstMismatch":None})
        rows.append({"round":round_no,"slot":slot,"ordinal":ordinal,"kind":kind,"state":state,"count":count,
          "calibration":[{"width":w,"rects":[v.expected(i,w) for i in range(count)]} for w in [160,168,160]],
          "hiddenOuter":[10,10,160,64],"outers":[[10,10,168 if i%2==0 else 160,64] for i in range(c["iterations"])],
          "times":{k:[0]*c["iterations"] for k in v.BUCKETS},
          "observations":[{"bucket":b,"iteration":i,"index":count-1,"width":168 if i%2==0 else 160,"rect":v.expected(count-1,168 if i%2==0 else 160)} for i in range(c["iterations"]) for b in ["first","repeat"]],
          **{k:[v.expected(i,160) for i in range(count)] for k in ["restored","cleanVisible","cleanReady","cleanAfter"]},"hotRows":hot})
o={"complete":True,"label":"synthetic","config":c,"elapsedMs":1,"rows":rows};summary=v.validate(o,c,"synthetic")
checks=[]
def rejects(name,change):
    x=copy.deepcopy(o);change(x)
    try:v.validate(x,c,"synthetic")
    except (ValueError,KeyError,TypeError):checks.append(name);return
    raise RuntimeError("Accepted corrupt receipt: "+name)
rejects("wrong_row",lambda x:x["rows"][0].update(kind="wrong"))
rejects("wrong_geometry_calibration",lambda x:x["rows"][0]["calibration"][0]["rects"][0].__setitem__(2,0))
rejects("wrong_query_order",lambda x:x["rows"][0]["observations"][0].update(bucket="repeat"))
rejects("missing_query",lambda x:x["rows"][0]["observations"].pop())
rejects("wrong_hot_checksum",lambda x:x["rows"][0]["hotRows"][0].update(checksum=0))
rejects("wrong_hot_read_count",lambda x:x["rows"][0]["hotRows"][0].update(reads=0))
rejects("negative_timing",lambda x:x["rows"][0]["times"]["first"].__setitem__(0,-1))
rejects("missing_clean_calibration",lambda x:x["rows"][0].update(cleanReady=[]))
bad=copy.deepcopy(o);bad["rows"][0]["observations"][0]["rect"][2]=0
if v.validate(bad,c,"synthetic")["geometryMismatches"]!=1:raise RuntimeError("Incorrect geometry erased")
progress=v.expected_progress(c,"synthetic")
print(json.dumps({"status":"PASS_STATIC_ONLY","python_parsed":3,"synthetic_rows":summary["measuredRows"],"synthetic_reads":summary["queryReads"],"progress_events":len(progress),"negative_controls":checks,"wrong_recovery_geometry_retained":True,"browser_executed":False},indent=2))
