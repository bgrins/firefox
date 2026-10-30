import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'artifacts/css-contextual-duration-feedback-browser-runtime-2'
FIXTURE = ROOT / 'artifacts/css-contextual-duration-same-element-dependency-probe-v1'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(folder, seal):
    assert sha(folder / 'FILES.json') == seal
    manifest = json.loads((folder / 'FILES.json').read_text())
    for name, entry in manifest.items():
        path = folder / name
        assert path.is_relative_to(folder) and all(not part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(folder))
        assert path.is_file() and sha(path) == (entry if isinstance(entry, str) else entry['sha256'])
        if isinstance(entry, dict):
            assert len(path.read_bytes()) == entry['bytes']
    return len(manifest)


runtime_count = authenticate(RUNTIME, '44135eb8194ce2ef7fdae519d6bcd28c65c96975cf17099e54ed22654d24df0b')
fixture_count = authenticate(FIXTURE, '426ebe5d83ab29defa5d8387a21c4e329fb91c29b4c7bb6ed6f891785b540039')
roster = json.loads((FIXTURE / 'ROSTER.json').read_text())
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
rows = [event for event in events if event.get('action') == 'test_status']
endings = [event for event in events if event.get('action') == 'test_end']
expected = sorted((test, name) for test, names in roster['tests'].items() for name in names)
assert sorted((row['test'], row['subtest']) for row in rows) == expected
assert sorted(row['test'] for row in endings) == sorted(roster['tests'])
assert all(row['status'] == 'OK' for row in endings)
assert sum(e.get('action') == 'suite_start' for e in events) == 1
assert sum(e.get('action') == 'suite_end' for e in events) == 1
assert [row['status'] for row in rows] == ['FAIL', 'PASS']
assessment = {'complete': True,
              'callbacks': [{key: row.get(key) for key in ('test', 'subtest', 'status', 'message')} for row in rows],
              'endings': [{key: row.get(key) for key in ('test', 'status')} for row in endings]}
assert assessment == json.loads((RUNTIME / 'ASSESSMENT.json').read_text())
assert (RUNTIME / 'PRE.json').read_bytes() == (RUNTIME / 'POST.json').read_bytes()
result = json.loads((RUNTIME / 'RESULT.json').read_text())
assert result == {'complete_browser_evidence': True, 'error': None, 'exit': 1,
                  'native_fix_acceptance': False, 'state_preserved': True}
terminal = json.loads((RUNTIME / 'ROOT-TERMINAL.json').read_text())
assert (terminal['session_id'], terminal['terminal_chunk'], terminal['owner_exit'], terminal['wpt_exit']) == (55405, '658b02', 0, 1)
assert terminal['fixture_manifest_sha256'] == sha(FIXTURE / 'FILES.json')
assert terminal['raw_sha256'] == sha(RUNTIME / 'raw.jsonl')
assert terminal['runner_sha256'] == sha(RUNTIME / 'RUNNER.py')
assert json.loads((RUNTIME / 'CLEANUP.json').read_text())['owned_group_absent']
resources = json.loads((RUNTIME / 'TESTED-RESOURCES.json').read_text())
for name, digest in resources.items():
    assert sha(FIXTURE / 'tests' / name) == sha(RUNTIME / 'tests' / name) == digest
metadata = json.loads((RUNTIME / 'TESTED-METADATA.json').read_text())
for name, digest in metadata.items():
    original = FIXTURE / 'MANIFEST.json' if name == 'MANIFEST.json' else FIXTURE / 'meta' / name
    assert sha(original) == sha(RUNTIME / 'metadata' / name) == digest
assert sorted(p.name for p in (RUNTIME / 'records').iterdir()) == sorted(roster['records'])
handler = FIXTURE / 'tests/css/css-animations/duration-same-element-record.py'
namespace = {}
exec(compile(handler.read_text(), str(handler), 'exec'), namespace)
records = {}
for name in roster['records']:
    value = json.loads((RUNTIME / 'records' / name).read_text())
    assert value['run_id'] == 'css-duration-feedback-original-v2'
    namespace['validate']({key: value[key] for key in ('kind', 'observations')})
    assert name == value['kind'] + '.json'
    records[value['kind']] = value
message = rows[0]['message']
embedded = message.split('Acyclic same-element dependency; ', 1)[1].rsplit('}: first-read opacity', 1)[0] + '}'
assert json.loads(embedded) == records['same-element-acyclic']['observations']
page = next(iter(roster['tests']))
source = (FIXTURE / 'tests' / page.lstrip('/')).read_text().split('<script>')[1].split('</script>')[0]
program = r'''
const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);
process.stdin.on('end',()=>{
 const v=JSON.parse(input),ok=x=>{if(!x)throw Error('assertion');};
 const c=vm.createContext({promise_test:()=>{},assert_true:ok,assert_equals:(a,b)=>ok(a===b),
  assert_approx_equals:(a,b,e)=>ok(Number.isFinite(a)&&Math.abs(a-b)<=e)});
 vm.runInContext(v.source,c);
 const a=v.records['same-element-acyclic'].observations,f=v.records['same-element-feedback'].observations;
 vm.runInContext('assertAcyclic',c)(a.literal,'literal');
 let rejected=false;try{vm.runInContext('assertAcyclic',c)(a.contextual,'contextual');}catch(_){rejected=true;}ok(rejected);
 vm.runInContext('assertLiteralFeedback',c)(f.literal500,500,32,'literal500');
 vm.runInContext('assertLiteralFeedback',c)(f.literal1000,1000,16,'literal1000');
 vm.runInContext('assertOwnership',c)(f.contextual,'contextual');
 process.stdout.write(JSON.stringify({literal_assertions_replayed:true,acyclic_assertions_reject:true,
  contextual_feedback_ownership_passes:true,dom_callbacks_executed:false}));
});
'''
assertions = json.loads(subprocess.run(['node', '-e', program], input=json.dumps({'source': source, 'records': records}),
                                      text=True, capture_output=True, check=True).stdout)
print(json.dumps({'runtime_files': runtime_count, 'fixture_files': fixture_count,
                  'callbacks': assessment['callbacks'], 'endings': assessment['endings'],
                  'saved_state_equal': True, 'literal_replay': assertions, 'records': records,
                  'native_acceptance': False}, indent=2))
