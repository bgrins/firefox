import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    analyzer, generator = load('analyze'), load('generate')
    for name, expected in json.loads((ROOT / 'PREPARATION-FILES.json').read_text()).items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    origin = json.loads((ROOT / 'ORIGINS.json').read_text())
    for item in origin['copies']:
        assert hashlib.sha256((ROOT / item['copy']).read_bytes()).hexdigest() == item['sha256']
    manifest = json.loads((ROOT / 'inputs/model-source-only.json').read_text())
    for local, original in [('oracle.json', 'text-transform-oracle.json'), ('model-TextLaws.lean', 'TextLaws.lean'), ('model-Fixture.lean', 'Fixture.lean'), ('model-extraction.json', 'extraction.json')]:
        assert hashlib.sha256((ROOT / 'inputs' / local).read_bytes()).hexdigest() == manifest[original]
    assert origin['full_spec_source']['sha256'] == manifest['inputs/css-text-3.bs']
    corpus = json.loads((ROOT / 'corpus.json').read_text())
    oracle = json.loads((ROOT / 'inputs/oracle.json').read_text())
    alpha = ['none', 'capitalize', 'uppercase', 'lowercase', 'full-width', 'full-size-kana']
    words = [list(x) for n in range(5) for x in itertools.product(alpha, repeat=n)]
    assert corpus['alphabet'] == alpha and corpus['maxLength'] == 4
    assert len(words) == 1555 and len(oracle) == 38
    assert corpus['rows'] == [dict(id=i, tokens=x, value=' '.join(x), expected=x in oracle) for i, x in enumerate(words)]
    assert corpus['oracleSha256'] == hashlib.sha256((ROOT / 'inputs/oracle.json').read_bytes()).hexdigest()
    assert corpus['modelManifestSha256'] == hashlib.sha256((ROOT / 'inputs/model-source-only.json').read_bytes()).hexdigest()
    assert (ROOT / 'probe.html').read_text() == generator.render()
    commands = []

    def node(args):
        result = subprocess.run(['node', *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0 and result.stderr == '', result.stderr
        commands.append(dict(argv=['node', *args], returncode=result.returncode, stdoutSha256=hashlib.sha256(result.stdout.encode()).hexdigest(), stderr=result.stderr))
        return result.stdout

    node(['--check', str(ROOT / 'probe.js')])
    node(['--check', str(ROOT / 'mock-collector.js')])
    baseline = json.loads(node([str(ROOT / 'mock-collector.js'), str(ROOT), 'baseline']))
    summary = analyzer.analyze(baseline)
    assert summary['status'] == 'MATCH' and len(baseline['rows']) == 1555
    assert any(row['style']['serialized'] != row['value'] and row['style']['present'] for row in baseline['rows'])
    over = analyzer.analyze(json.loads(node([str(ROOT / 'mock-collector.js'), str(ROOT), 'overaccept'])))
    assert over['status'] == 'MISMATCH' and [(x['value'], x['reasons']) for x in over['differences']] == [('none full-width', ['CSS.supports', 'CSSStyleDeclaration'])]
    removal = analyzer.analyze(json.loads(node([str(ROOT / 'mock-collector.js'), str(ROOT), 'broken-removal'])))
    assert removal['status'] == 'SETUP_FAILED' and removal['setupFailures'] == [''] and removal['differences'][0]['reasons'] == ['empty-removal']
    controls = []
    mutations = [
        ('bool-id', lambda x: x['rows'][0].update(id=False)),
        ('int-support', lambda x: x['rows'][1]['supports'].update(value=1)),
        ('int-presence', lambda x: x['rows'][1]['style'].update(present=1)),
        ('missing-row', lambda x: x['rows'].pop()),
        ('swapped-row', lambda x: x['rows'].__setitem__(1, copy.deepcopy(x['rows'][2]))),
        ('changed-value', lambda x: x['rows'][1].update(value='changed')),
        ('wrong-model', lambda x: x.update(modelManifestSha256='0' * 64)),
        ('extra-field', lambda x: x.update(extra=True)),
        ('missing-removal', lambda x: x['rows'][0].update(removal=None)),
        ('unexpected-removal', lambda x: x['rows'][1].update(removal=x['rows'][0]['removal'])),
    ]
    for label, mutate in mutations:
        changed = copy.deepcopy(baseline)
        mutate(changed)
        try:
            analyzer.analyze(changed)
        except ValueError as error:
            controls.append(dict(label=label, rejection=str(error)))
        else:
            raise AssertionError(label)
    try:
        json.loads('{"schema":1,"schema":1}', object_pairs_hook=analyzer.strict_object)
    except ValueError as error:
        controls.append(dict(label='duplicate-key', rejection=str(error)))
    else:
        raise AssertionError('duplicate-key')
    print(json.dumps(dict(status='PREPARATION_PASS', browserExecution=False, corpusRows=1555, expectedAccepted=38,
                         mockOnlyModes=3, schemaRefusals=controls, commands=commands), indent=2))


if __name__ == '__main__':
    main()
