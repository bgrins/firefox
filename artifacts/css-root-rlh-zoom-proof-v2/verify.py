import argparse
import hashlib
import json
from pathlib import Path
import sys
BASE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(source_only, expected_freeze):
    if expected_freeze:
        assert sha(BASE / 'FREEZE.json') == expected_freeze, 'freeze identity mismatch'
    freeze = json.loads((BASE / 'FREEZE.json').read_text())
    assert sha(BASE / 'SOURCE-MANIFEST.json') == freeze['sourceManifest']
    assert sha(BASE / 'FILES.json') == freeze['filesManifest']
    source = json.loads((BASE / 'SOURCE-MANIFEST.json').read_text())
    files = json.loads((BASE / 'FILES.json').read_text())
    for name, digest in source.items():
        assert files[name] == digest
    actual = set()
    for path in BASE.rglob('*'):
        assert not path.is_symlink(), str(path)
        if path.is_file():
            actual.add(path.relative_to(BASE).as_posix())
    allowed = set(files) | {'FREEZE.json', 'FILES.json'}
    assert actual <= allowed, ('unlisted input', sorted(actual - allowed))
    expected = source if source_only else files
    if not source_only:
        assert actual == allowed, ('missing files', sorted(allowed - actual))
    for name, digest in expected.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts and str(relative) == name
        assert sha(BASE / relative) == digest, ('input authentication failed', name)
    assert all(name in source for name in files if not name.startswith('results/') and name.endswith(('.py', '.lean', '.rs', '.cpp', '.h')))
    return freeze, dict(authenticated=len(expected), sourceOnly=source_only)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--expected-freeze')
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--lean', type=Path)
    args = parser.parse_args()
    freeze, receipt = authenticate(args.source_only, args.expected_freeze)
    sys.dont_write_bytecode = True
    if args.replay:
        assert args.lean is not None
        sys.path.insert(0, str(BASE))
        import joined_replay
        replay = joined_replay.run(args.replay, args.lean.resolve())
        assert replay['semanticResult'] == freeze['semanticResult']
        receipt['replay'] = replay
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
