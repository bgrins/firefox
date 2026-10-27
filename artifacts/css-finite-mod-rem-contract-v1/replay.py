import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert not out.exists() and not out.is_symlink()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    for n, h in inputs['pins'].items():
        assert sha(ROOT / n) == h, n
    for n, h in inputs['model_pins'].items():
        assert sha(HERE / n) == h, n
    for n, h in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        p = ROOT / n
        assert sha(p) == h, n
        if p.name == 'FILES.json':
            for member, expected in json.loads(p.read_text()).items():
                assert not Path(member).is_absolute() and '..' not in Path(member).parts
                assert sha(p.parent / member) == expected, member
    for n in ('Contract.lean', 'Examples.lean'):
        assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / n).read_text())
    out.mkdir()
    records = []
    compiler = ROOT / inputs['compiler']
    negatives = {'skip_opposite_sign_adjustment': 'example : adjust ((-17 : Int).tmod 3) 3 = -2 := by decide +kernel\n', 'add_divisor_to_zero': 'example : candidateGrid .mod (fun x => x) 0 3 = 3 := by decide +kernel\n', 'mod_uses_dividend_zero_sign': 'example : candidate .mod (fun x => x) true false 0 3 = .zero true := by decide +kernel\n', 'rem_uses_divisor_zero_sign': 'example : candidate .rem (fun x => x) true false 0 3 = .zero false := by decide +kernel\n', 'strict_projected_interval': 'example : (33554432 : Int) < 33554432 := by decide +kernel\n', 'missing_remainder_correspondence': 'example : candidateGrid .rem (fun x => x) 0 3 = (33554432 : Int).tmod 3 := by decide +kernel\n'}
    with tempfile.TemporaryDirectory(prefix='finite-mod-rem-contract-', dir='/private/tmp') as tmp:
        scratch = Path(tmp)
        env = dict(os.environ, LEAN_NUM_THREADS='2', LEAN_PATH=tmp)
        def run(name, args, success=True):
            result = subprocess.run([str(compiler), *args], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=55)
            text = result.stdout + result.stderr
            log = out / (name + '.log'); log.write_text(text)
            records.append({'name': name, 'exit': result.returncode, 'log_sha256': sha(log)})
            if success:
                assert result.returncode == 0 and 'sorryAx' not in text, text
                warnings = [line for line in text.splitlines() if 'warning:' in line]
                if warnings:
                    assert name == 'inherited-Dispatch' and all(re.fullmatch(r'Dispatch\.lean:\d+:\d+: warning: This simp argument is unused:', line) for line in warnings), text
            else:
                assert result.returncode != 0 and 'false' in text and 'decide' in text, text
                assert not any(t in text for t in ('Unknown identifier', 'unknown identifier', 'unexpected token', 'failed to synthesize')), text
            return text
        version = run('version', ['--version'])
        for module, path in inputs['imports'].items():
            shutil.copyfile(ROOT / path, scratch / (module + '.lean'))
            run('inherited-' + module, ['-o', module + '.olean', module + '.lean'])
        shutil.copyfile(HERE / 'Contract.lean', scratch / 'Contract.lean')
        shutil.copyfile(HERE / 'Examples.lean', scratch / 'Examples.lean')
        audit = run('contract', ['-o', 'Contract.olean', 'Contract.lean'])
        found = []
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match, line
            found.append(match[1])
            assert not match[2] or set(match[2].split(', ')) <= {'propext', 'Quot.sound', 'Classical.choice'}, line
        assert found == inputs['audits']
        run('examples', ['Examples.lean'])
        for name, body in negatives.items():
            source = 'import Contract\nopen FiniteModRemContract ModRemInfinity\n' + body
            (out / (name + '.lean.txt')).write_text(source)
            (scratch / 'FalseClaim.lean').write_text(source)
            run(name, ['FalseClaim.lean'], False)
    assert not scratch.exists()
    result = {'status': 'FINITE_MOD_REM_REPLACEMENT_CONTRACT_PASS', 'compiler': version.strip(),
              'compiler_sha256': sha(compiler), 'audits': inputs['audits'], 'audit_count': len(inputs['audits']),
              'core_results': ['truncating remainder sign adjustment satisfies exact Mod relation',
                               'candidate finite backend contract under explicit remainder and nearest-addition correspondence',
                               'nearest projection preserves closed interval and operation-specific zero signs',
                               'representable divisor endpoint is a valid nearest projection counterexample to strict bounds'],
              'inherited_capacity_new_theorem_credit': 0, 'positive_examples': 8,
              'negative_controls': list(negatives), 'records': records,
              'projection_quantifies_over_all_signed_encodings': True,
              'compiler_products_removed': True, 'canonical_integration': False,
              'inherited_dispatch_unused_simp_warnings': (out / 'inherited-Dispatch.log').read_text().count('warning:'),
              'new_model_warnings': 0,
              'native_remainder_correspondence_proved': False,
              'native_addition_RN_correspondence_proved': False,
              'browser_executed': False}
    (out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
