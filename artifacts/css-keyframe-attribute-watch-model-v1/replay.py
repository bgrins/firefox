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
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output.resolve()
    assert not out.exists() and not out.is_symlink()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert sha(ROOT / name) == digest
    for name, digest in inputs['model_pins'].items():
        assert sha(HERE / name) == digest
        assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / name).read_text())
    parent = ROOT / inputs['dependency']
    manifest = json.loads((parent / 'FILES.json').read_text())
    for name, digest in manifest.items():
        assert sha(parent / name) == digest
    assert sha(parent / 'Obligations.lean') == inputs['dependency_source_sha256']
    compiler = ROOT / inputs['compiler']
    assert sha(compiler) == inputs['compiler_sha256']
    negatives = {
        'missing-absent-read': '7 ∈ (change (dropAbsent empty 1 absentEntry) 7 11).pending',
        'equal-value-skipped-publication': '7 ∈ (change (equalSkip one 1 equalEntry) 7 12).pending',
        'shared-watch-removed': '7 ∈ (change (removeTargetWatches shared 1) 7 11).pending',
    }
    out.mkdir()
    records = []
    with tempfile.TemporaryDirectory(prefix='attribute-watch-', dir='/private/tmp') as tmp:
        scratch = Path(tmp)
        env = dict(os.environ, LEAN_PATH=tmp, LEAN_NUM_THREADS='2')
        def run(name, args, success=True):
            result = subprocess.run([str(compiler), *args], cwd=scratch, env=env,
                                    text=True, capture_output=True, timeout=55)
            log = result.stdout + result.stderr
            path = out / (name + '.log')
            path.write_text(log)
            records.append({'name':name,'exit':result.returncode,'log_sha256':sha(path)})
            if success:
                assert result.returncode == 0 and 'warning:' not in log and 'sorryAx' not in log, log
            else:
                assert result.returncode != 0 and 'false' in log and 'decide' in log, log
                assert not any(x in log for x in ['Unknown identifier','unknown identifier','unexpected token','failed to synthesize']), log
            return log
        version = run('version',['--version'])
        shutil.copyfile(parent / 'Obligations.lean', scratch / 'Obligations.lean')
        for name in ('Watches.lean','Witnesses.lean','Audit.lean'):
            shutil.copyfile(HERE / name, scratch / name)
        run('dependency',['-o','Obligations.olean','Obligations.lean'])
        run('watches',['-o','Watches.olean','Watches.lean'])
        run('witnesses',['-o','Witnesses.olean','Witnesses.lean'])
        audit = run('audit',['Audit.lean'])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",line)
            assert match,line
            axioms[match[1]] = match[2].split(', ') if match[2] else []
            assert set(axioms[match[1]]) <= {'propext','Quot.sound','Classical.choice'}
        assert list(axioms) == inputs['audits']
        for name, claim in negatives.items():
            source = 'import Witnesses\nopen AttributeWatches\nexample : ' + claim + ' := by decide +kernel\n'
            (out / (name + '.lean.txt')).write_text(source)
            (scratch / 'FalseClaim.lean').write_text(source)
            run(name,['FalseClaim.lean'],False)
    assert not scratch.exists()
    result = {'status':'ATTRIBUTE_WATCH_MODEL_REPLAY_PASS','compiler':version.strip(),'compiler_sha256':sha(compiler),
              'audits':axioms,'support_declarations':17,'closed_examples':7,'independent_obligations':3,'rejected_false_claims':list(negatives),
              'records':records,'inherited_theorem_credit':0,'native_refinement_proved':False,'new_browser_bug_claim':False,
              'canonical_integration':False,'scratch_build_products_removed':True,'browser_or_native_build':False}
    (out / 'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
