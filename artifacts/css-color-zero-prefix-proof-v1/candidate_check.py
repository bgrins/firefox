import json
import subprocess
import sys
from pathlib import Path
import source_binding as binding

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
SOURCE_NAMES = ['Fold.lean', 'check.py', 'controls.py', 'README.md', 'PREPARATION.json',
                'source_binding.py', 'candidate_check.py', 'CANDIDATE-SOURCE-v1.json',
                'CANDIDATE-SPEC-v1.json', 'color-mix-result.html', 'CANDIDATE-README.md']

def hashes(paths):
    return {str(path): binding.digest(path.read_bytes()) for path in paths}

def main():
    if sys.flags.optimize or len(sys.argv) not in [2, 3] or (len(sys.argv) == 3 and sys.argv[2] != '--snapshots-only'):
        raise RuntimeError('Usage: python3 candidate_check.py NEW_OUTPUT_DIRECTORY [--snapshots-only]')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    live = len(sys.argv) == 2
    paths = [BASE / name for name in SOURCE_NAMES]
    if live:
        paths += [ROOT / binding.MIX, ROOT / binding.FLAGS]
    before = hashes(paths)
    preparation = json.loads((BASE / 'PREPARATION.json').read_text())
    for name in ['Fold.lean', 'check.py', 'controls.py', 'README.md']:
        key = str((BASE / name).relative_to(ROOT))
        if binding.digest((BASE / name).read_bytes()) != preparation['hashes'][key]:
            raise RuntimeError('Prepared model changed: ' + name)
    spec = json.loads((BASE / 'CANDIDATE-SPEC-v1.json').read_text())
    if binding.digest((BASE / 'color-mix-result.html').read_bytes()) != spec['section_sha256']:
        raise RuntimeError('Spec subsection changed')
    source = binding.run(out / 'snapshots', live)
    command = [sys.executable, str(BASE / 'check.py'), str(out / 'model')]
    result = subprocess.run(command, capture_output=True, text=True)
    (out / 'model.stdout').write_text(result.stdout)
    (out / 'model.stderr').write_text(result.stderr)
    if result.returncode or result.stderr:
        raise RuntimeError('Model replay failed')
    model = json.loads((out / 'model/report.json').read_text())
    if model['status'] != 'checked-model-only' or len(model['audits']) != 17 or len(model['controls']) != 4 or len(model['record_controls']) != 9:
        raise RuntimeError('Model inventory mismatch')
    if hashes(paths) != before:
        raise RuntimeError('Inputs changed during candidate replay')
    report = {'status': 'pass', 'source_bridge': 'manually reviewed exact delta and frozen source shapes; not Rust extraction',
              **source, 'audits': model['audits'], 'semantic_controls': list(model['controls']),
              'record_controls': model['record_controls'], 'pins': before,
              'model_report_sha256': binding.digest((out / 'model/report.json').read_bytes()),
              'command': command, 'exit': result.returncode,
              'limits': 'Rational normalized fold after conversion/weight normalization; compatible interpolation premise. Raw rational fold preserved. No IEEE, parser, conversion, full premultiplication, browser, or all-zero-total conformance theorem.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'pass', 'live_native_verified': live, 'audits': 17,
                      'semantic_controls': 4, 'record_controls': 9,
                      'source_controls': len(source['source_controls'])}))

if __name__ == '__main__':
    main()
