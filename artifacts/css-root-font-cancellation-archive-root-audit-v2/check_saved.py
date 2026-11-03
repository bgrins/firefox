import copy
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))


binding = read(HERE / 'BINDINGS.json')
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is True
for key in ('archive_records', 'launch', 'outer_group', 'owner_manifest_sha256', 'result_sha256', 'terminal_sha256'):
    assert binding[key] is None
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin, path
parent = ROOT / 'artifacts/css-root-font-cancellation-native-root-audit-v2/audit.py'
expected = parent.read_text().replace('css-root-font-cancellation-candidate-browser-v2',
                                    'css-root-font-cancellation-archive-candidate-browser-v2').replace(
    'css-root-font-cancellation-candidate-browser-runtime-v1', 'css-root-font-cancellation-archive-candidate-browser-runtime-v1')
hook = "archive_audit = load('archive_handoff_audit', HERE / 'archive_audit.py')\nreport['archive_observation'] = archive_audit.verify_archive(ROOT, RUNTIME, policy, roles, claims, result, binding)\n"
expected = expected.replace('with (RUNTIME / "ROOT-LIVE-RESTORATION.json").open("x") as stream:', hook + 'with (RUNTIME / "ROOT-LIVE-RESTORATION.json").open("x") as stream:')
assert (HERE / 'audit.py').read_text() == expected
delta = ''.join(difflib.unified_diff(parent.read_text().splitlines(True), expected.splitlines(True),
                                   fromfile=str(parent.relative_to(ROOT)), tofile=str((HERE / 'audit.py').relative_to(ROOT))))
assert (HERE / 'AUDIT-DELTA.patch').read_text() == delta
for name in ('audit.py', 'archive_audit.py'):
    compile((HERE / name).read_bytes(), name, 'exec')
audit = load('archive_saved_audit', HERE / 'archive_audit.py')
source_helper = ROOT / 'artifacts/css-root-font-cancellation-archive-candidate-browser-v1/archive.py'
helper = load('archive_saved_helper', source_helper)
positive, rejected = [], []
scratch_paths = []


