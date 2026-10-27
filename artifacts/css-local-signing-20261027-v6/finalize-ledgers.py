import hashlib,json,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OUT=ROOT/"artifacts/css-quote-scope-append-ledger-candidates-v1"
read=lambda p:json.loads(p.read_text())
check=read(OUT/"CHECK.json");binding=read(OUT/"BINDING.json")
name="artifacts/stylo-bloom-tools/CURRENT-COMMITS.json"
p=OUT/"candidate"/name;d=read(p)
d.setdefault("local_signing_history",[]).append(d["latest_signing"])
d["latest_signing"]={"status":"SIGNED_VERIFIED_LOCAL","fix":135,"native_commit":binding["native_commit"],"research_commit":binding["research_commit"],"verification":binding["signing_verification"]}
d.setdefault("verified_working_epoch_history",[]).append(d["latest_verified_working_epoch"])
d["latest_verified_working_epoch"]={"path":"artifacts/css-local-signing-20261027-v6/CURRENT-EPOCH.json","status":"Restored quote candidate and signed source; full source/binary/nested preservation verified after each successful commit","browser_binary_contains_fixes":[133,134,135]}
d.setdefault("research_signing_history",[]).append(d["latest_research_signing"])
d["latest_research_signing"]={"status":"SIGNED_VERIFIED_LOCAL","commits":{n:read(HERE/(n+"-receipt.json"))["commit"] for n in ["animation-research","followup-research","quote-research"]}}
d["latest_research_checkpoints"]["ordered_quote_scopes"]={"directory":"artifacts/css-quote-ordered-scopes-model-v1","audits":16,"canonical_transfer":False,"scope":"Uniform provider and structural tree premises; no complete native refinement."}
d["latest_research_checkpoints"]["counter_and_language_audits"]={"directories":["artifacts/css-counter-scope-append-adjacent-audit-v1","artifacts/css-quote-provider-freshness-audit-v1"],"status":"SOURCE_PROPOSALS_UNRUN","accepted_fix_increment":0}
p.write_text(json.dumps(d,indent=2)+"\n")
row=f"| 135: Contained quote append | `{binding['native_commit']}` | `{binding['research_commit']}` |\n"
for name in check["postimages"]:
 p=OUT/"candidate"/name
 if p.suffix!=".md":continue
 s=p.read_text()
 if not name.endswith("PLAN-OF-RECORD.md"):
  marker="|---|---|---|\n";assert marker in s;s=s.replace(marker,marker+row,1)
 redundant=" Preserve unresolved animated-cycle policy, current underlying-value provenance, dependency publication and memory-reporting obligations."
 s=s.replace(redundant,"",1)
 p.write_text(s)
check["postimages"]={n:hashlib.sha256((OUT/"candidate"/n).read_bytes()).hexdigest() for n in check["postimages"]}
check["root_adjustments"]="Add fix135 table rows, update current signing/epoch pointers with prior entries preserved in history, record bounded new research, remove repeated next-step sentence."
(OUT/"CHECK.json").write_text(json.dumps(check,indent=2)+"\n")
delta=[]
for n in check["postimages"]:
 before=(ROOT/n).read_text();after=(OUT/"candidate"/n).read_text()
 delta.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="a/"+n,tofile="b/"+n))
(OUT/"root-reviewed.patch").write_text("".join(delta))
print("Five candidate ledgers finalized; live ledgers unchanged.")
