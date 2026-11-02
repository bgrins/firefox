import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
assert not any(ENV.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
commands = []


def git(*args, data=None):
    commands.append(GIT + list(args))
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV, input=data)


def objects(specs):
    assert all('\n' not in value for value in specs)
    output = git('cat-file', '--batch', data=('\n'.join(specs) + '\n').encode())
    result, position = {}, 0
    for spec in specs:
        end = output.index(b'\n', position)
        oid, kind, size = output[position:end].decode().split()
        assert kind == 'blob'
        start = end + 1
        position = start + int(size)
        assert output[position:position+1] == b'\n'
        result[spec] = (oid, output[start:position])
        position += 1
    assert position == len(output)
    return result


sha = lambda data: hashlib.sha256(data).hexdigest()
head = git('rev-parse', 'HEAD').decode().strip()
scope = ['testing/web-platform/tests', 'testing/web-platform/mozilla/tests']
inventory = git('ls-files', '--others', '--exclude-standard', '-z', '--', *scope)
untracked = sorted(x.decode() for x in inventory.split(b'\0') if x)
triage_path = ROOT / 'artifacts/css-untracked-wpt-triage-20261030-v1/INVENTORY.json'
triage = json.loads(triage_path.read_bytes())
previous = {row['path']: row for row in triage['files']}
assert set(untracked) <= previous.keys(), set(untracked) - previous.keys()
recovery = triage['recovery_commit']
git('merge-base', '--is-ancestor', recovery, head)
adopted = sorted(previous.keys() - set(untracked))
expected_adopted = json.loads((ROOT / 'artifacts/css-language-publication-untracked-audit-v1.json').read_bytes())['adopted_wpts_tracked']
assert adopted == sorted(expected_adopted)
accepted_commits = sorted({association['commit'] for row in triage['files'] for association in row['accepted_fix_associations']})
for commit in accepted_commits:
    git('merge-base', '--is-ancestor', commit, head)
landed = sorted({path for row in triage['files'] for association in row['accepted_fix_associations'] for path in association['landed_test_paths']})
specs = [recovery + ':' + previous[name]['committed_recovery'] for name in untracked]
specs += [head + ':' + name for name in landed + adopted]
blobs = objects(list(dict.fromkeys(specs)))
hyphen = {'hyphenate-limit-chars-dynamic.html', 'hyphenate-limit-chars-inline-ownership.html', 'hyphenate-limit-chars-pseudo-ownership.html'}
superseded = {'declaration-recovery-nesting-limit-padding.html', 'declaration-recovery-nesting-limit-width.html'}
rows = []
for name in untracked:
    prior = previous[name]
    file = ROOT / name
    assert file.is_file() and not file.is_symlink()
    body = file.read_bytes()
    oid, archived = blobs[recovery + ':' + prior['committed_recovery']]
    assert body == archived and sha(body) == prior['sha256'] and oid == prior['recovery_git_blob']
    assert (ROOT / prior['committed_recovery']).read_bytes() == archived
    matches = [path for path in landed if blobs[head + ':' + path][1] == body]
    basename = Path(name).name
    if basename in hyphen:
        category = 'pending hyphenation adoption'
        action = 'Keep at the WPT path for the active validation/publication lane; adopt the exact file only with the validated native fix.'
    elif basename in superseded:
        category = 'superseded exploratory variant'
        action = 'Recommend removing only this untracked working copy after active consumers finish; exact recovery remains committed and the landed combined test covers its cases.'
    elif prior['category'] == 'completed-fix-associated probe/control':
        category = 'completed-fix broader or historical control'
        action = 'Keep the committed archive; consider a scoped test-only promotion for useful extra coverage. Archive-only working-tree cleanup is possible after consumer review, but this audit does not establish full semantic redundancy.'
    elif prior['category'].startswith('passing negative'):
        category = 'passing preservation control'
        action = 'Retain as an archived negative/control; do not count it as a missing fix or blindly add it as a new conformance regression.'
    elif prior['category'].startswith('unresolved'):
        category = 'unresolved rejected or withdrawn lead'
        action = 'Retain archived diagnostic and oracle limitations; do not promote the rejected implementation or delete evidence merely because an old candidate passed a subset.'
    else:
        category = 'other pending candidate or useful control'
        action = 'Retain while the candidate is unresolved; use the pinned per-file remaining work before any native or test-only adoption.'
    rows.append({'path':name,'bytes':len(body),'sha256':sha(body),'recovery_commit':recovery,'recovery_path':prior['committed_recovery'],'recovery_blob':oid,'recovery_exact':True,'byte_identical_associated_landed_tests':matches,'category':category,'recommendation':action,'purpose':prior['purpose'],'prior_evidence_summary':prior['evidence_summary'],'remaining_from_prior_review':prior['remaining'],'accepted_fix_associations':prior['accepted_fix_associations']})
assert not any(row['byte_identical_associated_landed_tests'] for row in rows)
landed_hashes = {path: sha(blobs[head+':'+path][1]) for path in landed}
reference_paths = ['artifacts/css-untracked-wpt-triage-20261030-v1/FILES.json', str(triage_path.relative_to(ROOT)), 'artifacts/css-language-publication-untracked-audit-v1.json', 'artifacts/css-branch-work-readout-20261030-v17/FILES.json']
reference_blobs = objects([head + ':' + path for path in reference_paths])
references = {}
for path in reference_paths:
    body = (ROOT/path).read_bytes()
    assert body == reference_blobs[head+':'+path][1]
    references[path] = sha(body)
assert git('rev-parse', 'HEAD').decode().strip() == head
assert git('ls-files', '--others', '--exclude-standard', '-z', '--', *scope) == inventory
result = {'head':head,'inventory_scope':scope,'untracked_wpt_files':len(rows),'bytes':sum(x['bytes'] for x in rows),'categories':dict(collections.Counter(x['category'] for x in rows)),'recovery_commit':recovery,'recovery_ancestor_verified':True,'all_working_bodies_equal_committed_recovery':True,'exact_associated_landed_duplicates':0,'accepted_association_commits_verified':accepted_commits,'newly_adopted_since_53_file_triage':adopted,'unrelated_495_contents_read':False,'deletions':False,'native_or_index_mutations':False,'classification_is_not_new_browser_evidence':True,'references':references,'associated_landed_test_hashes':landed_hashes,'rows':rows,'commands':commands}
(HERE/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('rows','commands','references','associated_landed_test_hashes','accepted_association_commits_verified')}))
