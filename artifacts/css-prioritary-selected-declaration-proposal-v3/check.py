from pathlib import Path
import ast, difflib, hashlib, json, shutil, subprocess, tempfile, tomllib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REL=Path('servo/components/style/properties/cascade.rs')
base=(HERE/'base'/REL).read_bytes()
candidate=(HERE/'candidate'/REL).read_bytes()
assert hashlib.sha256(base).hexdigest()=='2cc7b3d4047b9759277f41809ad7ba7baef99431c26b608bcf459b2d83764656'
expected=''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/'+str(REL),tofile='b/'+str(REL)))
assert (HERE/'native.patch').read_text()==expected
previous=ROOT/'artifacts/css-prioritary-selected-declaration-proposal-v2'
for path,digest in json.loads((HERE/'REFERENCES.json').read_bytes()).items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
before='                if rollback_allows\n                    && entry'
after='                if rollback_allows\n                    && longhand != LonghandId::Appearance\n                    && entry'
old=(previous/'candidate'/REL).read_text()
assert old.count(before)==1 and candidate.decode()==old.replace(before,after)
assert (HERE/'V2-DELTA.patch').read_text()==''.join(difflib.unified_diff(old.splitlines(True),candidate.decode().splitlines(True),fromfile='v2/'+str(REL),tofile='b/'+str(REL)))
metadata=ROOT/'artifacts/css-priority-longhand-metadata-source-v1/longhands.toml'
assert hashlib.sha256(metadata.read_bytes()).hexdigest()=='36e1e5c382dd8f9abb5e3e5fe48338d96908859e0dfe4dbedec71208320201d9'
data=ROOT/'artifacts/css-animation-contextual-attr-source-admission-v1/frozen/servo/components/style/properties/data.py'
assign=next(n for n in ast.parse(data.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRIORITARY_PROPERTY_DEPENDENCIES' for t in n.targets))
priorities=ast.literal_eval(assign.value)
properties=tomllib.loads(metadata.read_text())
ignored=sorted(name for name in priorities if properties[name].get('ignored_when_colors_disabled'))
assert ignored==['color-scheme']
formatter=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
assert hashlib.sha256(formatter.read_bytes()).hexdigest()=='ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
subprocess.run([str(formatter),'--check','--edition','2024','--config','match_block_trailing_comma=true,reorder_imports=true',str(HERE/'candidate'/REL)],check=True)
scratch=Path(tempfile.mkdtemp(prefix='css-priority-selection-patch-'))
try:
    target=scratch/REL
    target.parent.mkdir(parents=True)
    target.write_bytes(base)
    for reverse,wanted in [(False,candidate),(True,base)]:
        result=subprocess.run(['patch','-p1','--batch']+(['-R'] if reverse else []),input=expected,text=True,cwd=scratch,capture_output=True)
        assert result.returncode==0,result.stdout+result.stderr
        assert target.read_bytes()==wanted
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
result={'exact_base_relative_patch':True,'forward_reverse':True,'rustfmt_check':True,'metadata_current_ignored_priorities':ignored,'scratch_removed':str(scratch),'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'real_stylo_typecheck':False,'native_execution':False,'semantic_operation_checks_pending':True}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
