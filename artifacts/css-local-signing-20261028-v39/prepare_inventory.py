import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p:json.loads(p.read_bytes())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda p,v:p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
assert read(HERE/'INPUTS.json')['execution_enabled'] is False
base = read(ROOT/'artifacts/css-local-signing-20261028-v38/CURRENT-EPOCH.json')['committed_research_working_payloads']
groups = {
 'cleanup':['css-terminal-symbol-cleanup-inventory-v2','css-terminal-symbol-next-inventory-v1','css-terminal-symbol-cleanup-v1','css-terminal-symbol-cleanup-v2','css-terminal-symbol-cleanup-runtime-1','css-terminal-symbol-cleanup-runtime-2'],
 'linear':['css-linear-second-position-reversible-pair-v1','css-linear-second-position-reversible-pair-v2','css-linear-second-stop-wpt-runner-v1','css-linear-second-stop-wpt-runner-v2','css-linear-second-position-reversible-pair-runtime-1','css-linear-second-position-prebuild-recovery-v1','css-linear-second-position-reversible-pair-runtime-2','css-linear-second-stop-pair-review-v1','css-linear-guard-pair-raw-index-refresh-v1','css-linear-guard-pair-raw-index-refresh-runtime-1','css-linear-second-position-final-scope-review-v1','css-linear-second-position-promotion-v1','css-linear-second-position-wpt-rename-v1','css-untracked-audit-post-linear-promotion-20261028-v1','css-untracked-audit-post-linear-rename-20261028-v1','css-linear-second-position-wpt-rename-runtime-1','css-linear-second-position-landing-payload-v1','css-linear-second-position-acceptance-draft-v1','css-linear-second-position-final-wpt-v2','css-linear-second-position-final-wpt-v1'],
 'final_validation':['css-linear-second-position-final-validation-v1','css-linear-second-position-promotion-runtime-v1','css-linear-second-position-final-review-v1','css-linear-second-position-acceptance-v1'],
 'separate_round_research':['css-round-context-quotient-repair-v2','css-round-quotient-prerequisite-observation-v1'],
}
allpins,validationpins,packages = {},{},[]
for category,dirs in groups.items():
 for name in dirs:
  directory=ROOT/'artifacts'/name;manifest=directory/'FILES.json'
  record=read(manifest);entries=record.get('files',record);pins={}
  for name,item in entries.items():
   path=directory/name
   assert path.is_file() and not path.is_symlink() and not Path(name).is_absolute() and '..' not in Path(name).parts
   expected=item['sha256'] if isinstance(item,dict) else item
   assert sha(path)==expected
   if isinstance(item,dict) and 'bytes' in item:assert path.stat().st_size==item['bytes']
   pins[str(path.relative_to(ROOT))]=expected
  pins[str(manifest.relative_to(ROOT))]=sha(manifest)
  assert not set(pins)&(set(allpins)|set(validationpins))
  omitted={n:p for n,p in pins.items() if base.get(n)==p}
  selected={n:p for n,p in pins.items() if n not in omitted}
  (validationpins if category=='final_validation' else allpins).update(selected)
  packages.append({'directory':str(directory.relative_to(ROOT)),'category':category,'manifest_sha256':sha(manifest),'selected_files':len(selected),'already_signed_identical':omitted})
save(HERE/'research-selection.json',{'id':'research','files':sorted(allpins),'source_pins':allpins,'message':'No bug - Preserve linear easing validation research and separate Round observations. r?#firefox-style-system-reviewers'})
save(HERE/'validation-selection.json',{'id':'validation','files':sorted(validationpins),'source_pins':validationpins,'message':'No bug - Record final linear easing guard validation. r?#firefox-style-system-reviewers'})
save(HERE/'INVENTORY.json',{'status':'DRAFT_NOT_FROZEN','packages':packages,'research_files':len(allpins),'validation_files':len(validationpins),'pending':['actual rename runtime and post-rename audit','renamed landing payload and actual final manifest parser proof','final promoted build/WPT/lint/acceptance packet and independent review','post-native readout successor with actual receipt hashes'],'native_selection_sha256':sha(HERE/'native-selection.json'),'no_live_actions':True})
print(json.dumps({'research_files':len(allpins),'validation_files':len(validationpins),'packages':len(packages),'selection_sha256':sha(HERE/'research-selection.json')}))
