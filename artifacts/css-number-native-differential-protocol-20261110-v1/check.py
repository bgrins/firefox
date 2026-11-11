import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    for path in ROOT.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    pins = json.loads((ROOT / 'PINS.json').read_text())
    for record in pins['files']:
        if hashlib.sha256((ROOT / record['installed']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Input changed: ' + record['installed'])
    instrument = runpy.run_path(str(ROOT / 'instrument.py'))['instrument']
    original = (ROOT / 'inputs/tokenizer.rs').read_text()
    changed = instrument(original)
    patch = ''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
        fromfile='a/src/tokenizer.rs', tofile='b/src/tokenizer.rs'))
    if patch != (ROOT / 'tokenizer-trace.patch').read_text():
        raise ValueError('Trace patch differs')
    generate = runpy.run_path(str(ROOT / 'cases.py'))
    with tempfile.TemporaryDirectory(prefix='native-protocol-static-') as temp:
        generated = Path(temp) / 'prepared'
        rows = generate['emit'](generated)
        for path in generated.iterdir():
            if path.read_bytes() != (ROOT / 'prepared' / path.name).read_bytes():
                raise ValueError('Prepared case drift: ' + path.name)
    singles = [c for c in rows if c['mode'] == 'single']
    if len(rows) != 196 or len(singles) != 84 or sum(c['bridge_eligible'] for c in rows) != 180:
        raise ValueError('Corpus inventory changed')
    for c in rows:
        if c['mode'] == 'history' and not c['tail'].endswith(' ;q'):
            raise ValueError('History has no progressing suffix')
        if c['prefix_utf8_bytes'] != len(c['prefix'].encode()):
            raise ValueError('Wrong byte start')
    module = runpy.run_path(str(ROOT / 'compare.py'))
    compare = module['compare']
    prefix = generate['PREFIX']
    case = dict(id='synthetic', prefix=prefix, tail='+1e0x ;q',
        prefix_utf8_bytes=len(prefix.encode()), mode='history', bridge_eligible=True)
    start = case['prefix_utf8_bytes']
    source = (prefix + case['tail']).encode()
    number = dict(start=start, end=start+5, kind='dimension', unit=b'x', has_sign=True,
        is_integer=False, float_bits='3f800000', remaining=source[start+5:], debug=b'Dimension', line=0, column=12)
    suffix = dict(start=start+5, end=start+6, kind='other', unit=b'', has_sign=False,
        is_integer=False, float_bits='00000000', remaining=source[start+6:], debug=b'WhiteSpace', line=0, column=13)
    public = {(case['id'], phase): copy.deepcopy(suffix if phase.startswith('suffix') else number)
        for phase in module['PHASES']}
    core = dict(positions=[start, start+4, start+1, start+2, start+2, start+2, start+3, start+4],
        slices=[b'+1e0', b'x ;q', b'1', b'', b'0'], has_sign=True, is_integer=False)
    trace = {key: [copy.deepcopy(core)] if key[1] in ('cold', 'reparsed') else [] for key in public}
    empty = {key: [] for key in public}
    model = [[case['tail'], False, [[43,49,101,48], [120,32,59,113], [49], [], [48], True, False], False]]
    base = compare([case], public, copy.deepcopy(public), empty, trace, model)
    if base['lexical_comparisons'] != 2:
        raise ValueError('Synthetic positive failed')
    controls = {}
    for name in ['sign', 'type', 'prefix', 'cached-trace', 'reset-end', 'missing-model', 'missing-cold-trace', 'utf8-scalar-offset']:
        c, p, t, m = copy.deepcopy(case), copy.deepcopy(public), copy.deepcopy(trace), copy.deepcopy(model)
        if name == 'sign': t[('synthetic', 'cold')][0]['has_sign'] = False
        elif name == 'type':
            for phase in ['cold', 'cached', 'reparsed']: p[('synthetic', phase)]['is_integer'] = True
            for phase in ['cold', 'reparsed']: t[('synthetic', phase)][0]['is_integer'] = True
        elif name == 'prefix': t[('synthetic', 'cold')][0]['positions'][1] += 1
        elif name == 'cached-trace': t[('synthetic', 'cached')] = [copy.deepcopy(core)]
        elif name == 'reset-end': p[('synthetic', 'reparsed')]['end'] += 1
        elif name == 'missing-model': m = []
        elif name == 'missing-cold-trace': t[('synthetic', 'cold')] = []
        else: c['prefix_utf8_bytes'] = len(prefix)
        try:
            compare([c], p, copy.deepcopy(p), empty, t, m)
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError('Control survived: ' + name)
    public_text = ''
    trace_text = ''
    for key, value in public.items():
        public_text += '\t'.join(['PUBLIC', *key, str(value['start']), str(value['end']), value['kind'],
            value['unit'].hex(), str(value['has_sign']).lower(), str(value['is_integer']).lower(),
            value['float_bits'], value['remaining'].hex(), value['debug'].hex(), str(value['line']), str(value['column'])]) + '\n'
        trace_text += '\t'.join(['CALL', *key]) + '\n'
        for value in trace[key]:
            trace_text += '\t'.join(['TRACE', *map(str, value['positions']), *[s.hex() for s in value['slices']],
                str(value['has_sign']).lower(), str(value['is_integer']).lower()]) + '\n'
        trace_text += '\t'.join(['END', *key]) + '\n'
    if module['public_rows'](public_text) != public or module['trace_rows'](trace_text) != trace:
        raise ValueError('Synthetic wire format did not roundtrip')
    varied_bits = copy.deepcopy(public)
    for phase in ['cold', 'cached', 'reparsed']: varied_bits[('synthetic', phase)]['float_bits'] = 'deadbeef'
    compare([case], varied_bits, copy.deepcopy(varied_bits), empty, trace, model)
    report = dict(status='static-source-protocol-pass', pinned_input_files=len(pins['files']),
        exact_insertion_sites=7, planned_cases=len(rows), inherited_baseline_cases=len(singles),
        bridge_eligible_cases=180, excluded_legacy_rows=16, synthetic_controls=controls,
        synthetic_float_bits_ignored_by_lexical_model=True, python_sources_parsed=True,
        rust_compiled=False, native_executed=False, lean_model_executed=False,
        production_feature_equivalence=False)
    (ROOT / 'STATIC-REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
