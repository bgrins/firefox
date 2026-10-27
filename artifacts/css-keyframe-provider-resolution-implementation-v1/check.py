import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
pre = read(HERE / "PREIMAGES.json")
post = read(HERE / "POSTIMAGES.json")
for name, value in pre.items():
    assert sha(HERE / "original" / name) == value
for name, value in post.items():
    assert sha(HERE / "candidate" / name) == value
for name, value in read(HERE / "SUPPORT-PINS.json").items():
    assert sha(HERE / "support" / name) == value
for name, value in read(HERE / "REFERENCES.json").items():
    assert sha(HERE.parents[1] / name) == value

def source(name, directory="candidate"):
    return (HERE / directory / name).read_text()

glue = "servo/ports/geckolib/glue.rs"
s = source(glue)
start = s.index('#[unsafe(no_mangle)]\npub extern "C" fn Servo_KeyframeEndpoint_ResolveRegistered(')
end = s.index('#[unsafe(no_mangle)]\npub extern "C" fn Servo_GetAnimationValues(', start)
assert s[:start] + s[end:] == source(glue, "original")
assert 'create_context_for_animation(' in s[start:end]
assert 'Some(providers.custom_properties().clone())' in s[start:end]
assert 'endpoint.resolve_registered(&data.stylist, context, &mut tracker)' in s[start:end]
assert 'Strong::null()' in s[start:end] and '*status = error;' in s[start:end]
endpoint = source("servo/components/style/keyframe_endpoint.rs")
assert 'mut context: crate::values::computed::Context' in endpoint
assert 'substitute_references_if_needed_and_apply(' in endpoint
assert 'handle_invalid_at_computed_value_time(' in endpoint
assert 'NeedsCascadeSelection' in endpoint and 'UnsupportedDeclaration' in endpoint
assert 'mFromValue' not in endpoint and 'mToValue' not in endpoint
cascade = source("servo/components/style/properties/cascade.rs")
a = cascade.index('    /// Prepare a retained custom endpoint')
b = cascade.index('    /// Resolves the cascaded custom properties', a)
assert cascade[:a] + cascade[b:] == source("servo/components/style/properties/cascade.rs", "original")
assert 'finish_cascade_custom_properties' not in cascade[a:b]
selection = read(HERE / 'SELECTION.json')
cpp = source('layout/style/test/gtest/TestKeyframePresentation.cpp')
for name in selection['gtest']:
    suite, test = name.split('.')
    assert f'TEST_F({suite}, {test})' in cpp
assert 'values.Clear();' in cpp and 'keyframes.Clear();' in cpp
assert 'StyleEndpointResolutionStatus::NotRegisteredCustomProperty, status' in cpp
with tempfile.TemporaryDirectory(prefix='provider-resolver-static-') as directory:
    scratch = Path(directory)
    for name in pre:
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / 'original' / name, target)
    for args in [['--check'], []]:
        subprocess.run(['git', 'apply', *args, str(HERE / 'full.patch')], cwd=scratch, check=True, capture_output=True)
    assert {name: sha(scratch / name) for name in post} == post
    subprocess.run(['git', 'apply', '-R', str(HERE / 'full.patch')], cwd=scratch, check=True, capture_output=True)
    assert {name: sha(scratch / name) for name in pre} == pre
    assert all(not (scratch / name).exists() for name in post.keys() - pre.keys())
    html = source('testing/web-platform/tests/' + selection['wpt'])
    script = html.split('<script>')[1].split('</script>')[0]
    probe = scratch / 'syntax.js'
    probe.write_text('const vm = require("node:vm"); const names = [];\n' +
                     'vm.runInNewContext(' + json.dumps(script) + ', {promise_test: (_, name) => names.push(name)});\n' +
                     'process.stdout.write(JSON.stringify(names));\n')
    result = subprocess.run(['node', str(probe)], check=True, capture_output=True, text=True)
    assert json.loads(result.stdout) == selection['ordered_names']
print(json.dumps({'status': 'PROVIDER_ENDPOINT_RESOLVER_STATIC_PASS',
                  'forward_reverse_exact': True, 'native_paths': 3, 'test_paths': 2,
                  'host_tests_prepared': 2, 'wpt_cases_inertly_registered': 4,
                  'existing_composition_and_keyframe_glue_unchanged': True,
                  'producer_enabled': False, 'native_compile_or_tests_run': False,
                  'live_mutation': False}, indent=2))
