import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
assert args.output.is_absolute() and not args.output.exists()
here = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = here / 'FILES.json'
if manifest.exists():
    for name, digest in json.loads(manifest.read_text()).items():
        assert sha(here / name) == digest, name
pre = json.loads((here / 'PREIMAGES.json').read_text())
post = json.loads((here / 'POSTIMAGES.json').read_text())
assert pre.keys() == post.keys() and len(pre) == 4
for side, expected in [('original', pre), ('candidate', post)]:
    for name, digest in expected.items():
        assert sha(here / side / name) == digest

def body(side, name):
    return (here / side / name).read_text()

endpoint = 'servo/components/style/keyframe_endpoint.rs'
original = body('original', endpoint)
candidate = body('candidate', endpoint)
old_resolver = original[original.index('impl KeyframeEndpoint {\n    /// Resolve'):original.index('impl MallocSizeOf')]
assert old_resolver in candidate
glue = 'servo/ports/geckolib/glue.rs'
old_glue = body('original', glue)
start = old_glue.index('#[unsafe(no_mangle)]\npub extern "C" fn Servo_KeyframeEndpoint_ResolveRegistered(')
end = old_glue.index('\n#[unsafe(no_mangle)]', start + 20)
assert old_glue[start:end] in body('candidate', glue)
cpp = 'layout/style/test/gtest/TestKeyframePresentation.cpp'
assert body('candidate', cpp).startswith(body('original', cpp).rsplit('}  // namespace', 1)[0].rstrip())
assert body('candidate', cpp).count('RetainedEndpointProviderDemand') == 1
custom = body('candidate', 'servo/components/style/custom_properties.rs')
var = custom[custom.index('fn substitute_one_reference'):]
assert var.index('names.contains(&reference.name)') < var.index('substitution_functions.get_var(')
assert 'Err(error @ SubstitutionError::Demand(_)) => return Err(error)' in var
assert var.index('if let Some(s) = substitution') < var.index('let Some(ref fallback)')
assert 'Err(SubstitutionError::Demand(demand)) => return Err(demand)' in custom
assert 'EndpointDemand::AttributePreparation' in candidate

args.output.mkdir()
receipts = []
with tempfile.TemporaryDirectory(prefix='endpoint-demand-transport-') as tmp:
    tree = Path(tmp) / 'tree'
    shutil.copytree(here / 'original', tree)
    for phase, reverse, expected in [('forward', False, post), ('reverse', True, pre)]:
        command = ['patch', '--batch', '-p1'] + (['-R'] if reverse else [])
        run = subprocess.run(command, cwd=tree, input=(here / 'native.patch').read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (args.output / (phase + '.log')).write_bytes(run.stdout)
        assert run.returncode == 0
        assert {name: sha(tree / name) for name in expected} == expected
        receipts.append({'command': command, 'exit_code': run.returncode})
assert not Path(tmp).exists()
(args.output / 'CHECK.json').write_text(json.dumps({
    'status': 'DEMAND_SUBSTITUTION_SOURCE_TRANSPORT_PASS',
    'receipts': receipts,
    'old_resolver_and_public_ffi_exact': True,
    'existing_presentation_tests_exact': True,
    'ordinary_scc_file_untouched': True,
    'native_compiled': False,
    'presentation_test_executed': False,
    'scratch_removed': True,
}, indent=2) + '\n')