class Fixture:
    def __init__(self, root, directory):
        self.root = root
        self.directory = directory
        self.runtime = root / 'artifacts/runtime'
        self.app = directory / 'Nightly.app'
        source = root / 'source.app'
        for name, data in {'Contents/Resources/application.ini': b'[App]\nBuildID=synthetic\n',
                           'Contents/MacOS/firefox': b'synthetic firefox',
                           'Contents/MacOS/XUL': b'synthetic XUL'}.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        shutil.copytree(source, self.app)
        owner = root / 'artifacts/css-root-font-cancellation-archive-candidate-browser-v2'
        owner.mkdir(parents=True)
        shutil.copyfile(source_helper, owner / 'archive.py')
        validator = 'artifacts/css-root-self-smil-archived-original-v1/run.py'
        (root / validator).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / validator, root / validator)
        self.policy = {'head': 'synthetic-native-head', 'bundle_path': 'objdir/Nightly.app',
                       'source_context_pins': {'servo/ports/geckolib/glue.rs': 'original-glue',
                                              'servo/components/style/custom_properties.rs': 'original-custom'},
                       'archive': {'validator': validator, 'validator_sha256': sha(root / validator)}}
        self.roles = {name: {'candidate_sha256': hashlib.sha256(name.encode()).hexdigest()}
                      for name in ('servo/components/style/data.rs', 'servo/components/style/traversal.rs')}
        self.claims = {name: {'identity': [1, i + 10]} for i, name in enumerate(self.roles)}
        self.binding = copy.deepcopy(binding)
        self.binding['owner_manifest_sha256'] = 'synthetic-owner-manifest'
        self.result = {'success': True, 'error': None, 'publication_errors': []}
        self.ownership = {'owned_directory': str(directory),
                          'owned_identity': [directory.stat().st_dev, directory.stat().st_ino]}
        files = helper.inventory(self.app, False)['files']
        self.build = {'native_sources': {name: row['candidate_sha256'] for name, row in self.roles.items()},
                      'binaries': {self.policy['bundle_path'] + '/' + name: files[name]['sha256']
                                   for name in ('Contents/MacOS/firefox', 'Contents/MacOS/XUL')},
                      'application_metadata': {'sha256': files['Contents/Resources/application.ini']['sha256'],
                                               'source_role': 'candidate', 'revision': self.policy['head']},
                      'browser_build_performed': True, 'command_success': True,
                      'preservation_verified': True, 'error': None}
        write(self.runtime / 'candidate-build/RESULT.json', self.build)
        write(self.runtime / 'candidate-build/COMMAND.json', {'source_sha256': self.build['native_sources'],
                                                            'owner_manifest': self.binding['owner_manifest_sha256']})
        for name in ('RESTORATION.json', 'POST.json', 'candidate-OUTCOMES.json'):
            write(self.runtime / name, {'synthetic': name})
        self.snapshot = dict(self.ownership, application=str(self.app), files=files,
                             bytes=sum(row['bytes'] for row in files.values()), source_role='candidate',
                             native_head=self.policy['head'], native_sources=self.build['native_sources'],
                             build_receipt=str((self.runtime / 'candidate-build/RESULT.json').relative_to(root)),
                             build_receipt_sha256=sha(self.runtime / 'candidate-build/RESULT.json'),
                             build_command_sha256=sha(self.runtime / 'candidate-build/COMMAND.json'),
                             application_metadata=self.build['application_metadata'], binaries=self.build['binaries'],
                             candidate_wpt_outcomes_sha256=sha(self.runtime / 'candidate-OUTCOMES.json'),
                             source_claims={name: [row['candidate_sha256'], *self.claims[name]['identity']]
                                            for name, row in self.roles.items()},
                             unchanged_source_preimages=self.policy['source_context_pins'],
                             resolved_source_inventory=helper.inventory(source, False), provisional=True,
                             independent_restoration_required=True, diagnostic_run_performed=False)
        self.reset()

    def reset(self):
        for path in self.runtime.glob('ARCHIVE-*.json'):
            path.unlink()
        write(self.runtime / 'ARCHIVE-OWNERSHIP.json', self.ownership)
        write(self.runtime / 'ARCHIVE-SNAPSHOT.json', self.snapshot)
        write(self.runtime / 'ARCHIVE-VALIDATION.json', helper.validate(self.root, self.snapshot, self.policy['archive']))
        self.handoff()

    def handoff(self):
        write(self.runtime / 'ARCHIVE-HANDOFF.json', {
            'application': str(self.app), 'snapshot_sha256': sha(self.runtime / 'ARCHIVE-SNAPSHOT.json'),
            'restoration_sha256': sha(self.runtime / 'RESTORATION.json'), 'post_sha256': sha(self.runtime / 'POST.json'),
            'owner_terminal_and_independent_audit_required': True, 'browser_execution_authorized': False})

    def verify(self):
        self.binding['archive_records'] = {path.name: sha(path) for path in self.runtime.glob('ARCHIVE-*.json')}
        return audit.verify_archive(self.root, self.runtime, self.policy, self.roles, self.claims, self.result, self.binding)

    def reject(self, name, mutation):
        self.reset()
        mutation()
        try:
            self.verify()
        except (AssertionError, KeyError, FileNotFoundError):
            rejected.append(name)
        else:
            raise AssertionError('accepted ' + name)

    def change(self, name, key, value):
        path = self.runtime / name
        row = read(path)
        row[key] = value
        write(path, row)
        if name == 'ARCHIVE-SNAPSHOT.json':
            self.handoff()


