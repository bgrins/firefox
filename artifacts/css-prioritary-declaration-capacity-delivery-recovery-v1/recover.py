import hashlib
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = 'artifacts/css-prioritary-declaration-capacity-publication-capacity-runtime-1'
TEST = 'testing/web-platform/tests/css/css-cascade/prioritary-after-many-unrelated-declarations.html'
URL = '/css/css-cascade/prioritary-after-many-unrelated-declarations.html'
TEST_SHA = 'ee8e840d4d1d260dc5effcd25b2a541ff594963cd2ac49a81b61db0e21ff0ce2'
EPOCH = 'b3ef95162682fb9a419152d00d4aeee0e65dec9a1b0d329984b7d6faec4eb25c'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def verify_entries(serialized, body):
    assert hashlib.sha256(body).hexdigest() == TEST_SHA
    blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    assert serialized['url_base'] == '/'
    assert serialized['version'] == 9
    assert serialized['items'] == {'testharness': {'css': {'css-cascade': {
        Path(TEST).name: [blob, [None, {'timeout': 'long'}]]}}}}
    return [URL]


def verify_saved(commands, lint, installed, failed):
    expected = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'lint', '-l',
                'wpt', '--include-third-party', TEST]
    assert lint == {'exit': 0, 'command': expected}
    assert commands['lint'] == expected
    assert commands['installation_manifest'] == installed['manifest_sha256']
    assert installed['installed'] and not installed['accepted'] and not installed['app_rebuilt']
    assert installed['stage'] == 'capacity' and installed['epoch_sha256'] == EPOCH
    assert installed['files'] == ['servo/components/style/properties/cascade.rs', TEST]
    assert failed['session'] == 4585 and failed['launch'] == 'b707a2'
    assert failed['terminal'] == 'ed9feb' and failed['exit'] == 1 and failed['lint_exit'] == 0
    return expected


def missing_outputs(output):
    assert output.is_dir() and not output.is_symlink()
    for name in ('SUBSET-MANIFEST.json', 'DELIVERY.json'):
        assert not os.path.lexists(output / name), name


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    assert len(sys.argv) == 3 and sys.argv[1] == '--run'
    assert sha(HERE / 'FILES.json') == sys.argv[2]
    for name, record in read(HERE / 'FILES.json').items():
        assert sha(HERE / name) == record['sha256']
    pins = read(HERE / 'REFERENCES.json')
    for name, pin in pins.items():
        assert sha(ROOT / name) == pin, name
    installed = read(ROOT / RUNTIME / 'INSTALL-RESULT.json')
    output = ROOT / RUNTIME / 'delivery'
    commands = read(output / 'COMMANDS.json')
    lint_command = verify_saved(commands, read(output / 'LINT-RESULT.json'), installed,
                                read(ROOT / RUNTIME / 'ROOT-DELIVERY-ATTEMPT1-TERMINAL.json'))
    missing_outputs(output)
    epoch_path = ROOT / 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json'
    assert sha(epoch_path) == EPOCH
    assert sha(ROOT / TEST) == TEST_SHA
    assert sha(ROOT / 'servo/components/style/properties/cascade.rs') == '832d08549227e20f88f1bede253824b75b66a58b4adb2b7efc357cc52915f1f5'
    tests_root = ROOT / 'testing/web-platform/tests'
    sys.path[:0] = [str(p) for p in (tests_root / 'tools/third_party').iterdir() if p.is_dir()] + [str(tests_root / 'tools'), str(tests_root)]
    from manifest.manifest import Manifest
    manifest = Manifest(str(tests_root), '/')
    manifest.update([(str((ROOT / TEST).relative_to(tests_root)), None, True)], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    urls = verify_entries(serialized, (ROOT / TEST).read_bytes())
    for name, pin in pins.items():
        assert sha(ROOT / name) == pin, name
    assert sha(epoch_path) == EPOCH
    missing_outputs(output)
    save(output / 'SUBSET-MANIFEST.json', serialized)
    evidence = dict(pins)
    evidence[str((HERE / 'FILES.json').relative_to(ROOT))] = sha(HERE / 'FILES.json')
    evidence[str((HERE / 'recover.py').relative_to(ROOT))] = sha(HERE / 'recover.py')
    evidence[str((output / 'SUBSET-MANIFEST.json').relative_to(ROOT))] = sha(output / 'SUBSET-MANIFEST.json')
    receipt = {'lint_exit': 0, 'lint_errors': 0, 'files': {TEST: TEST_SHA},
        'lint_command': lint_command, 'registered_urls': urls,
        'manifest_entries_verified': True, 'browser_executed': False,
        'manifest_command': list(sys.orig_argv), 'evidence': evidence,
        'installation_manifest': installed['manifest_sha256'],
        'recovery': {'lint_reused': True, 'original_delivery_exit': 1,
                     'expected_metadata': {'timeout': 'long'},
                     'original_manifest_command': commands['manifest']}}
    save(output / 'DELIVERY.json', receipt)
    print(json.dumps({'delivery_sha256': sha(output / 'DELIVERY.json'), 'lint_reused': True}))


if __name__ == '__main__':
    main()
