import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'artifacts/css-svg-length-conversion-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

seal = '1af99adde5bdae8c0daeb96952b7eed95e39e351fe2e1d037b2f34f79e7103b1'
assert sha(RUN / 'FILES.json') == seal
manifest = read(RUN / 'FILES.json')
assert len(manifest) == 67
for name, digest in manifest.items():
    assert sha(RUN / name) == digest, name
c, state, receipt = [read(RUN / n) for n in ('CONFIG.json', 'STATE.json', 'ROOT-FINAL-CHECK.json')]
before, final = [read(RUN / n) for n in ('BEFORE.json', 'FINAL.json')]
assert state['status'] == 'terminal' and state['restored'] is True
assert state['restore_build_exit'] == 0 and state['recovery_errors'] == [] and 'failure' not in state
assert state['paired_preservation_passed'] is True and state['lint_exit'] == 0
assert receipt['status'] == 'RESTORED_VERIFIED' and receipt['session'] == 62365 and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(RUN / 'STATE.json') == 'dc44c5938f8ff4d604b5e4ef1552d84de02ad8a5df77385c28441316d072895f'
assert receipt['final_sha256'] == sha(RUN / 'FINAL.json') == '3692cb3bc699c55ab3695f81d614efe1391196ccaafa817ce30ecdc33e1ec8e5'
assert final == before and final['sources'] == c['source_pins']
assert set(state['restored_paths']) == set(c['sources']) and len(state['restored_paths']) == 29
for name in c['sources']:
    assert sha(RUN / 'original' / name) == before['sources'][name]
assert state['restore_build_exit'] == read(RUN / 'fixture-lint.json')['exit'] == 0
assert state['restored_binary_pins'] == receipt['restored_binary_pins']
assert read(RUN / 'FINAL-PINS.json') == {**read(RUN / 'RESOURCES.json'), **final['sources'], **state['restored_binary_pins']}
assert len(final['sources']) == receipt['source_count'] == 52
assert len(read(RUN / 'FINAL-PINS.json')) == receipt['pin_count'] == 366
assert receipt['normalization_paths'] == 29 and receipt['native_modified_paths'] == len(c['modified_native_paths']) == 27
assert receipt['staged_paths_preserved'] == 925 and receipt['installed_test_identities_preserved'] is True
identities = {}
for name in ('css-cssom-offset-scroll-install-runtime-v1', 'css-cssom-client-install-runtime-v1', 'css-hidden-svg-matrix-install-runtime-v1'):
    prior = ROOT / 'artifacts' / name
    installation = read(prior / 'INSTALLATION.json')
    m = read(prior / 'FILES.json')
    assert sha(prior / 'INSTALLATION.json') == m['INSTALLATION.json']
    test = installation['owned_test']
    identities[test] = installation['owned_test_identity']
    assert read(RUN / 'FINAL-PINS.json')[test] == installation['owned_test_sha256'] == c['existing_test_pins'][test]
assert receipt['installed_test_identities'] == identities
assert final['head'] == c['head'] == '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
assert final['index_diff_sha256'] == '3ecc566a1cb1a78aab07c4f272b627d59f7888dec4adf563274849a966047272'
assert final['index_entries_sha256'] == 'e52cf295947403cec7f6cba85bc15a6b539aaa5591df17101dfb5098e3747e21'
phase = read(HERE / 'PHASE-REVIEW.json')
for role in ('baseline', 'candidate'):
    for filename, key in (('raw.json', 'raw_sha256'), ('RUN.json', 'run_sha256')):
        assert sha(RUN / ('wpt-' + role) / filename) == phase[role][key]
errors = {role: (RUN / (role + '-build.log')).read_text().count("KeyError: 'export'") for role in ('baseline', 'candidate', 'restore')}
assert errors == {'baseline': 4, 'candidate': 4, 'restore': 4}
result = {'runtime_manifest_sha256': seal, 'authenticated_payloads': len(manifest),
          'terminal_restoration_verified': True, 'original_bodies': 29, 'guarded_sources': 52,
          'final_roles': 366, 'preserved_native_differences': 27, 'preserved_installed_wpt_identities': 3,
          'staged_paths_preserved': 925, 'restored_binary_pins': state['restored_binary_pins'],
          'successful_build_resource_monitor_keyerrors': errors,
          'recommendation': 'SCOPED_ACCEPTANCE', 'accepted_or_installed_by_reviewer': False,
          'standalone_patch_sha256': '3cc9b8edd8d70ff238197c866210869c0a31eaefe812b2b9f205ab4a0d6d315e'}
(HERE / 'FINAL-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
