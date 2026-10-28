import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    out.mkdir(exist_ok=False)
    source = (HERE / 'helper.rs').read_text()
    assert (HERE / 'runtime-round-body.rs').read_text() in source
    native = 'artifacts/css-round-baseline-surprises-audit-v1/source/servo/components/style/values/generics/calc.rs'
    body = (HERE.parents[1] / native).read_bytes()
    assert hashlib.sha256(body).hexdigest() == json.loads((HERE / 'REFERENCES.json').read_text())[native]
    text = body.decode()
    start = text.index('Self::Round {', text.index('fn resolve_internal'))
    branch = text[start:text.index('Self::ModRem {', start)]
    assert branch[branch.index('let step = step.abs();'):branch.index('Ok((value, ty))')] == (HERE / 'runtime-round-body.rs').read_text()
    bits = [0xff800000, 0xbf800000, 0x80000000, 0, 0x3f800000, 0x7f800000, 0x7fc00000]

    def oracle(strategy, a, b):
        if a == 6 or b == 6 or b in (2, 3) or a in (0, 5) and b in (0, 5):
            return 'nan'
        if a in (0, 5):
            return bits[a]
        if b in (0, 5):
            if strategy in (0, 3):
                return 0x80000000 if a in (1, 2) else 0
            if strategy == 1:
                return 0x7f800000 if a == 4 else 0 if a == 3 else 0x80000000
            return 0xff800000 if a == 1 else 0x80000000 if a == 2 else 0
        return bits[a]

    receipts = []
    compiler = '/Users/bgrins/.cargo/bin/rustc'
    version = subprocess.check_output([compiler, '--version', '--verbose'], text=True)
    for variant in ('original', 'nan_first'):
        candidate = source if variant == 'original' else source.replace(
            'let step = step.abs();', 'if value.is_nan() || step.is_nan() { return f32::NAN; }\nlet step = step.abs();', 1)
        for opt in (0, 2):
            with tempfile.TemporaryDirectory(prefix='round-special-helper-') as tmp:
                path = Path(tmp)
                (path / 'helper.rs').write_text(candidate)
                build = subprocess.run([compiler, '--edition=2021', '-C', 'opt-level=' + str(opt),
                                        str(path / 'helper.rs'), '-o', str(path / 'helper')], capture_output=True, text=True)
                assert build.returncode == 0, build.stderr
                run = subprocess.run([str(path / 'helper')], capture_output=True, text=True)
                assert run.returncode == 0 and run.stderr == ''
            (out / f'{variant}-O{opt}.txt').write_text(run.stdout)
            rows = [line.split() for line in run.stdout.splitlines()]
            assert len(rows) == 196 and len({tuple(row[:3]) for row in rows}) == 196
            wrong = []
            for s, a, b, text in rows:
                s, a, b, value = int(s), int(a), int(b), int(text, 16)
                expected = oracle(s, a, b)
                nan = value & 0x7f800000 == 0x7f800000 and value & 0x007fffff != 0
                if not (nan if expected == 'nan' else value == expected):
                    wrong.append({'strategy': s, 'value_class': a, 'step_class': b,
                                  'observed_bits': text, 'expected': expected})
            assert len(wrong) == (16 if variant == 'original' else 0)
            receipts.append({'variant': variant, 'optimization': opt, 'rows': 196, 'mismatches': wrong})
    for variant in ('original', 'nan_first'):
        assert (out / f'{variant}-O0.txt').read_bytes() == (out / f'{variant}-O2.txt').read_bytes()
    (out / 'CHECK.json').write_text(json.dumps({'compiler': version, 'receipts': receipts,
        'source_helper_only': True, 'universal_IEEE_or_native_refinement': False,
        'owned_executables_removed': True}, indent=2) + '\n')
    print('196 cases x 2 optimization levels x 2 variants; original 16 NaN mismatches, nan-first 0.')


if __name__ == '__main__':
    main()
