import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    for name, digest in inputs['files'].items():
        assert sha(ROOT / name) == digest, name
    lean = ROOT / inputs['lean']
    assert sha(lean) == inputs['lean_sha256']
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        path = ROOT / name
        assert sha(path) == digest
        for member, value in json.loads(path.read_text()).items():
            assert not Path(member).is_absolute() and '..' not in Path(member).parts
            assert sha(path.parent / member) == value
    negatives = {
        'stale-rising-count': 'withStaleCache 3 4 = rendered 3',
        'stale-falling-count': 'withStaleCache 1 5 = rendered 1',
        'specified-placeholder-consumed': 'withStaleCache 2 0 = rendered 2',
        'unnamed-group-ignored': 'stored 4294967295 ([.ordinary (0 : Nat)] : List (Piece Nat)) = 0',
        'inverse-keeps-zero-cache': '(rebuild 4294967295 id (specify (computedEntries (fun _ => 3) supplied))).2 = 0',
    }
    exits = {}
    with tempfile.TemporaryDirectory(prefix='name-repeat-cache-') as directory:
        scratch = Path(directory)
        for source in inputs['modules']:
            path = ROOT / source
            (scratch / path.name).write_bytes(path.read_bytes())
        env = {**os.environ, 'LEAN_PATH': str(scratch), 'LEAN_NUM_THREADS': '2'}
        for name, count in [('CountTransport', 5), ('GuardedConsumer', 1), ('LinePrefix', 3),
                            ('SequencePrefix', 2), ('WholeAutofill', 8), ('ComputedCache', 0)]:
            run = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'], cwd=scratch,
                                 env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=60)
            (out / (name + '.log')).write_text(run.stdout)
            assert run.returncode == 0, run.stdout
            assert len(run.stdout.splitlines()) == count and 'sorryAx' not in run.stdout
            assert all(line.endswith(('depends on axioms: [propext, Quot.sound]',
                                      'depends on axioms: [propext, Classical.choice, Quot.sound]'))
                       for line in run.stdout.splitlines())
            exits[name] = run.returncode
        for name, claim in negatives.items():
            text = ('import ComputedCache\nopen NameRepeatComputedCache SubgridSequencePrefix\n'
                    'example : ' + claim + ' := by decide +kernel\n')
            (scratch / 'False.lean').write_text(text)
            (out / (name + '.lean.txt')).write_text(text)
            run = subprocess.run([str(lean), 'False.lean'], cwd=scratch, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=60)
            (out / (name + '.log')).write_text(run.stdout)
            assert run.returncode != 0 and 'Tactic `decide` proved that the proposition' in run.stdout and 'is false' in run.stdout, run.stdout
            assert 'unknown' not in run.stdout.lower() and 'unexpected token' not in run.stdout
            exits[name] = run.returncode
    result = {'status': 'SUPPLIED_COMPUTED_CACHE_REUSE_PASS', 'exits': exits,
              'prior_general_results_rebuilt': 19, 'new_theorem_credit': 0,
              'generic_adapter_checks': 5, 'closed_positive_checks': 9,
              'false_claims_rejected': 5, 'canonical_edits': False,
              'context_provider_refinement': False, 'native_refinement': False,
              'native_build_browser_index_actions': False, 'temporary_compiler_products_removed': True}
    (out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
