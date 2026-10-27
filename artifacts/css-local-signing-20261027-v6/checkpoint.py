import hashlib,json,os,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
GIT=["git","--no-optional-locks","-c","core.fsmonitor=false"]
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS="0"))
receipts={n:read(HERE/(n+"-receipt.json")) for n in ["animation-research","followup-research","quote-research","quote-fix"]}
assert all(r["signature_verified"] and r["working_bodies_and_nested_index_preserved"] for r in receipts.values())
pins=read(ROOT/"artifacts/css-unfinished-work-checkpoint-20261027-v4/SOURCE-PINS.json")
assert len(pins)==131
assert all(sha(ROOT/n)==v for n,v in pins.items())
tracked=set(git("ls-files","-z","--",*pins).decode().split("\0"))
modified=set(git("diff","--name-only").decode().splitlines())
remaining=(set(pins)-tracked)|(set(pins)&modified)
assert len(remaining)==128,len(remaining)
(HERE/"WIP-PRESERVATION.json").write_text(json.dumps({"snapshot":"artifacts/css-unfinished-work-checkpoint-20261027-v4","all_131_bodies_match":True,"remaining_unfinished_paths":sorted(remaining),"remaining_count":128},indent=2)+"\n")
body="# Local signing checkpoint\n\n"
for n,r in receipts.items():body+=f"- {n}: `{r['commit']}` (signature verified).\n"
body+="\nQuote fix 135 contains exactly two Gecko files and one WPT; its research is the immediate parent. The controlled browser comparison passes 64 cases with the fix, reproduces 12 failures without it, and passes all 64 again after restoration. All 18 existing regressions are unchanged. Both builds and WPT lint passed. The ledger now lists 134 committed fixes, with held repair 120 excluded.\n\nThe new ordered-scope Lean results remain standalone research, not an increase in canonical CSS-spec coverage. Animation integration and counter/language proposals remain unfinished. All 131 source/fixture/proof bodies in the committed v4 recovery snapshot still match; three are now the standalone quote commit, and the other 128 remain in the working tree. No duplicate snapshot is needed.\n\nNothing was pushed. Generated staged patches and redundant per-commit epoch copies are omitted; Git objects, signing receipts, the initial/ledger epochs and sealed comparison evidence preserve the relevant state. The current mutable continuation epoch is CURRENT-EPOCH.json in this directory.\n"
(HERE/"CHECKPOINT.md").write_text(body)
files=set(read(ROOT/"artifacts/css-quote-scope-append-ledger-candidates-v1/CHECK.json")["postimages"])
for folder in ["css-quote-scope-append-ledger-proposal-v1","css-quote-scope-append-ledger-candidates-v1"]:
 for p in (ROOT/"artifacts"/folder).rglob("*"):
  assert not p.is_symlink()
  if p.is_file():files.add(str(p.relative_to(ROOT)))
for p in HERE.iterdir():
 if not p.is_file() or p.name=="CURRENT-EPOCH.json" or p.name.endswith("-staged.patch"):continue
 if p.name.endswith("-EPOCH.json") and p.name not in ["INITIAL-EPOCH.json","LEDGER-EPOCH.json"]:continue
 assert p.suffix in [".py",".json",".log",".md",".txt"],p
 files.add(str(p.relative_to(ROOT)))
for name in ["research-checkpoint-receipt.json","research-checkpoint-signature.log","research-checkpoint-commit.log"]:
 p=ROOT/"artifacts/css-local-signing-20261027-v5"/name
 if p.exists() and not git("ls-files","--",str(p.relative_to(ROOT))).strip():files.add(str(p.relative_to(ROOT)))
item={"id":"research-checkpoint","files":sorted(files),"message":"No bug - Update CSS fix ledger and signed research checkpoint. r?#firefox-style-system-reviewers","source_pins":{n:sha(ROOT/n) for n in files},"source_modes":{n:"100755" if (ROOT/n).stat().st_mode&stat.S_IXUSR else "100644" for n in files}}
with (HERE/"research-checkpoint-plan.json").open("x") as f:json.dump(item,f,indent=2,sort_keys=True);f.write("\n")
print("Checkpoint prepared:",len(files),"files; 128 unfinished bodies preserved.")
