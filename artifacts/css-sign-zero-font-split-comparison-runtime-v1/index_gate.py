import hashlib

def index_state(wpt):
    expected = wpt.CONFIG['index_expectations']
    wpt.need(isinstance(expected, dict), 'unbound current index')
    paths = wpt.git('diff', '--cached', '--name-only').decode().splitlines()
    wpt.need(paths == expected['staged_paths'] and set(paths) == set(expected['staged_payload_sha256']), 'staged roster')
    wpt.need(wpt.git('rev-parse', 'HEAD').decode().strip() == expected['head'] == wpt.CONFIG['head'], 'execution HEAD')
    wpt.need(hashlib.sha256(wpt.git('diff', '--cached', '--binary')).hexdigest() == expected['index_diff_sha256'], 'index diff')
    wpt.need(hashlib.sha256(wpt.git('ls-files', '--stage', '-z')).hexdigest() == expected['index_entries_sha256'], 'index entries')
    for name, digest in expected['staged_payload_sha256'].items():
        wpt.need(name.startswith('artifacts/') and hashlib.sha256(wpt.git('show', ':' + name)).hexdigest() == digest, 'staged research payload')
