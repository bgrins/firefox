import argparse
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    for name in ['plain', 'instrumented', 'plain-trace', 'trace', 'model', 'out']:
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    schema = runpy.run_path(str(ROOT / 'strict_model.py'))
    cases = schema['strict_json']((ROOT / 'inputs/CASES.json').read_text())
    model = schema['read'](args.model, cases)
    reference = runpy.run_path(str(ROOT / 'inputs/reference_compare.py'))
    result = reference['compare'](cases, reference['public_rows'](args.plain.read_text()),
        reference['public_rows'](args.instrumented.read_text()), reference['trace_rows'](args.plain_trace.read_text()),
        reference['trace_rows'](args.trace.read_text()), model)
    result['model_json_exact_types_checked'] = True
    args.out.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
