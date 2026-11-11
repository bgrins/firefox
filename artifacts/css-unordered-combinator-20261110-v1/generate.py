import json
from pathlib import Path
import extract_v2

ROOT = Path(__file__).resolve().parent


def literal(value):
    if isinstance(value, str):
        return '.str ' + json.dumps(value)
    if type(value) is int:
        return 'Lean.toJson (' + str(value) + ' : Nat)'
    return '.arr #[' + ', '.join(literal(x) for x in value) + ']'


def generate():
    result = extract_v2.pinned_text_transform()
    program = result['program']
    ops = [('.unordered ' + str(x[1])) if x[0] == 'unordered' else
           '(.legacy (.' + x[0] + (' ' + json.dumps(x[1]) if len(x) == 2 else '') + '))' for x in program]
    oracle = json.loads((ROOT / 'text-transform-oracle.json').read_text())
    fixture = ('import JsonV2\n\nnamespace CssUnordered\n\ndef textProgram : List Op := [\n  ' + ',\n  '.join(ops) +
        ']\n\ndef textJson : Lean.Json := ' + literal(program) +
        '\n\ndef textGrammar : CssGrammar.Grammar := (decode textProgram).getD (.keyword "invalid")\n\n' +
        'def referenceWords : List (List String) := ' + json.dumps(oracle) + '\n\nend CssUnordered\n')
    return result, fixture


if __name__ == '__main__':
    result, fixture = generate()
    (ROOT / 'extraction.json').write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'program.json').write_text(json.dumps(result['program'], indent=2) + '\n')
    (ROOT / 'Fixture.lean').write_text(fixture)
