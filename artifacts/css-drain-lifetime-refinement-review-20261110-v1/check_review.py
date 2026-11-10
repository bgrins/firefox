import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--author', required=True, type=Path)
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    author, lean, out = args.author.resolve(), args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest_data = (author / 'SOURCES.json').read_bytes()
    sources = json.loads(manifest_data)
    imports = json.loads((author / 'IMPORTS.json').read_text())
    repo = ROOT.parent.parent
    for record in imports.values():
        if sha((repo / record['path']).read_bytes()) != record['sha256']:
            raise ValueError('Origin mismatch: ' + record['path'])
    commands = {}

    def run(label, command, work):
        result = subprocess.run([str(x) for x in command], cwd=work,
                                env=dict(os.environ, LEAN_PATH=str(work)),
                                capture_output=True, text=True, timeout=600)
        output = result.stdout + result.stderr
        (out / (label + '.log')).write_text(output)
        commands[label] = dict(exit_code=result.returncode, output_sha256=sha(output.encode()))
        if result.returncode or re.search(r'(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()', output):
            raise ValueError('Replay failed: ' + label + '\n' + output)
        return output

    with tempfile.TemporaryDirectory(prefix='lifetime-independent-', dir=out) as directory:
        work = Path(directory)
        for name, digest in sources.items():
            data = (author / name).read_bytes()
            if sha(data) != digest:
                raise ValueError('Author source drift: ' + name)
            (work / name).write_bytes(data)
        run('author-source-replay', ['python3', '-I', '-B', work / 'check.py', '--lean', lean,
                                    '--out', out / 'author-replay'], work)
        author_report = json.loads((out / 'author-replay/REPORT.json').read_text())
        if author_report['status'] != 'pass' or author_report['sources'] != sources:
            raise ValueError('Incomplete author replay receipt')
        modules = list(imports) + ['Lifetime', 'LifetimeDelivery']
        for module in modules:
            run('boundary-build-' + module,
                [lean, '-o', module + '.olean', module + '.lean'], work)
        shutil.copyfile(ROOT / 'Boundaries.lean', work / 'Boundaries.lean')
        run('boundaries', [lean, '-o', 'Boundaries.olean', 'Boundaries.lean'], work)
        names = ['IndependentLifetimeReview.' + name for name in
                 re.findall(r'^theorem (\w+)', (ROOT / 'Boundaries.lean').read_text(), re.M)]
        (work / 'Audit.lean').write_text('import Boundaries\n' + ''.join(
            '#print axioms ' + name + '\n' for name in names))
        output = run('boundary-audit', [lean, 'Audit.lean'], work)
        audits = {}
        for line in re.sub(r',\n\s*', ', ', output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError('Unknown axiom record: ' + line)
            axioms = match[3].split(', ') if match[3] else []
            if not set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}:
                raise ValueError('Unapproved boundary axiom')
            audits[match[1]] = axioms
        if set(audits) != set(names):
            raise ValueError('Incomplete boundary audit')
    if (author / 'SOURCES.json').read_bytes() != manifest_data:
        raise ValueError('Source manifest changed during replay')
    for name, digest in sources.items():
        if sha((author / name).read_bytes()) != digest:
            raise ValueError('Author source changed during replay: ' + name)
    report = dict(status='pass', source_manifest_sha256=sha(manifest_data),
                  author_sources=sources, authenticated_origins=imports,
                  author_audits=len(author_report['audits']),
                  author_observations=len(author_report['observations']),
                  author_false_claim_controls=author_report['negative_controls'],
                  boundary_audits=audits, commands=commands,
                  review_sources={name: sha((ROOT / name).read_bytes())
                                  for name in ['check_review.py', 'Boundaries.lean']},
                  temporary_sources_and_builds_removed=True)
    (out / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"PASS: {report['author_audits']} author audits, {report['author_observations']} observations, "
          f"{len(report['author_false_claim_controls'])} false-claim controls, {len(audits)} independent boundary proofs")


if __name__ == '__main__':
    main()
