import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


TESTHARNESS = frozenset(['testing/web-platform/tests/web-animations/animation-model/keyframe-effects/root-font-self-reference.html', 'testing/web-platform/tests/svg/animations/root-font-self-reference.html'])
SUPPORT = frozenset(['testing/web-platform/tests/svg/animations/resources/root-font-reference.svg', 'testing/web-platform/tests/svg/animations/resources/root-font-target.svg'])


def verify_entries(serialized, tests_root, files):
    assert set(files) == TESTHARNESS | SUPPORT and not TESTHARNESS & SUPPORT
    assert serialized['version'] == 9 and serialized['url_base'] == '/'
    expected = {'testharness': {}, 'support': {}}
    for kind, paths in (('testharness', TESTHARNESS), ('support', SUPPORT)):
        for name in paths:
            path = ROOT / name
            body = path.read_bytes()
            assert sha(path) == files[name]
            blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
            relative = path.relative_to(tests_root)
            entries = expected[kind]
            for part in relative.parts[:-1]:
                entries = entries.setdefault(part, {})
            entries[relative.name] = ([blob, [None, {'timeout': 'long'}]]
                                      if kind == 'testharness' else [blob, []])
    assert serialized['items'] == expected
    return sorted('/' + str((ROOT / name).relative_to(tests_root)) for name in TESTHARNESS)


def run(policy, installation_manifest):
    output = ROOT / policy['runtime_output'] / 'delivery'
    output.mkdir()
    files = {name: record['sha256'] for name, record in policy['files'].items() if name.startswith('testing/')}
    for name, pin in files.items():
        assert sha(ROOT / name) == pin
    save(output / 'COMMANDS.json', {'lint': policy['lint_command'],
         'manifest': list(sys.orig_argv),
         'manifest_api': 'Manifest(installed_tests_root, /).update(selected_paths, parallel=False)',
         'installation_manifest': installation_manifest})
    with (output / 'lint.log').open('x') as stream:
        result = subprocess.run(policy['lint_command'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0'))
    save(output / 'LINT-RESULT.json', {'exit': result.returncode, 'command': policy['lint_command']})
    assert result.returncode == 0, 'Installed WPT lint failed; retain output, do not commit'
    tests_root = ROOT / 'testing/web-platform/tests'
    sys.path[:0] = [str(p) for p in (tests_root / 'tools/third_party').iterdir() if p.is_dir()] + [str(tests_root / 'tools'), str(tests_root)]
    from manifest.manifest import Manifest
    manifest = Manifest(str(tests_root), '/')
    manifest.update([(str((ROOT / name).relative_to(tests_root)), None, True) for name in sorted(files)], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    urls = verify_entries(serialized, tests_root, files)
    save(output / 'SUBSET-MANIFEST.json', serialized)
    evidence = {str(p.relative_to(ROOT)): sha(p) for p in output.iterdir()}
    save(output / 'DELIVERY.json', {'lint_exit': 0, 'lint_errors': 0, 'files': files,
         'lint_command': policy['lint_command'], 'registered_urls': urls,
         'support_files': {name: files[name] for name in sorted(SUPPORT)},
         'manifest_entries_verified': True, 'browser_executed': False,
         'manifest_command': json.loads((output / 'COMMANDS.json').read_bytes())['manifest'],
         'evidence': evidence, 'installation_manifest': installation_manifest})
