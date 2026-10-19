import hashlib
import copy
import json
import os
from pathlib import Path
import re

import fixtures
import instrument
import lean_semantic_cases
import semantic
import traversal_mutations

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out, tools, compiler, execute, safe_model, native_mutants):
    out.mkdir()
    cases = semantic.corpus()
    ranks = [dict(id=c['id'], ranks=semantic.validate(c)) for c in cases]
    wire = '\n'.join(fixtures.wire(c) for c in cases) + '\n'
    (out / 'cases.json').write_text(json.dumps(cases, indent=2) + '\n')
    (out / 'ranks.json').write_text(json.dumps(ranks, indent=2) + '\n')
    (out / 'inputs.txt').write_text(wire)
    all_traces = {}
    recovery_checks = []
    for repaired in [False, True]:
        name = 'candidate' if repaired else 'original'
        ordinary = execute([out.parent / name], out, name + '-ordinary', wire)
        assert ordinary.returncode == 0, ordinary.stderr
        rows = ordinary.stdout.splitlines()
        assert len(rows) == len(cases)
        old_rows = (out.parent / (name + '-run.stdout')).read_text().splitlines()
        assert rows[:len(old_rows)] == old_rows
        source, inventory = instrument.generate(repaired)
        assert inventory['recovery_verified']
        for label, items, edits in [
            ('snippets', inventory['instrumented_snippets'], inventory['changes']),
            ('adapter', {'adapter': inventory['instrumented_adapter']}, inventory['adapter_changes']),
        ]:
            bad = copy.deepcopy(edits)
            bad[-1]['occurrences'] += 1
            try:
                instrument.recover(items, bad)
            except AssertionError:
                recovery_checks.append(dict(variant=name, component=label,
                                            corrupted_count_rejected=True))
            else:
                raise AssertionError(('corrupted instrumentation count accepted', name, label))
        file = out / (name + '-instrumented.cpp')
        file.write_text(source)
        (out / (name + '-instrumentation.json')).write_text(json.dumps(inventory, indent=2) + '\n')
        p = execute(compiler + [file, '-o', out / name], out, name + '-compile')
        assert p.returncode == 0, p.stderr
        p = execute([out / name], out, name + '-instrumented-run', wire)
        assert p.returncode == 0, p.stderr
        instrumented = p.stdout.splitlines()
        assert len(instrumented) == len(cases)
        traces = []
        for c, ordinary_row, row in zip(cases, rows, instrumented):
            values, providers, trace = row.split('|')
            assert values + '|' + providers == ordinary_row, ('instrumentation changed execution', c['id'])
            expected = fixtures.oracle(c, repaired)
            assert list(map(int, values.split())) == expected['values'], c['id']
            assert providers == ''.join(e + ';' for e in expected['events']), c['id']
            result, semantic_trace = semantic.oracle(c, repaired)
            assert result == expected['values'][1], c['id']
            assert trace == ''.join(e + ';' for e in semantic_trace), (c['id'], trace, semantic_trace)
            traces.append(semantic_trace)
        all_traces[name] = traces

    extended_mutants = []
    for mutation in native_mutants:
        name = mutation['name']
        p = execute([out.parent / name], out, 'extended-' + name, wire)
        assert p.returncode == 0, (name, p.stderr)
        rows = p.stdout.splitlines()
        assert len(rows) == len(cases), (name, len(rows), len(cases))
        value_differences = []
        for c, row in zip(cases, rows):
            values, providers = row.split('|')
            values = list(map(int, values.split()))
            assert values[0] == c['id']
            if values != fixtures.oracle(c, True)['values']:
                value_differences.append(c['id'])
        assert value_differences, name
        extended_mutants.append(dict(name=name, input_count=len(cases), run_exit=0,
                                     value_differences=len(value_differences), first_witness=value_differences[0],
                                     compiler_receipt='../' + name + '-compile.json'))

    preserved = 0
    for c, old, new in zip(cases, all_traces['original'], all_traces['candidate']):
        if all(f['pos'] != 3 for f in c['frames']):
            assert old == new, ('nonfixed trace', c['id'])
            preserved += 1
    pair = cases[-3:-1]
    left, right = [semantic.oracle(c, True) for c in pair]
    assert left[0] == right[0] and left[1] != right[1]
    (out / 'same-winner-distinct-flow.json').write_text(json.dumps(
        dict(ids=[c['id'] for c in pair], outcomes=[left, right]), indent=2) + '\n')

    env = os.environ.copy()
    env['LEAN_PATH'] = str(out.parent)
    source = (ROOT / 'Traversal.lean').read_text()
    safe_model(source)
    model = out / 'Traversal.lean'
    model.write_text(source)
    p = execute([tools['lean'], '-o', out.parent / 'Traversal.olean', model], out, 'lean-model', env=env)
    assert p.returncode == 0, p.stdout
    names = re.findall(r'^theorem (\w+)', source, re.M)
    audit = out / 'Audit.lean'
    audit.write_text('import Traversal\n' + '\n'.join('#print axioms Traversal.' + name for name in names) + '\n')
    p = execute([tools['lean'], audit], out, 'lean-axioms', env=env)
    assert p.returncode == 0 and len(re.findall("'Traversal\\.", p.stdout)) == len(names)
    assert 'sorryAx' not in p.stdout and 'Lean.ofReduceBool' not in p.stdout
    for axioms in re.findall(r'depends on axioms: \[(.*?)\]', p.stdout):
        assert set(axioms.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
    export = out / 'SemanticCases.lean'
    export.write_text(lean_semantic_cases.generate(cases))
    p = execute([tools['lean'], export], out, 'lean-semantic-cases', env=env)
    assert p.returncode == 0, p.stdout[:5000]
    rows = p.stdout.splitlines()
    assert len(rows) == len(cases)
    for c, row in zip(cases, rows):
        old, ot = semantic.oracle(c, False)
        new, nt = semantic.oracle(c, True)
        expected = [str(c['id']), str(old), str(old), str(new), str(new),
                    ';'.join(ot), ';'.join(ot), ';'.join(nt), ';'.join(nt)]
        assert row.split(' ') == expected, (c['id'], row, expected)

    mutations = []
    for name, old, new in traversal_mutations.CHANGES:
        assert source.count(old) == 1, name
        changed = source.replace(old, new)
        file = out / ('mutation-' + name + '.lean')
        file.write_text(changed)
        p = execute([tools['lean'], file], out, 'mutation-' + name, env=env)
        assert p.returncode == 1 and ('unsolved goals' in p.stdout or 'failed' in p.stdout or 'mismatch' in p.stdout), (name, p.stdout)
        expression, expected, altered = traversal_mutations.WITNESSES[name]
        executions = []
        for variant, body, wanted in [('reference', source, expected), ('changed', changed, altered)]:
            file = out / ('witness-' + name + '-' + variant + '.lean')
            file.write_text(traversal_mutations.executable(body, name))
            witness = execute([tools['lean'], file], out, 'witness-' + name + '-' + variant, env=env)
            assert witness.returncode == 0 and witness.stdout == wanted, (name, variant, witness.stdout)
            executions.append(dict(variant=variant, exit_code=0, stdout=witness.stdout))
        assert expected != altered
        mutations.append(dict(name=name, expression=expression, proof_failure_exit=p.returncode,
                              executions=executions, selected_value_changed=expected.split('|')[0] != altered.split('|')[0]))

    source, _ = instrument.generate(True)
    old = 'sem("K", sid(aFrame), static_cast<int>(listID));'
    assert source.count(old) == 1
    file = out / 'diagnostic-missing-trace-event.cpp'
    file.write_text(source.replace(old, '(void)listID;'))
    p = execute(compiler + [file, '-o', out / 'diagnostic-missing-trace-event'], out, 'diagnostic-missing-trace-event-compile')
    assert p.returncode == 0, p.stderr
    p = execute([out / 'diagnostic-missing-trace-event'], out, 'diagnostic-missing-trace-event-run', wire)
    assert p.returncode == 0, p.stderr
    rows = p.stdout.splitlines()
    reference_rows = (out / 'candidate-instrumented-run.stdout').read_text().splitlines()
    assert len(rows) == len(cases)
    changed_traces = 0
    for row, reference in zip(rows, reference_rows):
        actual, trace = row.rsplit('|', 1)
        reference, expected = reference.rsplit('|', 1)
        assert actual == reference
        changed_traces += trace != expected
    assert changed_traces > 0
    summary = dict(status='PASS', cases_per_native_variant=len(cases),
        direct_classifier_cases=sum(c['mode'] == 1 for c in cases),
        public_graph_cases=sum(c['mode'] == 0 for c in cases),
        ordinary_instrumented_state_and_provider_equality=True,
        semantic_outcomes_per_case=4, new_theorems=len(names),
        maximum_provider_rank=max(max(item['ranks']) for item in ranks),
        nofixed_trace_preservation_cases=preserved,
        native_instrumentation_edits_per_variant=14,
        adapter_instrumentation_edits_per_variant=5,
        exact_uninstrumented_source_recovery=True,
        recovery_diagnostics=recovery_checks,
        lean_semantic_mutations=mutations,
        native_semantic_mutations=extended_mutants,
        trace_observer_diagnostic=dict(input_count=len(cases), compile_exit=0, run_exit=0,
            trace_differences=changed_traces, value_and_provider_differences=0,
            classification='instrumentation sensitivity diagnostic; not native semantic bug mutation'),
        limits='Universal Lean interpreter agreement under ranked stable providers; C++ bridge remains bounded. Singleton continuation highlight providers.')
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary
