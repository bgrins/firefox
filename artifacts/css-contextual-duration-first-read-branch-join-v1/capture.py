import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'artifacts/css-contextual-duration-first-read-flush-review-v1'
REVISIONS = {
    'head': 'ecfe313d582a335c04d80bfd360fd3a591defdb7',
    'original': '20ab7e723b663c0f78c8490e60a6fccc5e65cc99',
}
FUNCTIONS = {
    'layout/base/PresShell.h': [
        'bool NeedFlush(FlushType aType, bool aFlushAnimations) const',
        'bool NeedFlush(const ChangesToFlush& aFlush) const',
        'void FlushPendingNotifications(FlushType aType)',
        'void FlushPendingNotifications(ChangesToFlush aType)',
    ],
    'layout/style/nsComputedDOMStyle.cpp': [
        'static bool ElementNeedsRestyle(',
        'bool nsComputedDOMStyle::NeedsToFlushStyle(',
        'void nsComputedDOMStyle::Flush(',
        'void nsComputedDOMStyle::UpdateCurrentStyleSources(',
    ],
    'dom/base/nsIContent.cpp': [
        'nsIFrame* nsIContent::GetPrimaryFrame(mozilla::FlushType aType)',
    ],
    'dom/base/nsIContent.h': [],
    'dom/base/Document.cpp': [
        'void Document::FlushPendingNotifications(mozilla::ChangesToFlush aFlush)',
    ],
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extract(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 0
    token = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]')
    for match in token.finditer(text, opening):
        if match[0] == '{':
            depth += 1
        elif match[0] == '}':
            depth -= 1
            if depth == 0:
                return text[start:match.end()]
    raise ValueError(f'incomplete function: {signature}')


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    excerpts = json.loads((PRIOR / 'UPSTREAM-EXCERPTS.json').read_text())
    queries = json.loads((PRIOR / 'SEARCHFOX-QUERIES.json').read_text())
    upstream = {path: [] for path in FUNCTIONS}
    upstream_file_hashes = {}
    for record in excerpts:
        path = record['command'][-1]
        if path in upstream:
            upstream[path].extend(record['excerpts'].values())
            upstream_file_hashes[path] = record['full_output_sha256']
    for query in queries:
        if 'nsComputedDOMStyle::' in query['query'] or 'nsIContent::GetPrimaryFrame' in query['query']:
            path = 'dom/base/nsIContent.cpp' if 'nsIContent' in query['query'] else 'layout/style/nsComputedDOMStyle.cpp'
            output = query['result']['value']['output']
            upstream[path].append('\n'.join(re.sub(r'^\s*(?:>>>)?\s*\d+: ?', '', line) for line in output.splitlines()))
    epoch_path = ROOT / 'artifacts/css-pow-special-value-promotion-runtime-1/final-build/EPOCH.json'
    epoch_data = epoch_path.read_bytes()
    assert sha(epoch_data) == 'be424e4a2b1e20ae32724e16b237cc674d83586dc77405b908cb2462a1ff5c33'
    pins = json.loads(epoch_data)['pins']
    results, bodies, commands = {}, {}, []
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    for path, signatures in FUNCTIONS.items():
        sources = {'current': (ROOT / path).read_bytes()}
        for role, revision in REVISIONS.items():
            command = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'show', f'{revision}:{path}']
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=True)
            assert not result.stderr
            sources[role] = result.stdout
            commands.append({'argv': command, 'exit_code': result.returncode, 'stdout_sha256': sha(result.stdout)})
        pin = pins.get(path)
        record = {
            'whole_files': {role: {'sha256': sha(body), 'bytes': len(body)} for role, body in sources.items()},
            'current_equals_head': sources['current'] == sources['head'],
            'head_equals_original': sources['head'] == sources['original'],
            'captured_upstream_whole_file_sha256': upstream_file_hashes.get(path),
            'captured_upstream_whole_file_equals_current': upstream_file_hashes.get(path) == sha(sources['current']) if path in upstream_file_hashes else None,
            'historical_build_pin': pin,
            'historical_build_pin_matches_current': pin == sha(sources['current']) if pin is not None else None,
            'functions': {},
        }
        if path == 'dom/base/nsIContent.h':
            declaration = 'nsIFrame* GetPrimaryFrame(mozilla::FlushType aType);'
            record['declaration'] = declaration
            record['declaration_present'] = {role: declaration in data.decode() for role, data in sources.items()}
        for signature in signatures:
            extracted = {role: extract(body.decode(), signature) if signature in body.decode() else None for role, body in sources.items()}
            matches = []
            for text in upstream[path]:
                try:
                    matches.append(extract(text, signature))
                except ValueError:
                    pass
            assert all(body == matches[0] for body in matches), signature
            fragments = [text for text in upstream[path] if signature in text]
            assert fragments, signature
            record['functions'][signature] = {
                'present': {role: body is not None for role, body in extracted.items()},
                'sha256': {role: sha(body.encode()) if body is not None else None for role, body in extracted.items()},
                'current_equals_head': extracted['current'] == extracted['head'] if extracted['current'] is not None else None,
                'head_equals_original': extracted['head'] == extracted['original'] if extracted['head'] is not None else None,
                'captured_upstream_sha256': sha(matches[0].encode()) if matches else None,
                'captured_upstream_equals_current': matches[0] == extracted['current'] if matches else None,
                'complete_upstream_function_available': bool(matches),
                'captured_fragments_found_verbatim_in_current': [text in sources['current'].decode() for text in fragments],
            }
            bodies[signature] = {'path': path, 'current_body': extracted['current']}
        results[path] = record
    write('SOURCE-JOIN.json', {'revisions': REVISIONS, 'files': results, 'commands': commands,
                              'extraction': 'From exact signature through balanced closing brace; excludes leading declaration indentation and trailing newline. Searchfox define line-number prefixes removed; no code whitespace normalization.'})
    write('FUNCTIONS.json', bodies)
    refs = [PRIOR / name for name in ('FILES.json', 'UPSTREAM-EXCERPTS.json', 'SEARCHFOX-QUERIES.json')]
    refs += [epoch_path, ROOT / 'layout/AGENTS.md', ROOT / 'layout/docs/LayoutOverview.md', ROOT / 'layout/docs/LayoutCodeReviewerChecklist.md']
    write('REFERENCES.json', {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in refs})
    print(json.dumps({path: {k: v for k, v in record.items() if k not in ('whole_files', 'functions')} for path, record in results.items()}, indent=2))
    print('Functions:', sum(len(record['functions']) for record in results.values()))


if __name__ == '__main__':
    main()
