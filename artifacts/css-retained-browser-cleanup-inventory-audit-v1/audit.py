import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PLAN = ROOT / 'artifacts/css-retained-browser-cleanup-candidates-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
assert sha((PLAN / 'FILES.json').read_bytes()) == 'db7fabe3dc635019576f1f2dadd1b342672721711ccb00d385ff2b26447228d7'
for name, record in json.loads((PLAN / 'FILES.json').read_bytes()).items():
    assert sha((PLAN / name).read_bytes()) == record['sha256']
plan = json.loads((PLAN / 'CANDIDATES.json').read_bytes())
refs = json.loads((PLAN / 'REFERENCES.json').read_bytes())
report = {'started_unix': time.time(), 'read_only': True, 'archives': [], 'commands': []}

def stable(st):
    return [st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns]

def command(argv, label):
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (HERE / (label + '.stdout')).write_bytes(proc.stdout)
    (HERE / (label + '.stderr')).write_bytes(proc.stderr)
    item = {'argv': argv, 'exit': proc.returncode, 'stdout': label + '.stdout', 'stdout_sha256': sha(proc.stdout), 'stderr': label + '.stderr', 'stderr_sha256': sha(proc.stderr)}
    report['commands'].append(item)
    return proc

for number, row in enumerate(plan['candidates']):
    start = time.time()
    manifest_path = ROOT / row['runtime_manifest']
    assert sha(manifest_path.read_bytes()) == row['runtime_manifest_sha256']
    manifest = json.loads(manifest_path.read_bytes())
    manifest = manifest.get('files', manifest)
    for key in ('ownership', 'inventory'):
        path = ROOT / row[key]
        pin = manifest[path.name]
        pin = pin['sha256'] if isinstance(pin, dict) else pin
        assert sha(path.read_bytes()) == pin == refs[row[key]]
    owned = json.loads((ROOT / row['ownership']).read_bytes())
    snapshot = json.loads((ROOT / row['inventory']).read_bytes())
    directory = Path(row['directory'])
    before = directory.lstat()
    assert stat.S_ISDIR(before.st_mode) and not directory.is_symlink()
    assert [before.st_dev, before.st_ino] == row['expected_root_identity'] == owned['owned_identity']
    assert owned['owned_directory'] == str(directory)
    assert sorted(p.name for p in directory.iterdir()) == ['Nightly.app']
    app = directory / 'Nightly.app'
    assert snapshot['application'] == str(app)
    expected_files = snapshot['files']
    expected_dirs = snapshot['resolved_source_inventory']['directories']
    assert expected_files == snapshot['resolved_source_inventory']['files']
    found_files = {}
    found_dirs = {}
    for current, dirs, files in os.walk(app, followlinks=False):
        current = Path(current)
        rel = str(current.relative_to(app))
        ds = current.lstat()
        assert stat.S_ISDIR(ds.st_mode) and not current.is_symlink()
        assert rel in expected_dirs and stat.S_IMODE(ds.st_mode) == expected_dirs[rel][2], rel
        found_dirs[rel] = stat.S_IMODE(ds.st_mode)
        for name in dirs:
            child = current / name
            assert stat.S_ISDIR(child.lstat().st_mode) and not child.is_symlink(), str(child)
        for name in files:
            path = current / name
            relfile = str(path.relative_to(app))
            first = path.lstat()
            assert stat.S_ISREG(first.st_mode) and not path.is_symlink() and relfile in expected_files, str(path)
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                opened = os.fstat(stream.fileno())
                assert stable(opened) == stable(first)
                while block := stream.read(1024 * 1024):
                    digest.update(block)
                assert stable(os.fstat(stream.fileno())) == stable(first)
            assert stable(path.lstat()) == stable(first)
            record = {'bytes': first.st_size, 'mode': stat.S_IMODE(first.st_mode), 'sha256': digest.hexdigest()}
            assert record == expected_files[relfile], relfile
            found_files[relfile] = record
    assert set(found_dirs) == set(expected_dirs)
    assert found_files == expected_files
    assert sum(r['bytes'] for r in found_files.values()) == snapshot['bytes']
    assert stable(directory.lstat()) == stable(before)
    assert sorted(p.name for p in directory.iterdir()) == ['Nightly.app']
    report['archives'].append({'directory': str(directory), 'root_identity': row['expected_root_identity'], 'runtime_manifest_sha256': row['runtime_manifest_sha256'], 'snapshot_sha256': sha((ROOT / row['inventory']).read_bytes()), 'files': len(found_files), 'directories': len(found_dirs), 'bytes': snapshot['bytes'], 'files_sha256': sha(json.dumps(found_files, sort_keys=True).encode()), 'directory_modes_sha256': sha(json.dumps(found_dirs, sort_keys=True).encode()), 'full_inventory_verified': True, 'no_symlinks_or_extra_entries': True, 'started_unix': start, 'finished_unix': time.time()})
    print(json.dumps(report['archives'][-1]), flush=True)
    proc = command(['/usr/sbin/lsof', '-nP', '+D', str(directory)], 'lsof-' + str(number))
    report['archives'][-1]['no_visible_open_files'] = proc.returncode == 1 and not proc.stdout and not proc.stderr

proc = command(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,command='], 'ps')
needles = [row['directory'].encode() for row in plan['candidates']]
matches = [line.decode(errors='replace') for line in proc.stdout.splitlines() if any(n in line for n in needles)]
report['process_matches'] = matches
report['no_matching_visible_process_commands'] = proc.returncode == 0 and not proc.stderr and not matches
report['finished_unix'] = time.time()
report['limitations'] = ['Point-in-time observation; root must recheck ownership/inventory/process freshness after active publication.', 'Unprivileged lsof/ps visibility only; command-line matching cannot identify a process that omits the archive path.', 'No archive source inode equality required: resolved_source_inventory identities belong to original copied build.', 'No deletion or source/index/canonical writes performed.']
(HERE / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'full_inventory_verified': len(report['archives']) == 3, 'no_matching_visible_process_commands': report['no_matching_visible_process_commands'], 'no_visible_open_files': all(a['no_visible_open_files'] for a in report['archives'])}), flush=True)
