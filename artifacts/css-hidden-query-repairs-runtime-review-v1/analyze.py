import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / 'css-hidden-query-repairs-runtime-v1'
PHASES = ['baseline', 'column-provider', 'skipped-line-block', 'both']
INPUTS_PIN = '4ee88af61d624271b4dfd68044bd79c509c2c5fd6942b4de6f6a991179de16a9'
read_pins = {}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    read_pins[str(path)] = digest(path)
    return json.loads(path.read_bytes())


def rows_map(rows):
    result = {}
    for row in rows:
        key = (row['test'], row['subtest'])
        need(key not in result, 'duplicate subtest')
        result[key] = (row['status'], row.get('message'))
    return result


def ends_map(rows):
    need(len({r['test'] for r in rows}) == len(rows), 'duplicate harness end')
    return {r['test']: r['status'] for r in rows}


parser = argparse.ArgumentParser()
parser.add_argument('--phase', choices=PHASES, action='append')
parser.add_argument('--final-files-sha256')
args = parser.parse_args()
selected = PHASES if args.final_files_sha256 else args.phase or []
need(digest(RUNTIME/'INPUTS.json') == INPUTS_PIN, 'INPUTS pin')
inputs = load(RUNTIME/'INPUTS.json')
need(inputs['before']['head'] == 'b37292ebe0c64a68c4fdd7b2d1be8ccd27efa912', 'prepared HEAD')
for relative, pin in inputs['payload_pins'].items():
    path = RUNTIME/relative
    need(not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe input')
    need(path.is_file() and not path.is_symlink() and digest(path) == pin, 'input '+relative)
need(digest(RUNTIME/'DRAFT-FILES.json') == inputs['draft_sha256'], 'draft pin')
for name,pin in inputs['prior_terminal_pins'].items():
    need(digest(HERE.parents[1]/name)==pin, 'prior terminal pin '+name)
config = load(RUNTIME/'CONFIG.json')
expected = {(url, name) for url, names in config['expected_subtests'].items() for name in names}
need(len(expected) == 66 and len(config['tests']) == 7, 'roster')
need(len(config['install']) == 2 and len(config['tracked_tests']) == 5, 'test partition')
prior = load(RUNTIME/'evidence/prior-both-RUN.json')
prior_rows = rows_map(prior['rows'])
prior_ends = ends_map(prior['ends'])
need(prior['complete'] and set(prior_rows) == expected, 'prior oracle completeness')
need(Counter(v[0] for v in prior_rows.values()) == {'PASS': 55, 'FAIL': 11}, 'prior oracle outcomes')
residuals = {k for k, value in prior_rows.items() if value[0] == 'FAIL'}
result = {'final': bool(args.final_files_sha256), 'prepared_head': inputs['before']['head'],
          'input_payloads_authenticated': len(inputs['payload_pins']), 'phases': {}}
retained = {}
for phase in selected:
    raw_path = RUNTIME/phase/'raw.json'
    read_pins[str(raw_path)] = digest(raw_path)
    events = [json.loads(line) for line in raw_path.read_bytes().splitlines() if line]
    rows = [r for r in events if r.get('action') == 'test_status']
    ends = [r for r in events if r.get('action') == 'test_end']
    values, harness = rows_map(rows), ends_map(ends)
    need(set(values) == expected and harness == prior_ends and len(harness) == 7, 'exact phase identities/harness')
    need(set(harness.values()) == {'OK'}, 'non-OK harness')
    need(sum(r.get('action') == 'suite_end' for r in events) == 1, 'suite incomplete')
    for url, names in config['expected_subtests'].items():
        need([r['subtest'] for r in rows if r['test'] == url] == names, 'ordered names')
    need(all(v[0] in ['PASS','FAIL'] for v in values.values()), 'unexpected status')
    run = load(RUNTIME/phase/'RUN.json')
    need(run['complete'] and run['exit'] in [0,1] and run['before'] == run['after'], 'phase integrity')
    need(rows_map(run['rows']) == values and ends_map(run['ends']) == harness, 'raw/RUN mismatch')
    for name, pin in inputs['resource_pins'].items():
        need(run['before'][name] == pin, 'resource pin '+name)
    replacements = {
        'layout/base/PresShell.cpp': 'pres-shell-column.cpp' if phase in ['column-provider','both'] else 'pres-shell-before.cpp',
        'layout/generic/nsBlockFrame.cpp': 'block-skipped-line.cpp' if phase in ['skipped-line-block','both'] else 'block-before.cpp',
    }
    for name in config['guard_sources']:
        if name in replacements:
            pin = digest(RUNTIME/'selected'/replacements[name])
        elif name in config['sources']:
            pin = digest(RUNTIME/'prepared/head'/name)
        else:
            pin = inputs['source_pins'][name]
        need(run['before'][name] == pin, 'source role '+name)
    for name, pin in run['before'].items():
        if pin is not None and '/Contents/MacOS/' not in name:
            need(digest(RUNTIME/phase/'inputs'/name) == pin, 'retained source/resource '+name)
    need(load(RUNTIME/(phase+'-build.json'))['exit'] == 0, 'build failed')
    if phase == 'baseline':
        need(values == prior_rows, 'baseline status/message oracle changed')
    subsets = {}
    for url in config['expected_subtests']:
        subsets[url] = dict(Counter(v[0] for k,v in values.items() if k[0] == url))
    result['phases'][phase] = {
        'counts': dict(Counter(v[0] for v in values.values())), 'exit': run['exit'],
        'subsets': subsets, 'harness': harness,
        'transitions_from_prior_baseline': dict(Counter(prior_rows[k][0]+'->'+values[k][0] for k in expected)),
        'regressions': [{'test':k[0], 'subtest':k[1], 'message':values[k][1]} for k in sorted(expected)
                        if prior_rows[k][0] == 'PASS' and values[k][0] == 'FAIL'],
        'changes': [{'test':k[0], 'subtest':k[1], 'before':prior_rows[k], 'after':values[k]}
                    for k in sorted(expected) if prior_rows[k] != values[k]],
    }
    retained[phase] = values
result['original_11_residuals'] = [{'test':k[0], 'subtest':k[1], 'prior':prior_rows[k],
    'phases': {phase:values[k] for phase, values in retained.items()}} for k in sorted(residuals)]
result['pairwise'] = {}
for i,left in enumerate(selected):
    for right in selected[i+1:]:
        result['pairwise'][left+' -> '+right] = {
            'transitions':dict(Counter(retained[left][k][0]+'->'+retained[right][k][0] for k in expected)),
            'changed': [{'test':k[0], 'subtest':k[1], 'before':retained[left][k], 'after':retained[right][k]}
                        for k in sorted(expected) if retained[left][k] != retained[right][k]],
        }
if set(selected)==set(PHASES):
    result['four_phase_patterns']=dict(Counter('/'.join(retained[p][k][0] for p in PHASES) for k in expected))
    root_analysis=load(HERE.parent/'css-hidden-query-repairs-analysis-v1/RESULT.json')
    need(root_analysis['four_phase_patterns']==result['four_phase_patterns'], 'root pattern mismatch')
    for phase in PHASES:
        need(root_analysis['phases'][phase]['counts']==result['phases'][phase]['counts'], 'root counts mismatch')
        need(root_analysis['phases'][phase]['files']==result['phases'][phase]['subsets'], 'root subsets mismatch')
    for label,comparison in root_analysis['pairs'].items():
        need(result['pairwise'][label]['transitions']==comparison['transitions'], 'root pair mismatch')
    for row in root_analysis['baseline_failure_matrix']:
        key=(row['test'],row['subtest'])
        need(key in residuals and all(tuple(row['outcomes'][phase])==retained[phase][key] for phase in PHASES), 'root residual mismatch')
    need(len(root_analysis['baseline_failure_matrix'])==11, 'root residual count')
    result['root_analysis_agreement']=True
if args.final_files_sha256:
    need(digest(RUNTIME/'FILES.json') == args.final_files_sha256, 'final runtime seal')
    manifest = load(RUNTIME/'FILES.json')
    manifest = manifest.get('files', manifest)
    for name,pin in manifest.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts
             and (RUNTIME/name).is_file() and not (RUNTIME/name).is_symlink()
             and digest(RUNTIME/name) == pin, 'final payload '+name)
    actual={str(p.relative_to(RUNTIME)) for p in RUNTIME.rglob('*') if p.is_file()}
    need(actual-set(manifest) <= {'FILES.json','FREEZE.json'}, 'unlisted runtime payload')
    state = load(RUNTIME/'STATE.json')
    final = load(RUNTIME/'FINAL.json')
    need(state['status'] == 'terminal' and state['restored'] and state['restore_build_exit'] == 0
         and not state['recovery_errors'] and 'failure' not in state, 'unsuccessful restoration')
    need(final == load(RUNTIME/'BEFORE.json') == inputs['before'], 'historical before/final mismatch')
    for phase in PHASES:
        need({k:v for k,v in state['phases'][phase]['status_counts'].items() if v} == result['phases'][phase]['counts'], 'root counts')
    need(all(digest(HERE.parents[1]/name)==pin for name,pin in final['sources'].items()), 'live restored source bytes')
    need(all(not (HERE.parents[1]/name).exists() and not (HERE.parents[1]/name).is_symlink()
             for name in config['must_be_absent']), 'temporary diagnostic remains')
    need(all(digest(HERE.parents[1]/name)==inputs['resource_pins'][name] for name in config['tracked_tests']), 'tracked test changed')
    result['restoration'] = {'historical_before_equals_final': True, 'native_guards':28,
        'tracked_test_files':5, 'temporary_test_files':2, 'restore_build_exit':0,
        'runtime_files_sha256':args.final_files_sha256, 'payloads':len(manifest),
        'live_restored_28_sources_and_5_tests_verified':True,'temporary_diagnostics_absent':True}
suffix = 'FINAL' if args.final_files_sha256 else '-'.join(selected) or 'INPUTS'
(HERE/(suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n')
(HERE/(suffix+'-READ-PINS.json')).write_text(json.dumps(read_pins,indent=2)+'\n')
print(json.dumps({'selected':selected, 'authenticated_inputs':len(inputs['payload_pins']),
                  'outcomes':{k:v['counts'] for k,v in result['phases'].items()},'final':result['final']},indent=2))
