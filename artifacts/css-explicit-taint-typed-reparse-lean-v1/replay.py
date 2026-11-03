import hashlib,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LEAN=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LEAN)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
assert len(sys.argv)==2 and Path(sys.argv[1]).name==sys.argv[1]
out=HERE/sys.argv[1];out.mkdir()
records=[]
names=re.findall(r'^theorem (\w+)',(HERE/'Reparse.lean').read_text(),re.M)
false_cases={
 'NativeOutputTaintLost': 'nativeLegacy (fun _ _ => some ⟨quoted, true⟩) dirty = some ⟨quoted, false⟩',
 'TaintSensitiveParseForcedValid': 'nativeTransported (fun _ bit => if bit then none else some ⟨quoted, false⟩) dirty = some ⟨quoted, true⟩',
 'LegacyPreservesExplicit': 'legacyReparse echo dirty = some ⟨quoted, true⟩',
 'TransportDropsExplicit': 'transportedReparse echo dirty = some ⟨quoted, false⟩',
 'InnerExplicitIgnored': 'transportedReparse echo ⟨quoted, true, false⟩ = some ⟨quoted, false⟩',
 'CleanInputContaminated': 'transportedReparse echo clean = some ⟨quoted, true⟩',
 'FailedParsePublishesDirty': 'withInitial ⟨quoted, false⟩ (transportedReparse (fun _ => none) dirty) = ⟨quoted, true⟩',
 'EqualPayloadMeansEqualProvenance': 'transportedReparse echo dirty = transportedReparse echo clean',
 'AggregateOriginLostAtHandoff': 'transportedReparse echo (wrap (publish dirtyWitness)) = some ⟨dirtyWitness.bytes, false⟩',
}


try:
 with tempfile.TemporaryDirectory(prefix='explicit-reparse-lean-',dir='/private/tmp') as temporary:
  scratch=Path(temporary);env=dict(os.environ,LEAN_PATH=str(scratch))
  modules=[]
  for row in json.loads((HERE/'IMPORT-PINS.json').read_text()):
   source=ROOT/row['path'];assert sha(source)==row['sha256']
   dest=scratch/(row['module'].replace('.','/')+'.lean');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);modules.append(row['module'])
  shutil.copyfile(HERE/'Reparse.lean',scratch/'Reparse.lean');shutil.copyfile(HERE/'Reparse.lean',out/'Reparse.lean');modules.append('Reparse')
  (scratch/'Audit.lean').write_text('import Reparse\n'+''.join('#print axioms ExplicitTaintReparse.'+n+'\n' for n in names))
  shutil.copyfile(scratch/'Audit.lean',out/'Audit.lean');modules.append('Audit')
  for name,claim in false_cases.items():
   text='import Reparse\nopen ExplicitTaintReparse RetainedAggregateTaint\nexample : '+claim+' := by decide\n'
   (scratch/(name+'.lean')).write_text(text);(out/(name+'.lean')).write_text(text);modules.append(name)
  for name in modules:
   path=name.replace('.','/');r=subprocess.run([str(LEAN),'-o',path+'.olean',path+'.lean'],cwd=scratch,env=env,capture_output=True,text=True,timeout=120)
   (out/(name+'.log')).write_text(r.stdout+r.stderr);records.append({'module':name,'exit':r.returncode})
   expected=name not in false_cases
   if (r.returncode==0)!=expected:raise RuntimeError(name)
   if not expected:assert 'Tactic `decide` proved that the proposition' in r.stdout and 'is false' in r.stdout
  audit=(out/'Audit.log').read_text();assert 'sorryAx' not in audit and 'Lean.ofReduceBool' not in audit
  assert audit.count('depends on axioms:')+audit.count('does not depend on any axioms')==len(names)
  axioms={n.strip() for group in re.findall(r'axioms: \[(.*?)\]',audit,re.S) for n in group.split(',') if n.strip()}
  assert axioms <= {'propext','Quot.sound','Classical.choice'}

finally:
 (out/'RESULT.json').write_text(json.dumps({'records':records,'scratch':str(scratch),'scratch_removed':not scratch.exists(),'source_sha256':sha(HERE/'Reparse.lean'),'theorems':names,'false_controls':list(false_cases)},indent=2)+'\n')
print('compiled',len(records),'modules; scratch removed')
