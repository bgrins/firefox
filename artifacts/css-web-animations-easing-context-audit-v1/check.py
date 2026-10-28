from pathlib import Path
import hashlib
import json
import subprocess
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
for name,digest in json.loads((P/'REFERENCES.json').read_text()).items():
    f=ROOT/name
    assert sha(f.read_bytes())==digest
    for n,h in json.loads(f.read_text()).items():
        assert sha((f.parent/n).read_bytes())==h
pins=json.loads((P/'SOURCE-PINS.json').read_text())
ex=json.loads((P/'SOURCE-EXCERPTS.json').read_text())
sources={}
for name,h in pins['paths'].items():
    b=subprocess.check_output(['git','show',pins['revision']+':'+name],cwd=ROOT)
    assert sha(b)==h
    sources[name]=b.decode()
    for e in ex[name]:assert e['text'] in sources[name]
glue=sources['servo/ports/geckolib/glue.rs']
a=glue.index('pub extern "C" fn Servo_ParseEasing')
body=glue[a:glue.index('\n#[unsafe(no_mangle)]',a)]
assert 'specified.to_computed_value_without_context()' in body
assert 'Context' not in body and 'Document' not in body
roster=sources['testing/web-platform/tests/web-animations/resources/easing-tests.js']
assert 'calc(' not in roster and 'sign(' not in roster
assert 'new KeyframeEffect(null,' in sources['testing/web-platform/tests/web-animations/interfaces/KeyframeEffect/constructor.html']
print(json.dumps({'status':'SOURCE_TRACE_CHECK_PASS','historical_sources':len(sources),'historical_revision':pins['revision'],'default_style_mandate':'NOT_ESTABLISHED','blanket_contextual_rejection_mandate':'NOT_ESTABLISHED','complete_WA_context_policy':'INCONCLUSIVE','fix120_installation':'HOLD','live_native_index_binary_reads':False,'browser_or_build':False},indent=2))
