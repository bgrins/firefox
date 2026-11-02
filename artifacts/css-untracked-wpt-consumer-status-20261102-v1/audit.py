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
head = git('rev-parse','HEAD').decode().strip()
assert head == '51b900ed6b003702c79e8aafd77cddac614597ee'
scope=['testing/web-platform/tests','testing/web-platform/mozilla/tests']
inventory=git('ls-files','--others','--exclude-standard','-z','--',*scope)
paths=sorted(x.decode() for x in inventory.split(b'\0') if x)
prior_path=ROOT/'artifacts/css-untracked-wpt-current-audit-20261102-v1/AUDIT.json'
cleanup_path=ROOT/'artifacts/css-untracked-wpt-superseded-cleanup-root-20261102-v1.json'
publication_path=ROOT/'artifacts/css-hyphenation-ownership-publication-commit-terminal-v2.json'
prior=json.loads(prior_path.read_bytes());previous={r['path']:r for r in prior['rows']}
cleanup=json.loads(cleanup_path.read_bytes());publication=json.loads(publication_path.read_bytes())
deleted={r['path'] for r in cleanup['deleted']}
adopted={n for n in publication['exact_files'] if n.startswith('testing/web-platform/')}
assert len(deleted)==2 and len(adopted)==3 and len(paths)==45
assert set(paths)==set(previous)-deleted-adopted==set(publication['untracked_wpt'])
recovery=prior['recovery_commit'];git('merge-base','--is-ancestor',recovery,head)
blobs=objects([recovery+':'+previous[n]['recovery_path'] for n in paths])
rows=[]
for name in paths:
    old=previous[name];f=ROOT/name;assert f.is_file() and not f.is_symlink()
    stat=f.stat();body=f.read_bytes();oid,archive=blobs[recovery+':'+old['recovery_path']]
    assert body==archive and sha(body)==old['sha256'] and oid==old['recovery_blob']
    row={k:old[k] for k in ('path','bytes','sha256','recovery_commit','recovery_path','recovery_blob','category','purpose','accepted_fix_associations')}
    row['identity']=[stat.st_dev,stat.st_ino];rows.append(row)
consumer_files = [
 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json',
 'artifacts/css-continuation-roadmap-20261102-v132/PLAN.md',
 'artifacts/css-continuation-roadmap-20261102-v132/STATUS.json',
 'artifacts/css-font-metric-selected-reference-next-step-v1/REPORT.md',
 'artifacts/css-font-metric-synthesis-native-typecheck-v4/POLICY.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v4/TYPECHECK.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v4/SOURCE-ROLES.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-runtime-2/candidate-check/COMMAND.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v5/POLICY.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v5/TYPECHECK.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v5/BROWSER-INPUTS.json',
 'artifacts/css-font-metric-synthesis-native-typecheck-v5/BROWSER-FOLLOWUP.md',
 'artifacts/css-registered-font-metric-demand-probe-v2/INPUTS.json',
 'artifacts/css-font-metric-phase-probe-v1/INPUTS.json',
 'artifacts/css-appearance-typed-attr-scheduling-probe-v1/INPUTS.json',
]
fixed_files=[prior_path,cleanup_path,publication_path]
fixed_blobs=objects([head+':'+str(f.relative_to(ROOT)) for f in fixed_files])
assert all(f.read_bytes()==fixed_blobs[head+':'+str(f.relative_to(ROOT))][1] for f in fixed_files)
references={str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in fixed_files}
observed_consumer_inputs={}
def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for key,child in value.items():yield key;yield from strings(child)
    elif isinstance(value,list):
        for child in value:yield from strings(child)
consumers={}
for name in consumer_files:
    body=(ROOT/name).read_bytes();observed_consumer_inputs[name]=sha(body)
    consumers[name]=(set(strings(json.loads(body))) if name.endswith('.json') else None,body.decode())
for row in rows:
    path=row['path'];url='/'+path.split('testing/web-platform/tests/',1)[1]
    row['direct_input_matches']=[];row['prose_or_archive_mentions']=[]
    for name,(values,text) in consumers.items():
        if values is not None and ({path,str(ROOT/path),url}&values):row['direct_input_matches'].append(name)
        elif path in text or Path(path).name in text:row['prose_or_archive_mentions'].append(name)
    row['future_cleanup_candidate']=row['category']=='completed-fix broader or historical control' and not row['direct_input_matches']
assert git('rev-parse','HEAD').decode().strip()==head
assert git('ls-files','--others','--exclude-standard','-z','--',*scope)==inventory
result={'head':head,'untracked_wpt_files':45,'bytes':sum(r['bytes'] for r in rows),'categories':dict(collections.Counter(r['category'] for r in rows)),'recovery_commit':recovery,'all_live_bodies_equal_committed_recovery':True,'transition':{'prior':50,'superseded_removed':sorted(deleted),'adopted':sorted(adopted),'current':45},'consumer_scope':consumer_files,'consumer_scope_is_bounded_not_global':True,'cleanup_deferred_until_after_current_typecheck_and_fresh_admission':True,'unrelated_contents_read':False,'deletions':False,'native_or_index_mutations':False,'fixed_references':references,'observed_consumer_input_hashes':observed_consumer_inputs,'rows':rows,'commands':commands}
(HERE/'STATUS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('fixed_references','observed_consumer_input_hashes','rows','commands','consumer_scope','transition')}))
print(json.dumps({'completed_control_candidates':sum(r['future_cleanup_candidate'] for r in rows),'completed_control_bytes':sum(r['bytes'] for r in rows if r['future_cleanup_candidate']),'directly_pinned_pending_or_unresolved_files':sum(bool(r['direct_input_matches']) for r in rows)}))
