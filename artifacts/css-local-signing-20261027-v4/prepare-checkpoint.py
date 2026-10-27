import hashlib,json,os,stat,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS="0")
GIT=["git","--no-optional-locks","-c","core.fsmonitor=false"]
def git(*args,env=ENV):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
base=git("rev-parse","HEAD").decode().strip()
assert base==json.loads((HERE/"cubic-native-receipt.json").read_text())["commit"]
assert not git("diff","--cached","--name-only")
prior=json.loads((ROOT/"artifacts/css-unfinished-work-checkpoint-20261027-v1/SOURCE-PINS.json").read_text())
modified=set(git("diff","--name-only").decode().splitlines())
assert {n for n in modified if not n.startswith("artifacts/")}<=set(prior)
if "--select-only" not in sys.argv:
 snapshot=ROOT/"artifacts/css-unfinished-work-checkpoint-20261027-v3"
 snapshot.mkdir(exist_ok=False)
 with tempfile.TemporaryDirectory(prefix="css-recovery-index-",dir="/private/tmp") as tmp:
  env=dict(ENV,GIT_INDEX_FILE=str(Path(tmp)/"index"))
  git("read-tree",base,env=env)
  names=Path(tmp)/"paths";names.write_bytes(b"".join(n.encode()+b"\0" for n in sorted(prior)))
  git("add","-f","--pathspec-from-file="+str(names),"--pathspec-file-nul",env=env)
  changed=git("diff","--cached","--name-only",base,env=env).decode().splitlines()
  pins={n:sha(ROOT/n) for n in changed}
  tree=git("write-tree",env=env).decode().strip()
  patch=snapshot/"unfinished.patch";patch.write_bytes(git("diff","--cached","--binary","--full-index",base,env=env))
  git("read-tree",base,env=env);git("apply","--cached",str(patch),env=env)
  assert git("write-tree",env=env).decode().strip()==tree
  for n,pin in pins.items():assert hashlib.sha256(git("show",":"+n,env=env)).hexdigest()==pin,n
  git("apply","--cached","--reverse",str(patch),env=env)
  assert git("write-tree",env=env)==git("rev-parse",base+"^{tree}")
 save(snapshot/"SOURCE-PINS.json",pins)
 save(snapshot/"BASE.json",{"commit":base,"tree":git("rev-parse",base+"^{tree}").decode().strip(),"snapshot_tree":tree})
 save(snapshot/"CHECK.json",{"files":len(pins),"exact_postimages":True,"reverse_restores_base_tree":True,"live_index_unchanged":not bool(git("diff","--cached","--name-only"))})
 (snapshot/"README.md").write_text(f"# Unfinished work checkpoint\n\nThis recovery patch preserves {len(pins)} unfinished project files, including native prototypes, unaccepted browser probes and proof-tool changes. It is not an accepted repair or a production patch. The 133 accepted fixes are committed separately.\n\nApply `unfinished.patch` to the commit in `BASE.json`; `SOURCE-PINS.json` records the exact resulting bodies. Application and reversal were verified in an isolated index. Unrelated untracked directories, build outputs and the separately committed CSS library are excluded. Native working files remain in place.\n\nThe current-provider animation prototype still needs integration work. The new provider resolver and canonical steps transfer remain prepared proposals. The installed local browser includes the signed steps and cubic-bezier fixes.\n")
 save(snapshot/"FILES.json",{str(f.relative_to(snapshot)):sha(f) for f in snapshot.iterdir() if f.is_file()})
 checkpoint=HERE/"CHECKPOINT.md"
 checkpoint.write_text(checkpoint.read_text()+f"\nThe [unfinished-work recovery snapshot](../css-unfinished-work-checkpoint-20261027-v3/README.md) preserves {len(pins)} remaining project files with verified patch application, exact bodies and reversal. These prototypes remain uncommitted in their native locations for continued development.\n")
packages=["css-integer-stored-range-metadata-correction-v1","css-integer-stored-range-metadata-correction-v2","css-steps-origin-library-proposal-v1","css-keyframe-provider-resolution-implementation-v1","css-keyframe-provider-resolution-self-review-v1","css-keyframe-provider-resolution-root-review-v1","css-keyframe-provider-resolver-host-preparation-v1","css-keyframe-provider-resolver-host-review-v1","css-keyframe-animated-provider-policy-v1","css-unfinished-work-checkpoint-20261027-v3"]
selected=set(json.loads((HERE/"LEDGER-PATHS.json").read_text()))
for name in packages:
 directory=ROOT/"artifacts"/name
 manifest=directory/"FILES.json"
 if not manifest.exists():manifest=directory/"DRAFT-FILES.json"
 entries=json.loads(manifest.read_text())
 selected.add(str(manifest.relative_to(ROOT)))
 for relative,pin in entries.items():
  f=directory/relative
  if isinstance(pin,dict):
   assert f.stat().st_size==pin["bytes"],str(f)
   pin=pin["sha256"]
  assert f.resolve().is_relative_to(directory.resolve()) and f.is_file() and sha(f)==pin,str(f)
  selected.add(str(f.relative_to(ROOT)))
for name in ["commit.py","update-ledger.py","prepare-checkpoint.py","CHECKPOINT.md","research-input.json","native-input.json","cubic-research-item.json","cubic-native-item.json","cubic-research-receipt.json","cubic-native-receipt.json","cubic-research-signature.log","cubic-native-signature.log","cubic-research-commit.log","cubic-native-commit.log","LEDGER-PREIMAGES.json","LEDGER-PATHS.json","LEDGER-EPOCH.json","steps-native-current.patch"]:
 selected.add(str((HERE/name).relative_to(ROOT)))
files=[]
for name in sorted(selected):
 current=(ROOT/name).read_bytes()
 old=subprocess.run(GIT+["show",base+":"+name],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 if old.returncode or old.stdout!=current:files.append(name)
item={"id":"research-checkpoint","message":"No bug - Checkpoint CSS verification research and fix ledger. r?#firefox-style-system-reviewers","files":files,"source_pins":{n:sha(ROOT/n) for n in files},"source_modes":{n:("100755" if (ROOT/n).stat().st_mode & stat.S_IXUSR else "100644") for n in files}}
save(HERE/"checkpoint-input.json",item)
print("Prepared checkpoint",len(files),"paths; recovery snapshot",json.loads((ROOT/"artifacts/css-unfinished-work-checkpoint-20261027-v3/CHECK.json").read_text())["files"],"files",flush=True)
