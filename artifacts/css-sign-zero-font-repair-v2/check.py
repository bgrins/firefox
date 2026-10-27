import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def function(s, key):
    i = s.index(key)
    j = s.index('{', i) + 1
    level = 1
    while level:
        level += (s[j] == '{') - (s[j] == '}')
        j += 1
    return s[i:j]


for name, pin in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
for role, entries in json.loads((HERE / 'SOURCE-PINS.json').read_text()).items():
    if role == 'revision':
        continue
    for name, pin in entries.items():
        assert hashlib.sha256((HERE / role / name).read_bytes()).hexdigest() == pin, name
path = 'servo/components/style/values/specified/length.rs'
old = (HERE / 'source' / path).read_text()
new = (HERE / 'candidate' / path).read_text()
values = (HERE / 'source/servo/components/style/values/mod.rs').read_text()
computed = (HERE / 'source/servo/components/style/values/computed/length.rs').read_text()
normal = function(values, 'pub fn normalize(')
sign = function(values, 'pub fn calc_sign(')
finite = function(computed, 'pub fn finite(')
normalized = function(computed, 'pub fn normalized(')
for name in ['font_relative_to_computed_value', 'reference_font_size_and_length', 'viewport_percentage_to_computed_value', 'container_relative_to_computed_value', 'servo_character_width_to_computed_value']:
    a = function(old, 'fn ' + name + '(')
    b = function(new, 'fn ' + name + '(')
    expected = a.replace('.finite()', '').replace('crate::values::normalize(trunc_scaled)', 'trunc_scaled')
    if name == 'font_relative_to_computed_value':
        expected = expected.replace('(reference_size * length)', 'reference_size * length')
    if name == 'servo_character_width_to_computed_value':
        expected = expected.replace('(average_advance * (cols - 1.0) + max_advance)', 'average_advance * (cols - 1.0) + max_advance')
    assert expected == b, name
source = '''#![allow(dead_code)]
type CSSFloat=f32;
trait Zero { fn is_zero(&self)->bool; }
impl Zero for f32 { fn is_zero(&self)->bool {*self==0.0} }
mod values {use super::{CSSFloat,Zero};
''' + normal + '\n' + sign + '''}
#[derive(Clone,Copy)] struct CSSPixelLength(f32);
impl CSSPixelLength { fn new(v:f32)->Self{Self(v)}
''' + finite + '\n' + normalized + '''}
fn same(a:f32,b:f32)->bool{(a.is_nan()&&b.is_nan())||a.to_bits()==b.to_bits()}
fn main(){
 let cs=[f32::NAN,f32::INFINITY,f32::NEG_INFINITY,0.0,-0.0,1.0,-1.0,2.0,-2.0,f32::from_bits(1),-f32::from_bits(1),f32::MAX,f32::MIN];
 let bs=[0.0f32,-0.0,0.5,1.0,16.0,60.0,6000.0];
 let mut count=0;
 for c in cs {for b in bs {
  let font=b*c;
  let viewport=((b as f64*c as f64/100.).trunc()/60.) as f32;
  let container=(b as f64*c as f64/100.) as f32;
  let absolute=c*b;
  let cols=c as i32 as f32;let char_width=(b*0.5)*(cols-1.0)+b;
  for (i,raw) in [font,viewport,container,absolute,char_width].into_iter().enumerate(){
   let old=if i==1 {CSSPixelLength::new(values::normalize(raw))}else{CSSPixelLength::new(raw).finite()};
   let wrapper=if i==1 {CSSPixelLength::new(raw).normalized()}else{CSSPixelLength::new(raw).finite()};
   assert!(same(old.0,wrapper.0));
   let expected=if raw.is_nan(){f32::NAN}else if raw==0.0{raw}else if raw<0.0{-1.0}else{1.0};
   assert!(same(values::calc_sign(raw),expected));
   if i<4 && c.is_nan(){assert!(raw.is_nan());}
   if i<4 && c.is_infinite() && b==0.0 {assert!(raw.is_nan());}
   count+=1;
  }
 }}
 assert_eq!(((60.0f64/100.).trunc()/60.)as f32,0.0);
 assert!(((60.0f64*2.0/100.).trunc()/60.)as f32>0.0);
 println!("{} scalar per-unit checks",count);
}
'''
with tempfile.TemporaryDirectory(prefix='sign-propagation-') as tmp:
    temp = Path(tmp)
    (temp / 'helper.rs').write_text(source)
    runs = []
    for opt in ['0', '2']:
        cmd = ['rustc', '--edition=2021', '-C', 'opt-level=' + opt, str(temp / 'helper.rs'), '-o', str(temp / 'helper')]
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        r = subprocess.run([str(temp / 'helper')], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        runs.append({'optimization': opt, 'compile_exit': 0, 'run_exit': 0, 'stdout': r.stdout})
    scratch = temp / 'git'
    scratch.mkdir()
    subprocess.run(['git', 'init', '-q', str(scratch)], check=True)
    for f in (HERE / 'source').rglob('*'):
        if f.is_file():
            dest = scratch / f.relative_to(HERE / 'source')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)
    patch = str(HERE / 'native-and-test.patch')
    for args in [['--check'], []]:
        subprocess.run(['git', '-C', str(scratch), 'apply', *args, patch], check=True)
    for f in (HERE / 'candidate').rglob('*'):
        if f.is_file():
            assert (scratch / f.relative_to(HERE / 'candidate')).read_bytes() == f.read_bytes()
    for args in [['--reverse', '--check'], ['--reverse']]:
        subprocess.run(['git', '-C', str(scratch), 'apply', *args, patch], check=True)
    for f in (HERE / 'source').rglob('*'):
        if f.is_file():
            assert (scratch / f.relative_to(HERE / 'source')).read_bytes() == f.read_bytes()
fixture = 'testing/web-platform/tests/css/css-values/sign-zero-font-basis.html'
assert (HERE / 'candidate' / fixture).read_bytes() == (ROOT / 'artifacts/css-sign-zero-font-special-controls-v1/probe.html').read_bytes()
print(json.dumps({'status': 'PASS', 'scope': 'Exact source-body delta checks and scalar arithmetic/terminal-policy adapters; not full provider, parser or Gecko compilation.', 'runs': runs, 'helper_sha256': hashlib.sha256(source.encode()).hexdigest(), 'rustc': subprocess.check_output(['rustc', '--version'], text=True).strip(), 'scratch_git_apply_reverse_exact': True, 'fourteen_case_fixture_transfer': True, 'temporary_products_removed': True}, indent=2))
