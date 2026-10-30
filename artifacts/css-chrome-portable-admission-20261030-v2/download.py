import base64
import concurrent.futures
import hashlib
import json
import posixpath
import stat
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
owner = json.loads((HERE / 'OWNER.json').read_text())
root = Path(owner['temporary_directory'])
assert [root.stat().st_dev, root.stat().st_ino] == owner['identity']


def download(item):
    name, spec = item
    archive = root / (name + '.zip')
    assert not archive.exists()
    with (HERE / (name + '-download.log')).open('x') as log:
        subprocess.run(['curl', '--fail', '--location', '--proto', '=https',
                        '--connect-timeout', '30', '--max-time', '300',
                        '--output', str(archive), spec['url']],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    data = archive.read_bytes()
    assert len(data) == spec['bytes']
    assert base64.b64encode(hashlib.md5(data).digest()).decode() == spec['md5_base64']
    symlinks = {}
    entries = []
    with zipfile.ZipFile(archive) as zipped:
        for info in zipped.infolist():
            path = info.filename.rstrip('/')
            assert path and not path.startswith('/') and '\\' not in path
            assert '..' not in path.split('/')
            assert path not in entries
            entries.append(path)
            mode = info.external_attr >> 16
            assert stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK)
            if stat.S_ISLNK(mode):
                target = zipped.read(info).decode()
                assert not target.startswith('/') and '\\' not in target
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                assert target != '..' and not target.startswith('../')
                symlinks[path] = target
        for entry in entries:
            path = entry
            seen = set()
            while True:
                assert path not in seen
                seen.add(path)
                parts = path.split('/')
                links = ['/'.join(parts[:i]) for i in range(1, len(parts) + 1)]
                link = next((p for p in links if p in symlinks), None)
                if link is None:
                    break
                path = posixpath.normpath(symlinks[link] + path[len(link):])
                assert path != '..' and not path.startswith('../') and not path.startswith('/')
    return name, {'url': spec['url'], 'bytes': len(data),
                  'sha256': hashlib.sha256(data).hexdigest(),
                  'transport_md5_matched': True, 'archive_path': str(archive),
                  'entry_count': len(entries), 'symlinks': symlinks,
                  'archive_paths_checked': True, 'extracted': False}


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = dict(executor.map(download, owner['assets'].items()))
(HERE / 'DOWNLOADS.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({k: {n: v[n] for n in ('bytes', 'sha256', 'entry_count')}
                  for k, v in results.items()}), flush=True)
