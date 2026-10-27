from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import argparse
import hashlib
import json
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


@lru_cache(None)
def exact(bits):
    sign = -1 if bits >> 31 else 1
    exponent, fraction = (bits >> 23) & 255, bits & 0x7fffff
    assert exponent != 255
    return sign * Fraction(fraction if exponent == 0 else fraction + (1 << 23)) * Fraction(2) ** (-149 if exponent == 0 else exponent - 150)


def nan(bits):
    return bits & 0x7fffffff > 0x7f800000


def infinite(bits):
    return bits & 0x7fffffff == 0x7f800000


def round_bits(value, zero_sign):
    if not value:
        return zero_sign << 31
    negative = value < 0
    value = abs(value)
    lo, hi = 0, 0x7f7fffff
    assert value <= exact(hi)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if exact(mid) <= value:
            lo = mid
        else:
            hi = mid - 1
    if exact(lo) != value:
        upper = lo + 1
        lower_distance, upper_distance = value - exact(lo), exact(upper) - value
        if upper_distance < lower_distance or upper_distance == lower_distance and upper % 2 == 0:
            lo = upper
    return lo | (int(negative) << 31)


def oracle(op, a, b):
    if nan(a) or nan(b) or infinite(a) or b & 0x7fffffff == 0:
        return None, None
    if infinite(b):
        return (None, None) if op == 'mod' and a >> 31 != b >> 31 else (a, None)
    aa, bb = exact(a), exact(b)
    quotient = aa / bb
    q = quotient.numerator // quotient.denominator if op == 'mod' else int(quotient)
    r = aa - q * bb
    return round_bits(r, b >> 31 if op == 'mod' else a >> 31), r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    for name, digest in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / name) == digest
    source_path = 'servo/components/style/values/generics/calc.rs'
    landing = 'testing/web-platform/tests/css/css-values/mod-rem-exact-finite-remainder.html'
    original = (HERE/'original-apply.rs').read_text()
    candidate = (HERE/'candidate-apply.rs').read_text()
    helper = (HERE/'helper.rs').read_text()
    for body in [original,candidate]:
        assert body.replace('    fn apply(', '    pub fn apply(') in helper
    rows = []
    nan_payload_differences = 0
    compiler = subprocess.run(['rustc','--version'],check=True,capture_output=True,text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='modrem-repair-') as tmp:
        scratch = Path(tmp)
        exe = scratch/'helper'
        for opt in [0,2]:
            command = ['rustc','--edition=2024','-C',f'opt-level={opt}','-C','overflow-checks=yes',str(HERE/'helper.rs'),'-o',str(exe)]
            result = subprocess.run(command,capture_output=True,text=True)
            (out/f'compile-{opt}.log').write_text(result.stdout+result.stderr)
            assert result.returncode == 0
            run = subprocess.run([str(exe)],check=True,capture_output=True,text=True)
            (out/f'run-{opt}.log').write_text(run.stdout)
            current = []
            for line in run.stdout.splitlines():
                op, aa, bb, oo, nn = line.split()
                a,b,old,new = [int(v,16) for v in [aa,bb,oo,nn]]
                expected, exact_result = oracle(op,a,b)
                assert nan(new) if expected is None else new == expected, (op,aa,bb,oo,nn,expected)
                old_ok = nan(old) if expected is None else old == expected
                special = nan(a) or nan(b) or infinite(a) or infinite(b) or not (a&0x7fffffff) or not (b&0x7fffffff)
                if special:
                    assert old_ok, ('special changed',op,aa,bb,oo,nn)
                endpoint = exact_result is not None and exact_result != 0 and new == b
                current.append(dict(op=op,a=aa,b=bb,old=oo,candidate=nn,expected=None if expected is None else f'{expected:08x}',
                                    old_matches=old_ok,special=special,rounded_to_divisor=endpoint))
            assert len(current) == len(read(HERE/'INPUT-BITS.json'))**2*2
            if rows:
                for previous, now in zip(rows, current):
                    for field in previous:
                        if previous[field] != now[field]:
                            assert field in ('old', 'candidate') and nan(int(previous[field],16)) and nan(int(now[field],16))
                            nan_payload_differences += 1
            rows=current
            exe.unlink()
        for role in ['head90','installed']:
            repo=scratch/role;repo.mkdir()
            subprocess.run(['git','init','-q',str(repo)],check=True,capture_output=True)
            path=repo/source_path;path.parent.mkdir(parents=True);path.write_bytes((HERE/role/'original'/source_path).read_bytes())
            assert path.read_text().count(original)==1
            assert (HERE/role/'candidate'/source_path).read_text()==path.read_text().replace(original,candidate)
            patch=HERE/f'{role}.patch'
            subprocess.run(['git','apply','--check',str(patch)],cwd=repo,check=True,capture_output=True)
            subprocess.run(['git','apply',str(patch)],cwd=repo,check=True,capture_output=True)
            for name in [source_path,landing]:
                assert (repo/name).read_bytes()==(HERE/role/'candidate'/name).read_bytes()
            subprocess.run(['git','apply','--reverse',str(patch)],cwd=repo,check=True,capture_output=True)
            assert path.read_bytes()==(HERE/role/'original'/source_path).read_bytes() and not (repo/landing).exists()
    targets=[r for r in rows if int(r['a'],16)&0x7fffffff==0x4c000000 and int(r['b'],16)&0x7fffffff==0x40400000]
    assert len(targets)==8 and all(not r['old_matches'] for r in targets)
    endpoints=[r for r in rows if r['rounded_to_divisor']]
    assert endpoints
    (out/'ROWS.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'ENDPOINTS.json').write_text(json.dumps(endpoints,indent=2)+'\n')
    result=dict(status='EXTRACTED_MOD_REM_CANDIDATE_MATCHES_BOUNDED_EXACT_ORACLE',compiler=compiler,
        optimizations=[0,2],rows_per_optimization=len(rows),target_repairs=len(targets),
        old_disagreements=sum(not r['old_matches'] for r in rows),special_rows_preserved=sum(r['special'] for r in rows),
        rounded_divisor_endpoints=len(endpoints),nan_payload_differences_between_optimizations=nan_payload_differences,git_roles=['head90','installed'],
        scratch_removed=not Path(tmp).exists(),browser=False,gecko_compilation=False,all_finite_proof=False)
    (out/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
