#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError((command, result.returncode, result.stdout, result.stderr))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    basis = json.loads((HERE / 'BASIS.json').read_text())
    query = ROOT / 'artifacts/css-pseudo-animation-query-inputs-20261110-v1'
    assert digest(query / 'candidate.patch') == basis['query_patch_sha256']
    for item in basis['files']:
        path = HERE / 'basis' / item['path']
        assert digest(path) == item['sha256']
        original = HERE / 'source' / item['path']
        if original.exists():
            data = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', basis['revision'] + ':' + item['path']], cwd=ROOT)
            assert data == original.read_bytes() == path.read_bytes()
        else:
            assert path.read_bytes() == (query / 'candidate' / item['path']).read_bytes()
    with tempfile.TemporaryDirectory(prefix='pseudo-query-driver-') as name:
        temporary = Path(name)
        generated = temporary / 'generated'
        run([sys.executable, '-B', str(HERE / 'prepare.py'), '--out', str(generated)])
        expected = HERE / 'generated'
        for f in sorted(expected.rglob('*')):
            if f.is_file():
                assert f.read_bytes() == (generated / f.relative_to(expected)).read_bytes()
        applied = temporary / 'applied'
        shutil.copytree(HERE / 'basis', applied)
        run(['patch', '-p1', '--batch', '-i', str(expected / 'driver.patch')], cwd=applied)
        for f in sorted((expected / 'candidate').rglob('*')):
            if f.is_file():
                assert f.read_bytes() == (applied / f.relative_to(expected / 'candidate')).read_bytes()
        run(['patch', '-R', '-p1', '--batch', '-i', str(expected / 'driver.patch')], cwd=applied)
        for f in sorted((HERE / 'basis').rglob('*')):
            if f.is_file():
                assert f.read_bytes() == (applied / f.relative_to(HERE / 'basis')).read_bytes()
        assert not (applied / 'dom/base/test/test_missing_pseudo_animation_query.html').exists()

    sys.path[:0] = [str(ROOT / 'xpcom/idl-parser'), str(ROOT / 'third_party/python/ply')]
    from xpidl import xpidl
    idl = HERE / 'generated/candidate/dom/interfaces/base/nsIDOMWindowUtils.idl'
    parsed = xpidl.IDLParser().parse(idl.read_text(), filename=str(idl))
    interface = next(p for p in parsed.productions if getattr(p, 'name', None) == 'nsIDOMWindowUtils')
    method = [m for m in interface.members if getattr(m, 'name', None) == 'getMissingPseudoAnimationValuesForTesting']
    assert len(method) == 1 and len(method[0].params) == 4
    manifest = tomllib.loads((HERE / 'generated/candidate/dom/base/test/mochitest.toml').read_text())
    assert manifest['test_missing_pseudo_animation_query.html']['prefs'] == ['layout.css.scroll-driven-animations.enabled=true', 'layout.css.typed-om.enabled=true']
    html = (HERE / 'test.html').read_text()
    names = re.findall(r'add_task\(async function (\w+)\(', html)
    assert len(names) == len(set(names)) == 13
    inventory = run(['node', str(HERE / 'inventory.cjs')], cwd=ROOT)
    assert inventory.stdout == (HERE / 'ASSERTIONS.json').read_text()
    assertions = json.loads(inventory.stdout)
    assert assertions['assertion_count'] == 208
    assert assertions['totals'] == {'diagnostic': 150, 'result': 36, 'setup': 20, 'preservation': 2}
    js = html.split('<script>')[1].split('</script>')[0]
    run(['node', '--check'], input=js)
    lint = run([str(ROOT / 'node_modules/.bin/eslint'), '--stdin', '--stdin-filename', 'dom/base/test/test_missing_pseudo_animation_query.html', '--rule', 'mozilla/import-globals: off'], input=html, cwd=ROOT)
    (out / 'eslint-scoped.log').write_text(lint.stdout + lint.stderr)
    formatted = run([str(ROOT / 'node_modules/.bin/prettier'), '--stdin-filepath', 'dom/base/test/test_missing_pseudo_animation_query.html'], input=html, cwd=ROOT)
    assert formatted.stdout == html
    body = (HERE / 'driver.cpp').read_text()
    lazy = body.index('ResolveStyleLazily(')
    calls = [m.start() for m in re.finditer('ComposeServoAnimationRulesForMissingPseudo', body)]
    assert len(calls) == 3 and all(p > lazy for p in calls)
    for operation in ['UpdateProperties(', 'RequestRestyle(', 'TryTrigger', '->Tick(', '->Play(', '->Pause(', 'ComposeStyle(', 'SetCurrentTime(', 'UpdateCascadeResults(']:
        assert operation not in body, operation
    assert body.count('mPendingState == state.mPending') == 1
    assert body.count('mHoldTime == state.mHold') == 1
    assert body.count('mStartTime == state.mStart') == 1
    assert 'animation.CascadeLevel() == state.mLevel' in body
    assert body.index('const Animation& animation = *state.mAnimation') > calls[-1]
    assert 'occupied.get() == occupiedPointer' in body and 'other.get() == otherPointer' in body
    assert 'aliased, aliased) && !aliased' in body
    assert body.count('sameEffects();') == 2
    report = {
        'status': 'PASS', 'basis_files': len(basis['files']),
        'query_patch_sha256': basis['query_patch_sha256'],
        'driver_patch_sha256': digest(HERE / 'generated/driver.patch'),
        'deterministic_generation': True, 'forward_reverse_patch': True,
        'xpidl_syntax_parsed': True, 'xpidl_types_resolved': False,
        'mochitest_manifest_parsed': True, 'task_names': names,
        'assertion_inventory': assertions['assertion_count'],
        'assertion_classifications': assertions['totals'],
        'inert_javascript_syntax': True,
        'eslint_other_rules_pass': True, 'eslint_import_globals_disabled': True,
        'prettier_idempotent': True,
        'native_compilation': False, 'browser_execution': False,
        'state_unchanged_claim': 'Named captured fields only; not complete renderer state or a no-reentrancy proof',
    }
    (out / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
