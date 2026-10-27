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
    output.mkdir()
    records = []
    with tempfile.TemporaryDirectory(prefix='quote-delivery-', dir='/private/tmp') as temporary:
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
        run('model', ['-o', 'QuoteAppend.olean', 'QuoteAppend.lean'])
        audit = run('audit', ['Audit.lean'])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match, line
            axioms[match[1]] = match[2].split(', ') if match[2] else []
            assert set(axioms[match[1]]) <= {'propext', 'Quot.sound', 'Classical.choice'}
        claims = {
            'old-shortcut-fresh': '(deliver explicitPairs (legacyAppend explicitPairs initial .noOpen)).childCache = childReference explicitPairs (legacyAppend explicitPairs initial .noOpen)',
            'dirty-alone-fresh': '(append explicitPairs initial .noOpen).childCache = childReference explicitPairs (append explicitPairs initial .noOpen)',
            'lost-demand-fresh': '(deliver explicitPairs { append explicitPairs initial .noOpen with dirty := false }).childCache = [⟨1, "AAA"⟩, ⟨2, "AAA"⟩]',
        }
        for name, claim in claims.items():
            text = 'import QuoteAppend\nopen QuoteAppend\nexample : ' + claim + ' := by decide +kernel\n'
            (scratch / 'False.lean').write_text(text)
            (output / (name + '.lean')).write_text(text)
            run(name, ['False.lean'], True)
        valid = (output / 'old-shortcut-fresh.log').read_text()
        assert not decisive(0, valid)
        assert not decisive(1, valid + 'False.lean:1:1: error: unrelated\n')
        assert not decisive(1, 'False.lean:1:1: error: Tactic `decide` failed to reduce\n')
    assert not scratch.exists()
    check = dict(status='QUOTE_APPEND_DELIVERY_MODEL_PASS', compiler=version, threads=1,
                 named_declarations=len(axioms), closed_examples=5, decisive_false_controls=3,
                 diagnostic_gate_negatives=3, axioms=axioms, records=records,
                 owned_scratch_removed=True, native_extraction=False, canonical_integration=False,
                 scope='Fixed child-after-parent boundary; finite append/flush histories; delivery and stable provider premises')
    (output / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check))


if __name__ == '__main__':
    main()
