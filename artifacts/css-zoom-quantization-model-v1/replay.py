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


def decisive(code, log):
    return code == 1 and re.fullmatch(
        r"False\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n[\s\S]+\nis false\n?", log
    ) is not None and log.count('error:') == 1 and not any(
        word in log for word in ('warning:', 'failed to reduce', 'Reduction got stuck', 'sorry', 'failed to synthesize'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    assert output.is_absolute() and not output.exists()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    compiler = ROOT / inputs['compiler']
    assert sha(compiler) == inputs['compiler_sha256']
    for name, digest in inputs['sources'].items():
        assert sha(HERE / name) == digest
        assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / name).read_text())
    for name, digest in inputs['imports'].items():
        assert sha(ROOT / name) == digest
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert sha(ROOT / name) == digest
    output.mkdir()
    records = []
    with tempfile.TemporaryDirectory(prefix='zoom-quantization-', dir='/private/tmp') as temporary:
        scratch = Path(temporary)
        for name in inputs['sources']:
            shutil.copyfile(HERE / name, scratch / name)
        env = dict(os.environ, LEAN_PATH=temporary, LEAN_NUM_THREADS='1')
        def run(name, args, negative=False):
            result = subprocess.run([str(compiler), '-j1', *args], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=45)
            log = result.stdout + result.stderr
            (output / (name + '.log')).write_text(log)
            records.append(dict(name=name, command=[str(compiler), '-j1', *args],
                                exit=result.returncode, log_sha256=sha(output / (name + '.log'))))
            assert decisive(result.returncode, log) if negative else (
                result.returncode == 0 and 'warning:' not in log and 'sorryAx' not in log), log
            return log
        version = run('version', ['--version']).strip()
        run('Quantization', ['-o', 'Quantization.olean', 'Quantization.lean'])
        audit = run('audit', ['Audit.lean'])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match, line
            assert match[1] not in axioms
            axioms[match[1]] = match[2].split(', ') if match[2] else []
            assert set(axioms[match[1]]) <= {'propext', 'Quot.sound', 'Classical.choice'}
        assert set(axioms) == set(inputs['audited_names'])
        claims = {'fractional-exact-cancellation': 'crossError tiny (normalize (quantize tiny oneAndHalf) oneAndHalf) = 0', 'quantization-commutes-with-zoom': 'crossError (normalize (quantize tiny one) one) (normalize (quantize tiny oneAndHalf) oneAndHalf) = 0', 'half-zoom-error-below-one-canonical-au': '(crossError tiny (normalize (quantize tiny half) half)).natAbs < 100', 'negative-truncation-is-floor': 'quantize (negate tiny) oneAndHalf = -12', 'integer-zoom-exact-cancellation': 'crossError tiny (normalize (quantize tiny (Zoom.mk ⟨2, by decide⟩ ⟨1, by decide⟩)) (Zoom.mk ⟨2, by decide⟩ ⟨1, by decide⟩)) = 0'}
        for name, claim in claims.items():
            source = 'import Quantization\nopen ZoomQuantization\nexample : ' + claim + ' := by\n  decide +kernel\n'
            (scratch / 'False.lean').write_text(source)
            (output / (name + '.lean')).write_text(source)
            run(name, ['False.lean'], True)
        good = (output / 'fractional-exact-cancellation.log').read_text()
        assert not decisive(0, good)
        assert not decisive(1, good + 'False.lean:1:1: error: unrelated\n')
        assert not decisive(1, 'False.lean:1:1: error: Unknown identifier `false`\n')
    assert not scratch.exists()
    check = dict(status='ZOOM_QUANTIZATION_PASS', compiler=version,
                 axioms=axioms, records=records, owned_scratch_removed=True,
                 rational_zoom=True, signed_lengths=True, truncation_toward_zero=True,
                 floating_point_model=False, native_refinement=False,
                 canonical_coverage_credit=0, accepted_bug_credit=0)
    (output / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check))


if __name__ == '__main__':
    main()
