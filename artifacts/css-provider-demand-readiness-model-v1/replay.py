import hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
assert hashlib.sha256(LEAN.read_bytes()).hexdigest() == "d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf"
out = P / "check"
out.mkdir(exist_ok=False)
controls = {
 "unknown_is_ready": "CanCompute .unknown (fun _ => True)",
 "empty_is_complete": "compute (fun _ => 800) (.contextual 0) = compute (fun _ => 200) (.contextual 0)",
 "applying_cache_is_ready": "lookup 1 (.applying 800) = some 800",
 "closed_frame_can_retry": "(begin (enumOnlySuspend popped)).isSome = true",
 "stale_ready_generation": "lookup 2 (.ready 1 800) = some 800",
 "duplicate_retry_effects": "badRetryEffects = 1",
 "demand_is_semantic_edge": "semanticEdge 1 0 = demandEdge 1 0",
}
records=[]
with tempfile.TemporaryDirectory(prefix="provider-demand-lean-") as tmp:
 scratch=Path(tmp)
 env=dict(os.environ, LEAN_PATH=str(scratch))
 for name in ["Admission", "Independence", "Demand"]:
  shutil.copyfile(P/(name+".lean"),scratch/(name+".lean"))
  r=subprocess.run([str(LEAN),"-j1","-o",name+".olean",name+".lean"],cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
  (out/(name+".log")).write_text(r.stdout)
  records.append({"name":name,"exit":r.returncode})
  assert r.returncode==0, r.stdout
 names=re.findall(r"^theorem (\w+)", (P/"Demand.lean").read_text(), re.M)
 audit="import Demand\n"+"".join("#print axioms ProviderDemand."+name+"\n" for name in names)
 (P/"Audit.lean").write_text(audit)
 (scratch/"Audit.lean").write_text(audit)
 r=subprocess.run([str(LEAN),"-j1","Audit.lean"],cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 (out/"Audit.log").write_text(r.stdout)
 assert r.returncode==0 and "sorryAx" not in r.stdout and "Lean.ofReduceBool" not in r.stdout
 for name, claim in controls.items():
  tactic = "change False; decide +kernel" if name == "unknown_is_ready" else "decide +kernel"
  source="import Demand\nopen ProviderDemand SelectedIndependence\nexample : "+claim+" := by "+tactic+"\n"
  (out/(name+".lean")).write_text(source)
  (scratch/"False.lean").write_text(source)
  r=subprocess.run([str(LEAN),"-j1","False.lean"],cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
  (out/(name+".log")).write_text(r.stdout)
  assert r.returncode!=0 and "proved that the proposition" in r.stdout and "false" in r.stdout, r.stdout
  records.append({"negative":name,"exit":r.returncode,"rejected_as_false":True})
(out/"RESULT.json").write_text(json.dumps({"theorems":len(names),"false_controls":len(controls),"records":records,"scratch_removed":not scratch.exists()},indent=2)+"\n")
print(json.dumps({"theorems":len(names),"false_controls":len(controls),"scratch_removed":not scratch.exists()}))
