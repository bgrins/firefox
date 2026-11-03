import ast, copy, difflib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('variation_archive_run', HERE / 'run.py')
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
policy = json.loads((HERE / 'POLICY-original.json').read_text())
assert policy['execution_enabled'] is False
assert policy['required_completed_owner'] == 'artifacts/css-explicit-taint-combined-native-candidate-browser-runtime-v1'
assert policy['source_role'] == 'archived-original' and policy['archive_role'] == 'original'
try:
    run.run(policy)
except AssertionError as exc:
    assert str(exc) == 'disabled preparation'
else:
    raise AssertionError('Disabled owner admitted')
run.pins()
parent = ROOT / 'artifacts/css-font-variation-archived-original-runner-v1'
assert (HERE / 'entry.py').read_bytes() == (parent / 'entry.py').read_bytes()
assert run.regular_files(HERE / 'support') == run.regular_files(parent / 'support')
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff((parent / 'run.py').read_text().splitlines(True), (HERE / 'run.py').read_text().splitlines(True), fromfile=str((parent / 'run.py').relative_to(ROOT)), tofile=str((HERE / 'run.py').relative_to(ROOT))))
def functions(path):
    s = path.read_text()
    return {n.name: ast.get_source_segment(s, n) for n in ast.parse(s).body if isinstance(n, ast.FunctionDef)}
old, new = functions(parent / 'run.py'), functions(HERE / 'run.py')
assert set(old) == set(new)
for name in old:
    if name != 'assess':
        assert old[name].replace("prefix='css-font-variation-'", "prefix='css-keyframe-font-units-'") == new[name], name
binding = policy['fixture_binding']; fixture = ROOT / binding['directory']
assert run.sha(fixture / 'FILES.json') == binding['manifest_sha256'] == 'bc7076009df8acddb197dd00675b8a9f62483d3e5ec11adb2e49e6864815e754'
inventory = json.loads((fixture / 'FILES.json').read_text())
for name, row in inventory.get('files',inventory).items(): assert run.sha(fixture / name) == (row if isinstance(row,str) else row['sha256'])
assert policy['settings']['metadata'] == {'mozilla': {}, 'portable': {}}
assert len(policy['settings']['resources']) == 3 and not any('pending/' in k for k in policy['settings']['resources'])
snapshot = json.loads((ROOT / policy['snapshot']).read_text())
assert run.sha(ROOT / policy['snapshot']) == policy['snapshot_sha256']
assert snapshot['source_role'] == 'original' and snapshot['application'] == policy['archive_application']
assert len(snapshot['files']) == policy['archive_files'] == 8326 and snapshot['native_sources'] == policy['native_sources']
assert run.sha(ROOT / snapshot['build_receipt']) == snapshot['build_receipt_sha256']
build = json.loads((ROOT / snapshot['build_receipt']).read_text())
assert build['native_sources'] == policy['native_sources']
assert build['application_metadata']['source_role'] == 'original'
assert build['application_metadata']['revision'] == policy['build_revision'] == 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
assert build['browser_build_performed'] and build['command_success'] and build['preservation_verified'] and build['error'] is None
if policy['pending_binding']:
    assert all(policy[key] is None for key in ('completed_runtime','prior_owner_terminal','prior_owner_audit','prior_audit_terminal'))
    enabled = copy.deepcopy(policy); enabled['execution_enabled'] = True
    try: run.run(enabled)
    except AssertionError: pass
    else: raise AssertionError('Pending restoration admitted')
else:
    runtime = ROOT / policy['completed_runtime']['directory']
    assert str(runtime.relative_to(ROOT)) == policy['required_completed_owner']
    assert run.sha(runtime/'FILES.json') == policy['completed_runtime']['manifest_sha256']
    frozen = json.loads((runtime/'FILES.json').read_text())
    for name,row in frozen.get('files',frozen).items(): assert run.sha(runtime/name) == (row if isinstance(row,str) else row['sha256'])
    expected_links = [f'candidate-wpt-{lane}/tests/tools' for lane in ('composition','controls','fallback','reparse')]
    assert frozen['verified_staging_tool_links'] == expected_links
    for name in expected_links:
        link = runtime/name
        assert link.is_symlink() and str(link.readlink()) == str(ROOT/'testing/web-platform/tests/tools')
    for key,name in [('prior_owner_terminal','ROOT-OWNER-TERMINAL.json'),('prior_owner_audit','ROOT-LIVE-RESTORATION.json'),('prior_audit_terminal','ROOT-AUDIT-TERMINAL.json')]:
        assert policy[key] == {'path':str((runtime/name).relative_to(ROOT)),'sha256':run.sha(runtime/name)}
    terminal = json.loads((runtime/'ROOT-OWNER-TERMINAL.json').read_text())
    audit = json.loads((runtime/'ROOT-LIVE-RESTORATION.json').read_text())
    at = json.loads((runtime/'ROOT-AUDIT-TERMINAL.json').read_text())
    assert terminal['terminal'] and terminal['exit'] in (0,1) and terminal['session'] == 97438
    assert at['terminal'] and at['exit'] == 0 and at['restoration_report_sha256'] == policy['prior_owner_audit']['sha256']
    assert audit['independent_live_restoration_verified'] and audit['owner_terminal'] == terminal
    assert audit['owner_result_sha256'] == terminal['result_sha256'] == run.sha(runtime/'RESULT.json')
