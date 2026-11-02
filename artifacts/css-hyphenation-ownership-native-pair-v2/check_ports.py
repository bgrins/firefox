import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())


def load(name):
    spec = importlib.util.spec_from_file_location('port_check_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(policy):
    source = ROOT / 'artifacts/css-nowrap-native-pair-runtime-1'
    load('admission').authenticate(ROOT, policy['port_fixture_binding'])
    scratch = Path(tempfile.mkdtemp(prefix='css-hyphenation-port-check-', dir=ROOT / 'artifacts'))
    ports, assessor = load('port_comparison'), load('assess')
    assessments, events = {}, {}
    try:
        for role in ('original', 'candidate'):
            folder = scratch / (role + '-wpt-regression')
            saved = source / folder.name
            (folder / 'metadata').mkdir(parents=True)
            shutil.copyfile(saved / 'metadata/MANIFEST.json', folder / 'metadata/MANIFEST.json')
            (folder / 'wptrunner.ini').write_text('[manifest:upstream]\ntests = ' + str(folder / 'tests') + '\nmetadata = ' + str(folder / 'metadata') + '\nurl_base = /\nmanifest = ' + str(folder / 'metadata/MANIFEST.json') + '\n')
            (folder / 'COMMAND.json').write_text(json.dumps({'command': ['--config=' + str(folder / 'wptrunner.ini')]}))
            events[role] = [json.loads(line) for line in (saved / 'raw.jsonl').read_text().splitlines()]
            assessments[role] = read(saved / 'ASSESSMENT.json')
        targets = policy['wpt_lanes']['regression']['target_subtests']
        for row in events['candidate']:
            if row.get('action') == 'test_status' and row.get('subtest') in targets.get(row['test'], []) and row['status'] == 'FAIL':
                row['status'] = 'PASS'
                row.pop('expected', None)
                row.pop('message', None)

        def evaluate(streams):
            actual = copy.deepcopy(assessments)
            for role, rows in streams.items():
                (scratch / (role + '-wpt-regression') / 'raw.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))
                actual[role]['rows'] = [row for row in rows if row.get('action') == 'test_status']
                actual[role]['ends'] = [row for row in rows if row.get('action') == 'test_end']
            return ports.compare(ROOT, scratch, policy, actual['original'], actual['candidate'], assessor.signature)

        result = evaluate(events)
        assert result['derived_ownership_gate'] and result['preserved_signatures'] == 452
        for mutation in ('target-failure', 'control-failure-message', 'prior-pass-message', 'wrong-port-host'):
            changed = copy.deepcopy(events)
            rows = changed['candidate']
            if mutation == 'target-failure':
                row = next(row for row in rows if row.get('action') == 'test_status' and row.get('subtest') in targets.get(row['test'], []))
                row.update(status='FAIL', expected='PASS', message='target failed')
            elif mutation == 'control-failure-message':
                row = next(row for row in rows if row.get('action') == 'test_status' and row['status'] == 'FAIL' and row['test'] not in targets)
                row['message'] = 'changed control failure'
            elif mutation == 'prior-pass-message':
                original_passes = {(row['test'], row.get('subtest')) for row in assessments['original']['rows'] if row['status'] == 'PASS'}
                row = next(row for row in rows if row.get('action') == 'test_status' and row['test'] in targets and (row['test'], row['subtest']) in original_passes)
                row['message'] = 'changed prior PASS'
            else:
                row = next(row for row in rows if row.get('action') == 'test_end' and str(row.get('message', '')).startswith('Testing http://'))
                row['message'] = row['message'].replace('web-platform.test', 'wrong.invalid')
            try:
                observed = evaluate(changed)
            except AssertionError:
                if mutation != 'wrong-port-host':
                    raise
            else:
                assert mutation != 'wrong-port-host' and not observed['derived_ownership_gate'], mutation
        return {'positive': 1, 'negative': 4, 'synthetic_target_improvements': True, 'frozen_server_and_manifest_evidence': True}
    finally:
        shutil.rmtree(scratch)
        assert not scratch.exists()


if __name__ == '__main__':
    print(json.dumps(check(read(HERE / 'POLICY.json')), sort_keys=True))
