import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for name, digest in sources['files'].items():
        result = subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false',
                                          'show', sources['revision'] + ':' + name])
        assert hashlib.sha256(result).hexdigest() == digest == sha(HERE / 'source' / name)
    query = json.loads((HERE / 'QUERY-INPUTS.json').read_text())
    origin = ROOT / query['origin']
    assert sha(origin / 'RUN-INPUTS.json') == query['manifest_sha256']
    manifest = json.loads((origin / 'RUN-INPUTS.json').read_text())
    for name, digest in query['files'].items():
        assert manifest[name] == digest == sha(origin / name)
        assert sha(HERE / 'query-source' / Path(name).relative_to('candidate')) == digest
    subprocess.run(['node', '--check', str(HERE / 'pending-timing.js')], check=True)
    html = (HERE / 'standalone.html').read_text()
    scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
    assert len(scripts) == 1
    with tempfile.TemporaryDirectory(prefix='pending-timing-syntax-') as directory:
        script = Path(directory) / 'inline.js'
        script.write_text(scripts[0])
        subprocess.run(['node', '--check', str(script)], check=True)
    result = {'status': 'PASS', 'native_git_inputs': len(sources['files']),
              'query_inputs': len(query['files']), 'javascript_syntax': True,
              'browser_execution': False, 'production_candidate_modified': False,
              'scratch_removed': not Path(directory).exists(),
              'probe_sources': {name: sha(HERE / name) for name in ['pending-timing.js', 'standalone.html']}}
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