roster = json.loads((ROOT / policy['roster']).read_text())
assert len(roster) == 1 and all(len(names) == 14 for names in roster.values())
inputs = json.loads((fixture/'INPUTS.json').read_text())
for name,row in inputs.items():
    assert policy['settings']['resources']['/'+name] == {'path':str((fixture/'tests'/name).relative_to(ROOT)),**row}
assert policy['settings']['manifests']['portable']['sha256'] == run.sha(fixture/'MANIFEST.json')
events = [{'action': 'suite_start'}]
for page, names in roster.items():
    events.append({'action':'test_start','test':page})
    events += [{'action':'test_status','test':page,'subtest':name,'status':'FAIL' if i<2 else 'PASS','expected':'PASS'} for i,name in enumerate(names)]
    events.append({'action':'test_end','test':page,'status':'OK'})
events.append({'action':'suite_end'})
assert run.assess(events,roster,1)['complete'] and run.assess(events,roster,1)['counts']=={'FAIL':2,'PASS':12}
all_pass=copy.deepcopy(events)
for row in all_pass:
    if row['action']=='test_status':row['status']='PASS'
assert run.assess(all_pass,roster,0)['all_14_pass']
negatives=[events[:-1],events[:2]+events[3:],events+[events[2]],events[:1]+events[2:],events+[{'action':'crash'}]]
for index,field,value in [(2,'subtest','wrong'),(-2,'status','CRASH'),(2,'status','TIMEOUT'),(2,'test','/wrong.html'),(-2,'test','/wrong-end.html')]:
    rows=copy.deepcopy(events);rows[index][field]=value;negatives.append(rows)
rows=copy.deepcopy(events);rows.insert(-1,copy.deepcopy(rows[-2]));negatives.append(rows)
rows=copy.deepcopy(events);rows.insert(1,rows.pop(2));negatives.append(rows)
assert all(not run.assess(rows,roster,1)['complete'] for rows in negatives)
assert not run.assess(events,roster,0)['complete'] and not run.assess(all_pass,roster,1)['complete']
scratch=Path(tempfile.mkdtemp(prefix='keyframe-font-unit-archive14-check-',dir='/private/tmp'))
result={'browser_execution':False,'archive_read':False,'native_operations':False,'saved_positive_streams':2,'saved_negative_streams':len(negatives)+2,'scratch':str(scratch),'pages':1,'callbacks':14,'unchanged_production_functions_except_assess':len(old)-1}
try:
    output=scratch/'stage';output.mkdir();run.prepare(output,policy)
    for url,record in policy['settings']['resources'].items():assert run.sha(output/'tests'/url.lstrip('/'))==record['sha256']
    command,env=run.command(output,scratch,policy,snapshot)
    assert './mach' not in command and not any(arg.startswith('--run-info='+str(ROOT/'objdir')) for arg in command)
    assert {arg.removeprefix('--include=') for arg in command if arg.startswith('--include=')}==set(roster)
    command.insert(3,'--check-args')
    process=subprocess.run(command,env=env,cwd=output,capture_output=True,text=True)
    result['argument_check']={'command':command,'exit':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
    assert process.returncode==0,(process.stdout,process.stderr)
    assert json.loads((output/'tests/config.json').read_text())['ports']=={name:['auto']*count for name,count in policy['settings']['server_protocols'].items()}
    assert (output/'run-info/mozinfo.json').read_bytes()==(HERE/'support/mozinfo.json').read_bytes()
    result.update(success=True,staged_files=len(run.regular_files(output)),disabled_gate_rejected=True,owner_terminal_pending=policy['pending_binding'],reference_count=len(json.loads((HERE/'REFERENCES.json').read_text())))
finally:
    shutil.rmtree(scratch);result['scratch_removed']=not scratch.exists()
    (HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