with tempfile.TemporaryDirectory(prefix='archive-audit-fixture-', dir='/private/tmp') as work, tempfile.TemporaryDirectory(prefix='css-font-unit-candidate-', dir='/private/tmp') as owned:
    scratch_paths.extend([work, owned])
    f = Fixture(Path(work), Path(owned))
    accepted = f.verify()
    assert accepted['archive_retained_verified'] and not accepted['browser_execution_authorized'] and not accepted['native_acceptance']
    positive.append('real inventory and validator accept isolated successful archive')
    for name, file, key, value in [
        ('ownership inode', 'ARCHIVE-OWNERSHIP.json', 'owned_identity', [0, 0]),
        ('source binding', 'ARCHIVE-SNAPSHOT.json', 'native_sources', {}),
        ('source inode', 'ARCHIVE-SNAPSHOT.json', 'source_claims', {}),
        ('original glue', 'ARCHIVE-SNAPSHOT.json', 'unchanged_source_preimages', {}),
        ('build receipt', 'ARCHIVE-SNAPSHOT.json', 'build_receipt_sha256', 'bad'),
        ('build command', 'ARCHIVE-SNAPSHOT.json', 'build_command_sha256', 'bad'),
        ('WPT outcomes', 'ARCHIVE-SNAPSHOT.json', 'candidate_wpt_outcomes_sha256', 'bad'),
        ('binary binding', 'ARCHIVE-SNAPSHOT.json', 'binaries', {}),
        ('restoration handoff', 'ARCHIVE-HANDOFF.json', 'restoration_sha256', 'bad'),
        ('post handoff', 'ARCHIVE-HANDOFF.json', 'post_sha256', 'bad'),
        ('browser authority', 'ARCHIVE-HANDOFF.json', 'browser_execution_authorized', True),
    ]:
        f.reject(name, lambda file=file, key=key, value=value: f.change(file, key, value))
    f.reject('missing handoff', lambda: (f.runtime / 'ARCHIVE-HANDOFF.json').unlink())
    f.reject('success with cleanup', lambda: write(f.runtime / 'ARCHIVE-CLEANUP.json', {'removed': False}))
    binary = f.app / 'Contents/MacOS/firefox'
    original = binary.read_bytes()
    f.reject('changed archive bytes', lambda: binary.write_bytes(original + b'changed'))
    binary.write_bytes(original)
    f.reset()
    sibling = f.directory / 'hardlink'
    os.link(binary, sibling)
    try:
        f.verify()
    except AssertionError:
        rejected.append('extra ownership entry')
    else:
        raise AssertionError('accepted extra ownership entry')
    sibling.unlink()
    link = Path(work) / 'hardlink'
    os.link(binary, link)
    try:
        f.verify()
    except AssertionError:
        rejected.append('archive hardlink')
    else:
        raise AssertionError('accepted archive hardlink')
    link.unlink()
    binary.unlink()
    binary.symlink_to(Path(work) / 'source.app/Contents/MacOS/firefox')
    try:
        f.verify()
    except AssertionError:
        rejected.append('archive symlink')
    else:
        raise AssertionError('accepted archive symlink')
    binary.unlink()
    binary.write_bytes(original)
    f.result.update(success=False, error='synthetic copy/publication failure')
    row = f.verify()
    assert row['status'] == 'failed-retained-untrusted' and not row['archive_retained_verified']
    assert not row['handoff_is_authority']
    positive.append('failed retained archive and stale handoff are untrusted')
    f.reset()
    (f.runtime / 'ARCHIVE-OWNERSHIP.json').unlink()
    write(f.runtime / 'ARCHIVE-CLEANUP.json', {'removed': False, 'ownership': f.ownership})
    assert f.verify()['status'] == 'failed-retained-untrusted'
    positive.append('cleanup-only ownership remains untrusted')
    f.reject('claimed removal while retained', lambda: write(f.runtime / 'ARCHIVE-CLEANUP.json', {'removed': True}))
    shutil.rmtree(f.app)
    f.directory.rmdir()
    for path in f.runtime.glob('ARCHIVE-*.json'):
        path.unlink()
    write(f.runtime / 'ARCHIVE-OWNERSHIP.json', f.ownership)
    write(f.runtime / 'ARCHIVE-CLEANUP.json', {'removed': True, 'reason': 'synthetic failure'})
    assert f.verify()['status'] == 'failed-no-recorded-retained-archive'
    positive.append('removed failed copy')
    for path in f.runtime.glob('ARCHIVE-*.json'):
        path.unlink()
    assert f.verify()['status'] == 'failed-no-recorded-retained-archive'
    positive.append('failure before ownership')
assert all(not Path(path).exists() for path in scratch_paths)
print(json.dumps({'references': len(binding['references']), 'audit_parent_delta_exact': True,
                  'positive_cases': positive, 'rejected_controls': rejected,
                  'scratch_paths': scratch_paths, 'scratch_absent': True,
                  'live_audit_executed': False}, indent=2))
