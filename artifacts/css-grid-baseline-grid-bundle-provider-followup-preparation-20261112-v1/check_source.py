import ast
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    for name, digest in json.loads((HERE / 'PREDECESSORS.json').read_text()).items():
        assert sha(Path(name)) == digest
    for name, digest in json.loads((HERE / 'REFERENCE-INPUTS.json').read_text()).items():
        assert sha(Path(name)) == digest
    for name, row in json.loads((HERE / 'ORIGINS.json').read_text()).items():
        assert sha(HERE / name) == sha(Path(row['origin'])) == row['sha256']
    for name, digest in json.loads((HERE / 'FIXTURE-ORIGINS.json').read_text()).items():
        assert sha(Path(name)) == digest
    old_provider = HERE.parent / 'css-grid-baseline-demand-provider-trace-plan-20261112-v1'
    for name in ('eligibility.html', 'isolation.html', 'debug-isolation.html'):
        assert (HERE / 'provider-fixtures' / name).read_bytes() == (old_provider / name).read_bytes()
    old_work = HERE.parent / 'css-grid-baseline-measurement-work-execution-plan-20261112-v3/fixtures'
    for path in (HERE / 'work-fixtures').iterdir():
        assert path.read_bytes() == (old_work / path.name).read_bytes()
    commands = []
    for stage in ('provider', 'work'):
        base = HERE / stage
        edits = json.loads((base / 'EDITS.json').read_text())
        changed = sorted({edit['file'] for edit in edits})
        for path in (base / 'original').rglob('*'):
            if not path.is_file():
                continue
            name = str(path.relative_to(base / 'original'))
            original = path.read_text()
            candidate = (base / 'candidate' / name).read_text()
            reconstructed = candidate
            for edit in reversed([item for item in edits if item['file'] == name]):
                assert reconstructed.count(edit['new']) == 1
                reconstructed = reconstructed.replace(edit['new'], edit['old'])
            assert reconstructed == original
            for getter in ('GetNaturalBaselineBOffset(', 'GetBBaseline(', 'GetIBaseline('):
                assert candidate.count(getter) == original.count(getter), (stage, name, getter)
        with tempfile.TemporaryDirectory(prefix='grid-bundle-trace-source-') as tmp:
            scratch = Path(tmp)
            shutil.copytree(base / 'original', scratch, dirs_exist_ok=True)
            for reverse in (False, True):
                argv = ['/usr/bin/patch', '--batch', '-p1'] + (['-R'] if reverse else [])
                completed = subprocess.run(argv, cwd=scratch, input=(base / 'DIAGNOSTIC.patch').read_bytes(), capture_output=True)
                commands.append(dict(stage=stage, argv=argv, exit=completed.returncode,
                                     stdout=completed.stdout.decode(), stderr=completed.stderr.decode()))
                assert completed.returncode == 0
                for name in changed:
                    assert (scratch / name).read_bytes() == (base / ('original' if reverse else 'candidate') / name).read_bytes()
        assert not scratch.exists()
    source = Path(json.loads((HERE / 'EXTRACTION.json').read_text())['source']).read_text()
    start = source.index('enum class MeasuringReflowRequest')
    end = source.index('// A cached result', start)
    a = source.index('  struct Snapshot {', end)
    b = source.index('\n  CachedBAxisMeasurement(', a)
    assert (HERE / 'snapshot-extracted.inc').read_text() == source[start:end] + source[a:b]
    assert 'NS_STATE_GRID_PRODUCED_BASELINES' in (HERE / 'work/candidate/layout/generic/nsGridContainerFrame.cpp').read_text()
    result = dict(status='PASS source-only diagnostic transport and exact fixtures/extraction',
                  getter_call_counts_unchanged=True, source_edits_invert_exactly=True,
                  patch_commands=commands, original_work_configurations=4, flushes_per_configuration=29,
                  provider_fixture_families=3, state_methods_verbatim=True,
                  compiler_browser_native_execution=False, scratch_removed=True)
    (HERE / 'SOURCE-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
