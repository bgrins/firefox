import copy
import hashlib
import json
import re
import resource
import subprocess
import sys
from pathlib import Path

from bridge import generate
from controls import CPP_MUTATIONS, LEAN_MUTATIONS
from prepare import BASE, ROOT, sha, sources


def run(command, prefix):
    result = subprocess.run(command, text=True, capture_output=True)
    prefix.with_suffix(".stdout").write_text(result.stdout)
    prefix.with_suffix(".stderr").write_text(result.stderr)
    prefix.with_suffix(".command.json").write_text(json.dumps({"command":command,"exit":result.returncode},indent=2)+"\n")
    return result


def reject_diagnostics(source, path, result, target):
    if result.returncode != 1 or result.stderr:
        raise RuntimeError("Wrong Lean mutation terminal")
    lines = source.splitlines()
    decls = [(i,line) for i,line in enumerate(lines,1) if re.match(r"^(theorem |def |inductive |structure |end |#print)",line)]
    spans = []
    for (start,line),(end,_) in zip(decls,decls[1:]):
        if line.startswith("theorem "):
            spans.append((line.split()[1],start,end))
    headers = re.findall(r"^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$",result.stdout,re.M)
    if len(headers) != len(re.findall(r"\berror(?:\([^\n)]*\))?:",result.stdout)):
        raise RuntimeError("Unlocated Lean diagnostic")
    owners = []
    for filename,line,message in headers:
        found = [n for n,a,b in spans if a <= int(line) < b]
        if filename != str(path) or len(found) != 1 or any(x in message for x in ["Unknown identifier","unexpected token","failed to synthesize"]):
            raise RuntimeError("Mutation failed outside theorem checking")
        owners.append(found[0])
    if target not in owners:
        raise RuntimeError("Mutation did not refute intended theorem: "+repr(owners))
    return owners


