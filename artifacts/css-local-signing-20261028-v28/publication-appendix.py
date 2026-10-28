import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def verify():
    plan=read(HERE/"SYNC-PLAN.json");review=ROOT/plan["posthoc_review"]
    assert sha(review/"FILES.json")==plan["posthoc_review_manifest_sha256"]
    for name,pin in read(review/"FILES.json").items():assert sha(review/name)==pin["sha256"]
    inventory=read(review/"RUNTIME-INVENTORY.json");directory=ROOT/inventory["directory"]
    files,links={},{}
    for path in directory.rglob("*"):
        name=str(path.relative_to(directory))
        if path.is_symlink():links[name]=str(path.resolve())
        elif path.is_file():files[name]={"sha256":sha(path),"bytes":path.stat().st_size}
    assert links==inventory["links"]==read(directory/"SYMLINKS.json")
    assert set(files)==set(inventory["files"])|{"FILES.json","SYMLINKS.json"}
    assert len(inventory["files"])==72 and all(files[n]==pin for n,pin in inventory["files"].items())
    assert read(directory/"FILES.json")=={n:pin for n,pin in files.items() if n!="FILES.json"}
    for name,pin in plan["publication_metadata"].items():assert sha(ROOT/name)==pin
    assert not (directory/"RESULT.json").exists() and read(directory/"OUTER.json")["exit"]==1
    assessment=read(directory/"ASSESSMENT.json");capsule=ROOT/assessment["capsule_directory"]
    run=load("appendix_run",capsule/"run.py");run.authenticate(capsule,assessment["capsule_manifest_sha256"])
    policy=read(capsule/"POLICY.json");parser=load("appendix_assess",capsule/"assess.py");checks=load("appendix_checks",ROOT/policy["helpers"]["checks"])
    events=[json.loads(line) for line in (directory/"raw.jsonl").read_text().splitlines()]
    replay=parser.assess(events,1,policy,checks,original=None,run_binding=read(directory/"APPLICATION-METADATA.json"))
    for key,value in replay.items():
        if key not in ["oracle_caveat","subtest_cardinality_policy"]:assert assessment[key]==value
    assert assessment["complete"] and assessment["execution_preserved"]
    observations=load("appendix_history",capsule/"observations.py");histories=observations.validate(ROOT,capsule,policy,SimpleNamespace(**vars(run)))
    assert observations.compare(assessment,histories,policy)==read(directory/"COMPARISON.json")
    assert read(directory/"PRE.json")==read(directory/"POST.json")
    assert read(directory/"CLEANUP.json")["owned_group_absent"] and read(directory/"CLEANUP.json")["temporary_root_removed"]
    return {"original_payloads_unchanged":72,"later_metadata_files":2,"raw_assessment_and_comparison_replayed":True,"original_wrapper_exit":1,"original_RESULT_absent":True,"WPT_exit_is_derived_not_separately_observed":True,"runtime_mutations":False}

if __name__=="__main__":print(json.dumps(verify(),indent=2))
