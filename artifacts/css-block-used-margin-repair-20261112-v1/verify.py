import collections
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    inputs = read('INPUTS.json')
    for name, pins in inputs.items():
        assert sha(ROOT / name) == pins['candidate']
        assert sha(HERE / 'candidate' / name) == pins['candidate']
        if 'original' in pins:
            assert sha(HERE / 'original' / name) == pins['original']
    phases = {}
    for phase, exit_code in [('baseline', 1), ('build', 0), ('fixed', 0)]:
        commands = read(phase + '/COMMANDS.json')
        assert len(commands) == 1
        command = commands[0]
        assert command['exit'] == exit_code and 'timeout' not in command
        assert command['label'] == phase
        try:
            os.killpg(command['pgid'], 0)
        except ProcessLookupError:
            pass
        else:
            raise RuntimeError('Owned command group is still present')
        phases[phase] = dict(exit=exit_code, group_absent_now=True,
                            original_wrapper_error=command.get('final_inspection_error'),
                            log_sha256=sha(HERE / phase / (phase + '.log')))
    baseline = read('baseline/wptreport.json')['results']
    fixed = read('fixed/wptreport.json')['results']
    test = '/css/cssom/resolved-margins-overconstrained-block.html'
    assert len(baseline) == 1 and baseline[0]['test'] == test
    assert baseline[0]['status'] == 'OK'
    assert collections.Counter(t['status'] for t in baseline[0]['subtests']) == {'PASS': 30, 'FAIL': 66}
    assert {r['test'] for r in fixed} == {test, '/css/cssom/computed-style-005.html',
                                       '/css/cssom-view/cssom-getBoxQuads-001.html'}
    assert all(r['status'] == 'OK' for r in fixed)
    assert all(t['status'] == 'PASS' for r in fixed for t in r['subtests'])
    new_fixed = next(r for r in fixed if r['test'] == test)
    assert len(new_fixed['subtests']) == 96
    assert [t['name'] for t in new_fixed['subtests']] == [t['name'] for t in baseline[0]['subtests']]
    assert len({t['name'] for t in new_fixed['subtests']}) == 96
    assert sum(len(r['subtests']) for r in fixed) == 106
    before = read('baseline/before-BINARIES.json')
    assert before == read('baseline/after-BINARIES.json') == read('build/before-BINARIES.json')
    after = read('build/after-BINARIES.json')
    assert after == read('fixed/before-BINARIES.json') == read('fixed/after-BINARIES.json')
    assert before != after
    for name, pin in after.items():
        assert sha(name) == pin['sha256'] and Path(name).stat().st_size == pin['bytes']
    patch_commands = []
    scratch = Path(tempfile.mkdtemp(prefix='css-used-margin-patch-', dir='/private/tmp'))
    try:
        for name, pins in inputs.items():
            if 'original' in pins:
                dest = scratch / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / 'original' / name, dest)
        for flags in [('--check',), ()]:
            argv = ['git', 'apply', *flags, str(HERE / 'candidate.patch')]
            result = subprocess.run(argv, cwd=scratch, capture_output=True, text=True)
            patch_commands.append(dict(argv=argv, exit=result.returncode,
                                       stdout=result.stdout, stderr=result.stderr))
            assert result.returncode == 0
        for name, pins in inputs.items():
            assert sha(scratch / name) == pins['candidate']
        for flags in [('--reverse', '--check'), ('--reverse',)]:
            argv = ['git', 'apply', *flags, str(HERE / 'candidate.patch')]
            result = subprocess.run(argv, cwd=scratch, capture_output=True, text=True)
            patch_commands.append(dict(argv=argv, exit=result.returncode,
                                       stdout=result.stdout, stderr=result.stderr))
            assert result.returncode == 0
        for name, pins in inputs.items():
            assert (sha(scratch / name) == pins['original'] if 'original' in pins
                    else not (scratch / name).exists())
    finally:
        shutil.rmtree(scratch)
    receipt = dict(status='native repair validated locally', phases=phases,
                   baseline_pass=30, baseline_fail=66, fixed_pass=96,
                   suite_files=3, suite_subtests=106, patch_commands=patch_commands,
                   scratch_removed=not scratch.exists(), native_refinement_proved=False,
                   discovered_by='source/spec audit; historical rediscovery', committed=False)
    (HERE / 'ACCEPTANCE.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
