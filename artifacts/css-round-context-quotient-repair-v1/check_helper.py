import sys
sys.dont_write_bytecode = True
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import random
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-round-context-quotient-audit-v1/source/servo/components/style/values/generics/calc.rs'
CANDIDATE = HERE / 'candidate/servo/components/style/values/generics/calc.rs'


def extract(path):
    source = path.read_text()
    start = source.index('                let step = step.abs();', source.index('            Self::Round {', source.index('fn resolve_internal')))
    end = source.index('                Ok((value, ty))', start) + len('                Ok((value, ty))')
    return source[start:end]


def rational(bits):
    sign = -1 if bits >> 31 else 1
    exp, frac = (bits >> 23) & 255, bits & 0x7fffff
    if exp == 255:
        return None
    return sign * Fraction(frac if exp == 0 else (1 << 23) + frac) * Fraction(2) ** ((-126 if exp == 0 else exp - 127) - 23)


def rounded_bits(x, negative_zero=False):
    if x == 0:
        return 0x80000000 if negative_zero else 0
    sign = 0x80000000 if x < 0 else 0
    x = abs(x)
    maximum = rational(0x7f7fffff)
    if x >= maximum + Fraction(2) ** 103:
        return sign | 0x7f800000
    if x >= maximum:
        return sign | 0x7f7fffff
    lo, hi = 0, 0x7f7fffff
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if rational(mid) <= x:
            lo = mid
        else:
            hi = mid
    dl, dh = x - rational(lo), rational(hi) - x
    return sign | (lo if dl < dh or (dl == dh and lo % 2 == 0) else hi)


def oracle(a, b, mode):
    value, step = rational(a), rational(b)
    if value is None or step is None or step == 0:
        return None
    step = abs(step)
    quotient = value / step
    lower = (quotient.numerator // quotient.denominator) * step
    if value == lower:
        return a
    upper = lower + step
    result = {'Down': lower, 'Up': upper, 'ToZero': lower if value > 0 else upper,
              'Nearest': lower if value - lower < upper - value else upper}[mode]
    return rounded_bits(result, result == 0 and value < 0)


old, new = extract(SOURCE), extract(CANDIDATE)
header = '''#[derive(Clone, Copy)]
enum RoundingStrategy { Nearest, Up, Down, ToZero }
trait Zero { fn is_zero(self) -> bool; }
impl Zero for f32 { fn is_zero(self) -> bool { self == 0.0 } }
'''
program = header
for name, body in [('old', old), ('candidate', new)]:
    program += f'fn {name}(mut value: f32, step: f32, strategy: RoundingStrategy) -> Result<(f32, ()), ()> {{\nlet ty = ();\n{body}\n}}\n'
program += '''fn main() {
    use std::io::{self, Read};
    let mut input = String::new(); io::stdin().read_to_string(&mut input).unwrap();
    for line in input.lines() {
        let words: Vec<&str> = line.split_whitespace().collect();
        let a = u32::from_str_radix(words[0],16).unwrap(); let b = u32::from_str_radix(words[1],16).unwrap();
        for strategy in [RoundingStrategy::Nearest, RoundingStrategy::Up, RoundingStrategy::Down, RoundingStrategy::ToZero] {
            println!("{:08x} {:08x}",old(f32::from_bits(a),f32::from_bits(b),strategy).unwrap().0.to_bits(),candidate(f32::from_bits(a),f32::from_bits(b),strategy).unwrap().0.to_bits());
        }
    }
}
'''
(HERE / 'helper.rs').write_text(program)
values = [0,0x80000000,1,0x80000001,0x3e800000,0xbe800000,0x3f000000,0xbf000000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00000]
steps = [0,0x80000000,1,0x80000001,0x3eaaaaab,0xbeaaaaab,0x3e800000,0xbe800000,0x3f800000,0x40000000,0x7f7fffff,0x7f800000,0xff800000,0x7fc00000]
pairs = [(a,b) for a in values for b in steps]
rng = random.Random(14818)
pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(256)]
text = ''.join(f'{a:08x} {b:08x}\n' for a,b in pairs)
with tempfile.TemporaryDirectory(prefix='round-context-helper-') as temporary:
    executable = Path(temporary) / 'helper'
    command = ['rustc','--edition=2021','-C','opt-level=0','-C','overflow-checks=yes',str(HERE/'helper.rs'),'-o',str(executable)]
    build = subprocess.run(command,capture_output=True,text=True)
    if build.returncode: raise RuntimeError(build.stderr)
    execution = subprocess.run([str(executable)],input=text,capture_output=True,text=True,check=True)
    outputs = [tuple(int(s,16) for s in line.split()) for line in execution.stdout.splitlines()]
assert len(outputs) == len(pairs)*4
modes = ['Nearest','Up','Down','ToZero']; rows=[]; differences=[]; exact_old=exact_new=0; specials=0
for pair_index,(a,b) in enumerate(pairs):
    for mode_index,mode in enumerate(modes):
        old_bits,new_bits=outputs[pair_index*4+mode_index]
        expected=oracle(a,b,mode)
        row={'a':f'{a:08x}','b':f'{b:08x}','mode':mode,'old':f'{old_bits:08x}','candidate':f'{new_bits:08x}','exact_oracle':None if expected is None else f'{expected:08x}'}
        rows.append(row)
        if expected is not None:
            exact_old += old_bits != expected; exact_new += new_bits != expected
            if new_bits != expected: differences.append(row)
        elif rational(a) is None or rational(b) is None or rational(b)==0:
            assert old_bits == new_bits or (rational(old_bits) is None and rational(new_bits) is None and old_bits&0x7fffff and new_bits&0x7fffff)
            specials += 1
for sign in (0,0x80000000):
    for mode in modes:
        row=next(r for r in rows if r['a']==f'{sign:08x}' and r['b']=='3f800000' and r['mode']==mode)
        assert row['candidate']==f'{sign:08x}'
for mode in ('Nearest','Up','ToZero'):
    row=next(r for r in rows if r['a']=='be800000' and r['b']=='3f800000' and r['mode']==mode)
    assert row['candidate']=='80000000'
for a,mode,wanted in [('3f800000','Down','3f2aaaab'),('3f800000','ToZero','3f2aaaab'),('bf800000','Up','bf2aaaab'),('bf800000','ToZero','bf2aaaab')]:
    row=next(r for r in rows if r['a']==a and r['b']=='3eaaaaab' and r['mode']==mode)
    assert row['candidate']==wanted and row['candidate']==row['exact_oracle'] and row['old']!=row['exact_oracle']
(HERE/'HELPER-ROWS.json').write_text(json.dumps(rows,indent=2)+'\n')
receipt={'compiler':subprocess.run(['rustc','--version'],capture_output=True,text=True,check=True).stdout.strip(),'build_exit':build.returncode,'execution_exit':execution.returncode,'pairs':len(pairs),'checks':len(rows),'unchanged_special_checks':specials,'old_exact_oracle_differences':exact_old,'candidate_exact_oracle_differences':exact_new,'candidate_differences':differences,'old_extracted_sha256':hashlib.sha256(old.encode()).hexdigest(),'candidate_extracted_sha256':hashlib.sha256(new.encode()).hexdigest(),'adapter':'exact scalar branch after type checking; unit type tag; is_zero equals IEEE numeric zero; no typed CalcNode pipeline','temporary_products_removed':not executable.exists(),'universal_IEEE_proof':False}
(HERE/'HELPER.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='candidate_differences'},indent=2))
