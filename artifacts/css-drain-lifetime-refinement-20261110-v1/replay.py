import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = json.loads((P / 'SOURCES.json').read_text())
    for name, digest in sources.items():
        if sha(P / name) != digest:
            raise ValueError('source drift: ' + name)
    with tempfile.TemporaryDirectory(prefix='lifetime-replay-') as temp:
        work = Path(temp)
        for name in sources:
            shutil.copyfile(P / name, work / name)
        run = subprocess.run([sys.executable, str(work / 'check.py'), '--lean',
                              str(args.lean.resolve()), '--out', str(work / 'results')],
                             capture_output=True, text=True, timeout=600)
        (out / 'replay.log').write_text(run.stdout + run.stderr)
        if run.returncode:
            raise ValueError('source-only replay failed')
        shutil.copytree(work / 'results', out / 'results')
        report = json.loads((out / 'results' / 'REPORT.json').read_text())
        if report['sources'] != sources:
            raise ValueError('source-only input mismatch')
    if work.exists():
        raise ValueError('temporary source tree retained')
    (out / 'REPLAY.json').write_text(json.dumps({
        'status': 'pass', 'sources': sources, 'source_tree_removed': True,
        'no_prebuilt_module_inputs': True, 'report_sha256': sha(out / 'results' / 'REPORT.json'),
        'audits': len(report['audits']), 'new_declarations': len(report['new_declarations']),
        'observations': len(report['observations']), 'false_claim_rejections': len(report['negative_controls'])
    }, indent=2) + '\n')
    print(run.stdout.strip())

if __name__ == '__main__':
    main()
