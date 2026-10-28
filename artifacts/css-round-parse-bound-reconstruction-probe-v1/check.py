import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-round-context-quotient-repair-v2/base/servo/components/style/values/generics/calc.rs'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'b9a36918f1291b2c08cfb6d83aca73eb309185d1d2691961d6334b7bc69d1274'
source = SOURCE.read_text()
start = source.index('                if value_or_stop!(step.is_negative_leaf()) {', source.index('fn simplify'))
end = source.index('                SimplificationResult::Simplified', start) + len('                SimplificationResult::Simplified')
body = source[start:end]
(HERE / 'EXTRACTED.txt').write_text(body)
program = '''use std::ops::{Add, Sub, Rem};
#[derive(Clone,Copy)] enum RoundingStrategy { Nearest, Up, Down, ToZero }
enum SimplificationResult { Simplified }
#[derive(Clone,Copy)] struct Scalar(f32);
impl Scalar {
    fn try_op<O:Fn(f32,f32)->f32>(&self, other:&Self, op:O)->Result<Self,()> { Ok(Self(op(self.0,other.0))) }
    fn is_negative_leaf(&self)->Option<bool> { Some(self.0.is_sign_negative()) }
    fn is_zero_leaf(&self)->Option<bool> { Some(self.0==0.0) }
    fn negate(&mut self) { self.0 = -self.0; }
    fn lt(&self, other:&Self)->bool { self.0 < other.0 }
}
fn simplify(value:&mut Box<Scalar>, step:&mut Box<Scalar>, strategy:RoundingStrategy, result:&mut Scalar)->SimplificationResult {
    macro_rules! value_or_stop { ($value:expr) => {$value.unwrap()}; }
    macro_rules! replace_self_with { ($value:expr) => {*result = (*$value).clone()}; }
''' + body + '''
}
fn main() {
    use std::io::{self,Read};
    let mut input=String::new();io::stdin().read_to_string(&mut input).unwrap();
    for line in input.lines() {
        let words:Vec<_>=line.split_whitespace().collect();
        let a=u32::from_str_radix(words[0],16).unwrap();let b=u32::from_str_radix(words[1],16).unwrap();
        for mode in [RoundingStrategy::Nearest,RoundingStrategy::Up,RoundingStrategy::Down,RoundingStrategy::ToZero] {
            let mut result=Scalar(f32::NAN);
            simplify(&mut Box::new(Scalar(f32::from_bits(a))),&mut Box::new(Scalar(f32::from_bits(b))),mode,&mut result);
            println!("{:08x}",result.0.to_bits());
        }
    }
}
'''
(HERE / 'helper.rs').write_text(program)
oracle_path = ROOT / 'artifacts/css-round-context-quotient-arithmetic-review-v1/audit.py'
spec = importlib.util.spec_from_file_location('round_exact_oracle', oracle_path)
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
bits = lambda value: struct.unpack('<I', struct.pack('<f', value))[0]
pairs = [(bits(a), bits(b)) for a, b in [(0.65, 0.1), (0.66, 0.1), (-0.65, 0.1), (-0.66, 0.1), (0.65, 0.125), (0.5, 0.25)]]
with tempfile.TemporaryDirectory(prefix='round-parse-extract-') as directory:
    executable = Path(directory) / 'helper'
    build = subprocess.run(['rustc', '--edition=2021', '-C', 'opt-level=2', str(HERE / 'helper.rs'), '-o', str(executable)], capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    output = subprocess.check_output([str(executable)], input=''.join(f'{a:08x} {b:08x}\n' for a,b in pairs), text=True)
values = [int(line,16) for line in output.splitlines()]
rows = []
for i,(a,b) in enumerate(pairs):
    expected = oracle.oracle(a,b)
    for j,mode in enumerate(oracle.MODES):
        rows.append({'a':f'{a:08x}','b':f'{b:08x}','strategy':mode,'simplifier':f'{values[4*i+j]:08x}','exact':f'{expected[j]:08x}','match':values[4*i+j]==expected[j]})
assert not executable.exists()
assert any(not row['match'] for row in rows)
(HERE / 'SCALAR.json').write_text(json.dumps({'rows':rows,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'extracted_sha256':hashlib.sha256(body.encode()).hexdigest(),'compiler':subprocess.check_output(['rustc','--version'],text=True).strip(),
    'temporary_binary_removed':True,'native_typecheck':False,'browser_executed':False},indent=2)+'\n')
print(json.dumps({'checks':len(rows),'mismatches':sum(not r['match'] for r in rows),'rows':rows},indent=2))