def main():
    if sys.flags.optimize or len(sys.argv) not in [2,3] or (len(sys.argv)==3 and sys.argv[2]!="--live"):
        raise RuntimeError("Usage: python3 check.py NEW_OUTPUT_DIRECTORY [--live]")
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    live = len(sys.argv)==3
    read = lambda name:(BASE/name).read_text()
    record = sources(read,live)
    tools = json.loads(read("TOOLCHAIN-v1.json"))
    for name,tool in tools.items():
        if sha(Path(tool["path"])) != tool["sha256"] or subprocess.check_output([tool["path"],"--version"],text=True) != tool["version"]:
            raise RuntimeError("Toolchain changed: "+name)
    lean,clang = tools["lean"]["path"],tools["clang"]["path"]
    paths = [BASE/n for n in read("tooling-paths-v1.txt").splitlines()] + [Path(lean),Path(clang)]
    if live:
        paths.append(ROOT/record["source"])
    before = {str(p):sha(p) for p in paths}
    source_controls=[]
    for row in record["records"]:
        name=row["snapshot"]
        try:
            sources(lambda n:read(n)+"\n" if n==name else read(n))
        except RuntimeError:
            source_controls.append(name)
        else:
            raise RuntimeError("Accepted source corruption")
    record_controls=[]
    faults=[]
    value=copy.deepcopy(record); value["records"].pop(); faults.append(("missing-row",value))
    value=copy.deepcopy(record); value["records"].append(value["records"][0]); faults.append(("duplicate-row",value))
    value=copy.deepcopy(record); value["unknown"]=True; faults.append(("extra-key",value))
    value=copy.deepcopy(record); value["source"]="other.cpp"; faults.append(("wrong-source",value))
    value=copy.deepcopy(record); value["records"][0]["sha256"]="f"*64; faults.append(("wrong-snapshot-digest",value))
    value=copy.deepcopy(record); value["records"][0]["kind"]="ResolveLineRange"; faults.append(("wrong-kind",value))
    value=copy.deepcopy(record); value["before_source_sha256"]="bad"; faults.append(("malformed-base-digest",value))
    value=copy.deepcopy(record); value["records"][0]["snapshot"]="unknown.inc"; faults.append(("unknown-snapshot",value))
    value=copy.deepcopy(record); del value["records"][0]["sha256"]; faults.append(("missing-digest",value))
    for label,value in faults:
        try:
            sources(lambda n:json.dumps(value) if n=="SOURCE-v1.json" else read(n))
        except RuntimeError:
            record_controls.append(label)
        else:
            raise RuntimeError("Accepted malformed source record")
    proof=read("GridAbspos.lean")
    if re.search(r"\b(sorry|admit|axiom)\b",proof):
        raise RuntimeError("Untrusted proof declaration")
    result=run([lean,str(BASE/"GridAbspos.lean")],out/"lean")
    if result.returncode or result.stderr or "warning:" in result.stdout or "error:" in result.stdout:
        raise RuntimeError("Positive Lean check failed")
    names=re.findall(r"^theorem (\w+)",proof,re.M)
    audits=re.findall(r"^'GridAbspos\.(\w+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",result.stdout,re.M)
    if [n for n,_ in audits] != names or any(set(a.split(", "))-{"","propext","Classical.choice","Quot.sound"} for _,a in audits):
        raise RuntimeError("Axiom audit mismatch")
    lean_controls=[]
    for label,(old,new,target) in LEAN_MUTATIONS.items():
        if proof.count(old)!=1:
            raise RuntimeError("Ambiguous Lean mutation")
        mutated=proof.replace(old,new)
        path=out/(label+".lean")
        path.write_text(mutated)
        result=run([lean,str(path)],out/("lean-"+label))
        lean_controls.append({"name":label,"failed_theorems":reject_diagnostics(mutated,path,result,target)})
    code=generate(read)
    source=out/"bridge.cpp"
    source.write_text(code)
    binary=out/"bridge"
    command=[clang,"-isysroot",tools["clang"]["sdk"],"-std=c++17","-O2","-fsanitize=undefined","-fno-sanitize-recover=all",str(source),"-o",str(binary)]
    result=run(command,out/"cpp-compile")
    if result.returncode or result.stdout or result.stderr:
        raise RuntimeError("C++ bridge compilation failed")
    result=run([str(binary)],out/"cpp-run")
    if result.returncode or result.stderr:
        raise RuntimeError("C++ bridge execution failed")
    counts=json.loads(result.stdout)
    if counts != {"normal_flow_cases":567000,"abspos_cases":542080,"bounded_distinct_projection_cases":344120}:
        raise RuntimeError("Changed finite case inventory")
    cpp_controls=[]
    for label,(name,old,new) in CPP_MUTATIONS.items():
        if read(name).count(old)!=1:
            raise RuntimeError("Ambiguous C++ mutation: "+label)
        mutated=generate(lambda n:read(n).replace(old,new) if n==name else read(n))
        source=out/(label+".cpp")
        source.write_text(mutated)
        binary=out/label
        result=run([clang,"-isysroot",tools["clang"]["sdk"],"-std=c++17","-O2","-fsanitize=undefined","-fno-sanitize-recover=all",str(source),"-o",str(binary)],out/("cpp-compile-"+label))
        if result.returncode or result.stdout or result.stderr:
            raise RuntimeError("Mutation did not compile: "+label)
        result=run([str(binary)],out/("cpp-run-"+label))
        if result.returncode != 1 or result.stdout or result.stderr.strip() not in {
            "normal-flow changed","abspos policy/finalizer mismatch","endpoint projection mismatch","independent endpoint witness mismatch"}:
            raise RuntimeError("Mutation did not fail a semantic assertion: "+label+repr((result.returncode,result.stderr)))
        cpp_controls.append({"name":label,"failure":result.stderr.strip()})
    after={str(p):sha(p) for p in paths}
    if before != after:
        raise RuntimeError("Inputs changed during replay")
    result={"status":"passed","live":live,"axiom_audits":audits,"lean_mutations":lean_controls,"cpp_cases":counts,"cpp_mutations":cpp_controls,"source_controls":source_controls,"record_controls":record_controls,"pins":before,"limits":["Theorem scope is integer endpoint policy; name resolution and C++ arithmetic/adapter correspondence remain premises.","Spec refinement excludes equal resolved endpoints and requires resolved endpoints within UA limits.","Finite compiled bridge uses scripted name lookup and release LineRange storage; it is not a Gecko build or native-name-resolution proof."]}
    (out/"RESULTS.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":"passed","axiom_audits":len(audits),"lean_mutations":len(lean_controls),"cpp_cases":counts,"cpp_mutations":len(cpp_controls),"source_controls":len(source_controls),"record_controls":len(record_controls)}))


if __name__=="__main__":
    main()
