import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from fractions import Fraction as Q
import effect_native
import effect_oracle
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'baseline'))
import oracle
import check


def command(args, out, env, commands, input=None):
    result = subprocess.run(args, cwd=BASE, env=env, input=input, text=True, capture_output=True)
    commands.append(dict(command=args, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout


def run(out, baseline_result, lean):
    out.mkdir(parents=True, exist_ok=False)
    events = effect_native.run(out / 'native')
    proof = out / 'lean'
    proof.mkdir()
    env = dict(os.environ, LEAN_PATH=str(proof) + os.pathsep + str(baseline_result / 'lean'))
    commands = []
    for name in ['Effects', 'EffectRunner']:
        command([str(lean), '-o', str(proof / (name + '.olean')), str(BASE / (name + '.lean'))], proof, env, commands)
    source = (BASE / 'Effects.lean').read_text()
    assert not re.search(r'\b(sorry|axiom|native_decide)\b', source)
    names = re.findall(r'^theorem ([A-Za-z_][A-Za-z_0-9]*)', source, re.M)
    (proof / 'Axioms.lean').write_text('import Effects\n' + ''.join('#print axioms Rlh.Effects.' + n + '\n' for n in names))
    axioms = command([str(lean), str(proof / 'Axioms.lean')], proof, env, commands)
    assert 'sorryAx' not in axioms and 'Lean.ofReduceBool' not in axioms
    dependencies = re.findall(r'depends on axioms: \[(.*?)\]', axioms)
    assert len(dependencies) == len(names)
    for row in dependencies:
        assert set(row.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
    assert not re.search(r'\b(sorry|axiom|native_decide)\b', (BASE / 'EffectRunner.lean').read_text())
    (proof / 'axioms.txt').write_text(axioms)
    (proof / 'theorems.json').write_text(json.dumps(names, indent=2) + '\n')
    lines = []
    read_events = [e for e in events if e['event'] == 'READ']
    for e in read_events:
        values = [e[k] for k in ['id', 'role', 'base', 'form', 'parentForm', 'flags']]
        for key in ['fontDependency', 'lineHeightDependency']:
            values.extend([int(e[key] is not None), str(Q(e[key] or 0))])
        lines.append(' '.join(map(str, values)))
    protocol = '\n'.join(lines) + '\n'
    (proof / 'input.txt').write_text(protocol)
    variants = [('original', 4), ('candidate', 0), ('drop-relative', 1), ('drop-normal', 2), ('clear-incoming', 3)]
    allrows = {}
    counts = {}
    witnesses = {}
    preparation = check.preparation(events)
    roots = {}
    root = None
    for event in events:
        if event['event'] == 'ROOT':
            root = event
        elif event['event'] == 'READ':
            assert root is not None and event['form'] == root['form']
            roots[event['id']] = root
    for name, mutation in variants:
        output = command([str(lean), '--run', str(BASE / 'EffectRunner.lean'), str(mutation)], proof, env, commands, protocol)
        (proof / (name + '.txt')).write_text(output)
        native = [json.loads(x) for x in (out / 'native' / name / 'raw.jsonl').read_text().splitlines()]
        expected = oracle.observe(events, 'original' if name == 'original' else 'candidate')
        assert len(native) == len(events) == len(expected)
        setup = [json.loads(x) for x in (out / 'native' / name / 'stderr.txt').read_text().splitlines()]
        assert setup == preparation
        for e, actual, prediction in zip(events, native, expected):
            if e['event'] == 'READ':
                prediction.update(effect_oracle.expected_effect(e, mutation if name != 'original' else 0))
            assert actual == prediction, (name, e, actual, prediction)
        reads = {r['id']: r for r in native if r['event'] == 'read'}
        allrows[name] = reads
        model_rows = [row.split() for row in output.splitlines()]
        assert len(model_rows) == len(read_events)
        for e, row in zip(read_events, model_rows):
            ident = int(row[0]); assert ident == e['id']
            actual = reads[ident]
            expected_scaled, expected_exposed = effect_oracle.semantic(e, roots[ident], name == 'original')
            assert Q(row[1]) == expected_scaled == check.exact_bits(actual['scaled_bits'])
            assert Q(row[2]) == expected_exposed == check.exact_bits(actual['exposed_bits']) == check.exact_bits(actual['cpp_bits'])
            assert int(row[3]) == actual['flags']
            assert (row[4] == 'true') == actual['font_present']
            assert (row[6] == 'true') == actual['lh_present']
            assert Q(row[5]) == check.exact_bits(actual['font_dependency'])
            assert Q(row[7]) == check.exact_bits(actual['lh_dependency'])
        counts[name] = dict(events=len(native), reads=len(reads), leanRows=len(model_rows), fullMachineTraceOracle=True)
    effects = ['flags', 'font_dependency', 'lh_dependency', 'font_present', 'lh_present']
    preserved = 0
    for e in read_events:
        a = allrows['original'][e['id']]; b = allrows['candidate'][e['id']]
        assert {k: a[k] for k in effects} == {k: b[k] for k in effects}
        if e['role'] != 0:
            assert a == b
            preserved += 1
    for name, mutation in variants[2:]:
        changed = []
        for e in read_events:
            a = allrows[name][e['id']]; b = allrows['candidate'][e['id']]
            assert {k: v for k, v in a.items() if k not in effects} == {k: v for k, v in b.items() if k not in effects}
            if a['flags'] != b['flags']:
                changed.append(dict(input=e, candidate=b, mutant=a))
        assert changed, name
        counts[name]['effectDifferences'] = len(changed)
        counts[name]['numericDifferences'] = 0
        witnesses[name] = changed[:3]
    result = dict(theorems=len(names), variants=counts, nonrootCompletePreservation=preserved,
        allRoleEffectPreservation=len(read_events), mutantWitnesses=witnesses,
        normalDiagnosticReads=sum(e['diagnostic'] for e in read_events),
        seededNonemptyReads=sum(e['flags'] != 0 and (e['fontDependency'] is not None or e['lineHeightDependency'] is not None) for e in read_events))
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
