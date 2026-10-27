#!/usr/bin/env python3
import argparse, hashlib, json, os, re, shutil, struct, subprocess, tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUST = '/Users/bgrins/.cargo/bin/rustc'
LEAN = Path('/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')

def body(source, marker):
    start = source.index(marker)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

def run(cmd, **kwargs):
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for name, pin in pins.items():
        assert hashlib.sha256((HERE/'sources'/name).read_bytes()).hexdigest() == pin['sha256']
    sources = {name: (HERE/'sources'/name).read_text() for name in pins}
    normalize = body(sources['values.rs'], 'pub fn normalize(').replace('CSSFloat', 'f32')
    assert body(sources['number-head90.rs'], 'pub fn get(&self) -> f32') == body(sources['number-118.rs'], 'pub fn get(&self) -> f32')
    get = body(sources['number-118.rs'], 'pub fn get(&self) -> f32').replace('crate::values::normalize', 'normalize')
    clamp = body(sources['numeric-policy.rs'], 'pub fn clamp(&self, val: f32)')
    calc = sources['calc.rs']
    assert 'self.clamping_mode.clamp(leaf_to_f32(result))' in calc
    assert 'Ok(Leaf::Number(n)) => n.get(),' in sources['number-118.rs']
    extracts = {'normalize': normalize, 'get': get, 'clamp': clamp, 'rounding': {}}
    functions = []
    for role in ['head90', '118']:
        source = sources['number-'+role+'.rs']
        resolve = body(source, 'pub fn resolve(&self) -> Option<CSSInteger>')
        computed = body(source, 'impl ToComputedValue for Integer')
        rounding = re.search(r'\((?:f64::from\(value\)|value) \+ 0\.5\)\.floor\(\) as CSSInteger', resolve).group()
        computed_rounding = re.search(r'\((?:f64::from\(clamped\)|clamped) \+ 0\.5\)\.floor\(\) as i32', computed).group()
        assert 'let clamped = crate::values::normalize(value).min(f32::MAX).max(f32::MIN);' in computed
        extracts['rounding'][role] = {'resolve': resolve, 'computed': computed}
        functions.append(f'fn round_{role}(value:f32)->i32 {{ {rounding.replace("CSSInteger","i32")} }}')
        functions.append(f'fn context_{role}(raw:f32, mode:Mode)->i32 {{ let value=mode.clamp(Number(raw).get()); let clamped=normalize(value).min(f32::MAX).max(f32::MIN); {computed_rounding} }}')
    bitset = {0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x807fffff, 0x00800000,
              0x80800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
              0x7fc00000, 0xffc00000, 0x7fa00001}
    for value in [-2147483648., -8388609., -10., -2.5, -1.5, -1., -.5, .49, .5, 1., 1.49, 1.5, 2.5, 8388609., 2147483648.]:
        bits = struct.unpack('>I', struct.pack('>f', value))[0]
        bitset.update([bits-1, bits, bits+1])
    bits = sorted(bitset)
    helper = '#![allow(dead_code)]\n' + normalize + '\nstruct Number(f32);\nimpl Number {' + get + '}\n'
    helper += '#[derive(Clone,Copy,Debug)] enum Mode { All, NonNegative, AtLeastOne, ZeroToOne }\nimpl Mode {'+clamp+'}\n'
    helper += '\n'.join(functions)
    helper += '\nfn main(){ for bits in ['+','.join(str(b)+'u32' for b in bits)+'] { let raw=f32::from_bits(bits); for mode in [Mode::All,Mode::NonNegative,Mode::AtLeastOne,Mode::ZeroToOne] { let got=Number(raw).get(); let clamped=mode.clamp(got);'
    for role in ['head90','118']:
        helper += f'println!("{role} {{bits:08x}} {{mode:?}} {{}} {{}} {{}}",round_{role}(got),round_{role}(clamped),context_{role}(raw,mode));'
    helper += '}}}\n'
    (out/'helper.rs').write_text(helper)
    (out/'EXTRACTION.json').write_text(json.dumps(extracts,indent=2)+'\n')
    logs=[]
    with tempfile.TemporaryDirectory(prefix='integer-range-') as temp:
        temp=Path(temp)
        for opt in [0,2]:
            exe=temp/('helper'+str(opt))
            compile_log=run([RUST,'--edition=2021','-C','overflow-checks=yes','-C','opt-level='+str(opt),str(out/'helper.rs'),'-o',str(exe)])
            (out/('compile-'+str(opt)+'.log')).write_text(compile_log)
            log=run([str(exe)]);logs.append(log);(out/('helper-'+str(opt)+'.log')).write_text(log)
        assert logs[0]==logs[1]
        model = HERE/'RangePolicy.lean'
        dep=HERE/'sources'/'CssIntegerRounding.lean'
        (temp/'CssSemantics').mkdir();shutil.copyfile(dep,temp/'CssSemantics'/'CssIntegerRounding.lean')
        env={**os.environ,'LEAN_PATH':str(temp),'LEAN_NUM_THREADS':'2'}
        run([str(LEAN),'-o',str(temp/'CssSemantics'/'CssIntegerRounding.olean'),'CssSemantics/CssIntegerRounding.lean'],env=env,cwd=temp)
        shutil.copyfile(model,temp/'RangePolicy.lean')
        leanlog=run([str(LEAN),'RangePolicy.lean'],env=env,cwd=temp);(out/'lean.log').write_text(leanlog)
    counts={'head90':{'old_context_differences':0,'candidate_context_differences':0,'candidate_exact_oracle_differences':0},'118':{'old_context_differences':0,'candidate_context_differences':0,'candidate_exact_oracle_differences':0}}
    for line in logs[0].splitlines():
        role,hexadecimal,mode,old,new,context=line.split();old,new,context=map(int,[old,new,context])
        b=int(hexadecimal,16);exp=(b>>23)&255;fraction=b&0x7fffff;negative=bool(b>>31)
        if exp==255:
            q=Fraction(0) if fraction else Fraction((2**24-1)*2**104)*(-1 if negative else 1)
        else:
            q=Fraction(fraction if exp==0 else fraction+2**23)*Fraction(2)**(-149 if exp==0 else exp-150)*(-1 if negative else 1)
        if mode!='All':q=max(q,Fraction(1 if mode=='AtLeastOne' else 0))
        if mode=='ZeroToOne':q=min(q,Fraction(1))
        exact=max(-2**31,min(2**31-1,(q+Fraction(1,2)).numerator//(q+Fraction(1,2)).denominator))
        counts[role]['old_context_differences']+=old!=context
        counts[role]['candidate_context_differences']+=new!=context
        counts[role]['candidate_exact_oracle_differences']+=new!=exact
        assert new==context
        if role=='118':assert new==exact
    summary={'status':'PASS','raw_inputs':len(bits),'rows_per_optimization':len(logs[0].splitlines()),'optimizations':[0,2],'counts':counts,'temporary_products_removed':True,'rust_version':run([RUST,'--version']).strip(),'lean_version':run([str(LEAN),'--version']).strip()}
    (out/'CHECK.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
