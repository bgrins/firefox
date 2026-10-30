import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('capture', HERE / 'capture.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
row = {'kind': 'zoom-observation', 'initial': '0px', 'diagnosticOnly': True, 'phases': []}
for index, size in enumerate([20, 30]):
    row['phases'].append({'phase': index, 'value': '1em', 'samples': [f'{size}px'] * 4,
                         'expected': None, 'expectedFont': None, 'font': f'{size}px', 'line': '19px',
                         'family': 'monospace', 'writingMode': 'horizontal-tb', 'zoom': str(size),
                         'referenceFont': f'{size}px', 'referenceWidth': f'{size*2}px', 'size': size,
                         'keywordSupported': True, 'zoomSyntaxSupported': True})
checks = []
with tempfile.TemporaryDirectory(prefix='css-zoom-capture-', dir='/private/tmp') as scratch:
    scratch_path = Path(scratch)
    def setup(name):
        output = scratch_path / name
        tests = output / 'tests'
        page = tests / capture.PAGE[1:]
        page.parent.mkdir(parents=True)
        page.write_bytes((HERE / 'candidate.html').read_bytes())
        binding = capture.install(tests, output, 'original')
        directory = tests / '__research__/zoom'
        spec = importlib.util.spec_from_file_location('handler_' + name, directory / 'receive.py')
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
        payload = {k: binding[k] for k in ['version', 'nonce', 'role', 'page']}
        payload['row'] = copy.deepcopy(row)
        return output, directory, binding, handler, payload
    class Headers(dict):
        def set(self, key, value):
            self[key] = value
    def post(handler, payload, origin=b'http://web-platform.test:8000'):
        request = SimpleNamespace(method='POST', headers={b'Content-Type': b'application/json',
                                  b'Host': b'web-platform.test:8000', b'Origin': origin},
                                  body=json.dumps(payload).encode())
        response = SimpleNamespace(headers=Headers(), status=200)
        body = handler.main(request, response)
        return response.status, json.loads(body)
    events = [{'action':'test_status', 'test':capture.PAGE, 'subtest':capture.NAME, 'status':'PASS'},
              {'action':'test_end', 'test':capture.PAGE, 'status':'OK'}]
    output, directory, binding, handler, payload = setup('positive')
    assert post(handler, payload) == (200, {'accepted': True})
    assert json.loads((directory/'REQUEST.json').read_bytes()) == payload
    result = capture.review(output, events)
    assert result['row'] == row and result['target_correctness'] is None
    assert capture.replay(output, events) == result
    checks.append('exact handler POST -> persisted request -> independent replay')
    changed = copy.deepcopy(result)
    changed['role'] = 'candidate'
    changed['row']['phases'][0]['samples'] = ['0px'] * 4
    assert capture.compare(result, changed)['differences'][0]['field'] == 'samples'
    assert capture.compare(result, changed)['target_correctness'] is None
    checks.append('different target samples retained without numerical verdict')
    try:
        capture.compare(result, result)
        raise RuntimeError('same phase compared as before/after')
    except AssertionError:
        pass
    checks.append('same-phase comparison rejected')
    assert post(handler, payload)[0] == 400
    assert json.loads((directory/'REQUEST.json').read_bytes()) == payload
    assert (directory/'ERRORS.jsonl').exists()
    checks.append('duplicate rejected, original request preserved, marker retained')
    for name, mutate in [('nonce', lambda x:x.update(nonce='wrong')),
                         ('role', lambda x:x.update(role='candidate')),
                         ('page', lambda x:x.update(page='/wrong'))]:
        output, directory, binding, handler, payload = setup(name)
        mutate(payload)
        assert post(handler,payload)[0] == 400 and not (directory/'REQUEST.json').exists()
        checks.append(name + ' rejected')
    output, directory, binding, handler, payload = setup('origin')
    assert post(handler,payload,b'http://wrong.test')[0] == 400
    checks.append('origin rejected')
    output, directory, binding, handler, payload = setup('missing')
    try:
        capture.review(output,events)
        raise RuntimeError('missing request accepted')
    except FileNotFoundError:
        pass
    checks.append('missing capture rejected')
    for name, mutate in [('one_phase', lambda x:x['row']['phases'].pop()),
                         ('one_sample', lambda x:x['row']['phases'][0]['samples'].pop()),
                         ('numeric_oracle', lambda x:x['row']['phases'][0].update(expected='20px')),
                         ('nonstring', lambda x:x['row']['phases'][0].update(zoom=1)),
                         ('wrong_kind', lambda x:x['row'].update(kind='winning-variable'))]:
        payload = {k: binding[k] for k in ['version','nonce','role','page']}
        payload['row'] = copy.deepcopy(row)
        mutate(payload)
        try:
            capture.validate(payload,binding)
            raise RuntimeError(name + ' accepted')
        except AssertionError:
            pass
        checks.append(name + ' rejected')
    output, directory, binding, handler, payload = setup('failure_status')
    assert post(handler,payload)[0] == 200
    failed_events=copy.deepcopy(events);failed_events[0]['status']='FAIL'
    assert capture.review(output,failed_events)['test_status']['status']=='FAIL'
    checks.append('ordinary FAIL retained independently from complete capture')
    payload['row']['phases'][0]['zoom'] = ''
    assert capture.validate(payload, binding)['phases'][0]['zoom'] == ''
    checks.append('empty CSS serialization preserved without value oracle')
assert not scratch_path.exists()
subprocess.run(['node','--check',str(HERE/'record.js')],check=True)
program = r'''
const fs=require('fs'),vm=require('vm');
(async()=>{
let calls=[]; const row={kind:'zoom-observation',phases:[{samples:['x']}]};
const context=vm.createContext({window:{},location:{pathname:'/expected'},fetch:async(url,options)=>{
 calls.push({url,options});
 return {ok:true,json:async()=>calls.length===1?{nonce:'n',role:'original'}:{accepted:true}};
}});
vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),context);
await context.window.capturePrioritaryZoom(row);
if(calls.length!==2 || JSON.stringify(JSON.parse(calls[1].options.body).row)!==JSON.stringify(row))throw Error('row changed');
context.fetch=async()=>({ok:false});
let rejected=false;try{await context.window.capturePrioritaryZoom(row)}catch(e){rejected=true}
if(!rejected)throw Error('failure hidden');
console.log('bridge exact row; persistence/config failure rejects');
})().catch(e=>{console.error(e);process.exit(1)});
'''
subprocess.run(['node','-e',program,str(HERE/'record.js')],check=True)
result={'checks':checks,'scratch_removed':True,'bridge_vm':True,'browser_execution':False,
        'listening_server_execution':False,'native_build':False}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
