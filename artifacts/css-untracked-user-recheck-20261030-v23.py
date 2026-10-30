import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / 'artifacts/css-untracked-user-recheck-20261030-v22.json'
BATCH = ROOT / 'artifacts/css-completed-publication-batch-v2/RESULT.json'
OUTPUT = ROOT / 'artifacts/css-untracked-user-recheck-20261030-v23.json'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def git(*args, cwd=ROOT):
    return subprocess.check_output(GIT + list(args), cwd=cwd, env=ENV)


def paths(body):
    return [name.decode() for name in body.split(b'\0') if name]


def index_hash(directory):
    path = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index', cwd=directory).decode().strip())
    return sha(path.read_bytes()) if path.exists() else None


def main():
    assert BATCH.exists(), 'Publication batch has no completed result; do not capture final audit yet'
    batch_body = BATCH.read_bytes()
    batch = json.loads(batch_body)
    assert batch['all_four_signed_publications_complete'] is True
    reference_body = REFERENCE.read_bytes()
    assert sha(reference_body) == 'e91be783247276319d0a78d4317d31160d6438451ea3034c93b05856cd1df417'
    prior = json.loads(reference_body)
    metadata_path = ROOT / prior['unrelated_metadata_reference']
    metadata_body = metadata_path.read_bytes()
    assert sha(metadata_body) == 'fed7f9b09747e610981a3d637d8bbb49fd2b52f5f4739b67c76476f242f802bb'
    metadata = json.loads(metadata_body)
    assert len(prior['project_files']) == 68 and len(metadata) == 495
    expected = {r['path'] for r in prior['project_files']} | {r['path'] for r in metadata}
    assert len(expected) == prior['untracked_count'] == 563
    before = index_hash(ROOT)
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == batch['commits']['image'], 'Capture before final research checkpoint'
    untracked = set(paths(git('ls-files', '--others', '--exclude-standard', '-z')))
    result = copy.deepcopy(prior)
    result.update(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), head=head,
                  reference_audit=str(REFERENCE.relative_to(ROOT)), reference_sha256=sha(reference_body),
                  untracked_count=len(untracked), unexpected_paths=sorted(untracked - expected),
                  missing_paths=sorted(expected - untracked), project_files=[])
    for old in prior['project_files']:
        path = ROOT / old['path']
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode), old['path']
        digest = sha(path.read_bytes())
        committed = sha(git('show', head + ':' + old['committed_recovery']))
        result['project_files'].append(dict(old, sha256=digest, committed_sha256=committed,
                                           matches=digest == committed == old['sha256']))
    mismatches = []
    for old in metadata:
        try:
            info = (ROOT / old['path']).lstat()
            kind = 'symlink' if stat.S_ISLNK(info.st_mode) else 'file' if stat.S_ISREG(info.st_mode) else 'other'
            actual = {'path': old['path'], 'bytes': info.st_size, 'identity': [info.st_dev, info.st_ino],
                      'kind': kind, 'mode': stat.S_IMODE(info.st_mode)}
        except FileNotFoundError:
            actual = None
        if actual != old:
            mismatches.append({'expected': old, 'observed': actual})
    result['project_hashes_match_committed_recovery'] = all(r['matches'] for r in result['project_files'])
    result['unrelated_metadata_mismatches'] = mismatches
    result['unrelated_metadata_sha256'] = sha(metadata_body)
    result['unrelated_contents_read'] = False
    result['staged_paths'] = paths(git('diff', '--cached', '--name-only', '-z'))
    result['tracked_modified_paths'] = paths(git('diff', '--name-only', '-z'))
    result['native_modified_paths'] = [name for name in result['tracked_modified_paths'] if not name.startswith('artifacts/')]
    nested = ROOT / 'artifacts/css-spec-lean'
    nested_index_before = index_hash(nested)
    nested_head = git('rev-parse', 'HEAD', cwd=nested).decode().strip()
    nested_status = git('status', '--porcelain=v1', '-z', '--untracked-files=all', cwd=nested)
    nested_entries = paths(nested_status)
    result['nested_css_spec_lean'] = {'head': nested_head, 'status_entries': nested_entries,
                                    'status_sha256': sha(nested_status), 'clean': not nested_status,
                                    'tracked_clean': all(entry.startswith('?? ') for entry in nested_entries),
                                    'known_metadata_only': nested_entries == ['?? .DS_Store'],
                                    'status_expected': nested_entries in ([], ['?? .DS_Store']),
                                    'head_matches_prior': nested_head == '162b20fb7c53a0ab89b20875a965baee98fb66bb',
                                    'raw_index_unchanged': nested_index_before == index_hash(nested)}
    result['raw_index_unchanged'] = before == index_hash(ROOT)
    result['head_unchanged_during_audit'] = head == git('rev-parse', 'HEAD').decode().strip()
    result['untracked_set_stable_during_audit'] = untracked == set(paths(git('ls-files', '--others', '--exclude-standard', '-z')))
    result['publication_batch'] = {'path': str(BATCH.relative_to(ROOT)), 'sha256': sha(batch_body), 'commits': batch['commits']}
    assert REFERENCE.read_bytes() == reference_body and metadata_path.read_bytes() == metadata_body and BATCH.read_bytes() == batch_body
    result['verified'] = all((not result['unexpected_paths'], not result['missing_paths'],
        result['project_hashes_match_committed_recovery'], not mismatches,
        not result['staged_paths'], not result['tracked_modified_paths'],
        result['nested_css_spec_lean']['tracked_clean'], result['nested_css_spec_lean']['status_expected'],
        result['nested_css_spec_lean']['head_matches_prior'], result['nested_css_spec_lean']['raw_index_unchanged'],
        result['raw_index_unchanged'], result['head_unchanged_during_audit'], result['untracked_set_stable_during_audit']))
    with OUTPUT.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(OUTPUT.relative_to(ROOT)), 'sha256': sha(OUTPUT.read_bytes()),
                      'verified': result['verified'], 'untracked': len(untracked), 'project': 68,
                      'unrelated': 495, 'nested_clean': result['nested_css_spec_lean']['clean'],
                      'nested_known_metadata_only': result['nested_css_spec_lean']['known_metadata_only']}))
    assert result['verified'], 'Audit retained mismatches; root review required'


if __name__ == '__main__':
    main()
