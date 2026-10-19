from pathlib import Path
import difflib,hashlib,json,subprocess
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
name='servo/components/style/properties/cascade.rs'
p=root/name;original=p.read_text()
old='''        if refs.flags.intersects(ReferenceFlags::ATTR) {
            self.update_attributes_map(context, value, attribute_tracker);
            if !refs.flags.intersects(ReferenceFlags::VAR) {
                return;
            }
        }
'''
new='''        if refs.flags.intersects(ReferenceFlags::ATTR) {
            self.update_attributes_map(context, value, attribute_tracker);
        }
'''
assert original.count(old)==1
receipt=json.loads((here/'baseline-v1-receipt.json').read_text())
assert receipt['all_inputs_unchanged']
assert hashlib.sha256(original.encode()).hexdigest()==receipt['pins_after'][name]
candidate=original.replace(old,new,1)
(here/'native-original.rs').write_text(original);(here/'native-candidate.rs').write_text(candidate)
base=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();assert base.count(old)==1
patch='diff --git a/'+name+' b/'+name+'\n'+''.join(difflib.unified_diff(base.splitlines(True),base.replace(old,new,1).splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(here/'native-only-v1.patch').write_text(patch)
test='testing/web-platform/tests/css/css-values/attr-noncustom-dependency-cycles.html'
patch+='diff --git a/'+test+' b/'+test+'\nnew file mode 100644\n'+''.join(difflib.unified_diff([], (root/test).read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+test))
(here/'native-wpt-v1.patch').write_text(patch)
p.write_text(candidate)
print('native+WPT patch',hashlib.sha256(patch.encode()).hexdigest())
