import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONFIG = json.loads((HERE / 'CONFIG.json').read_text())
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', GIT_OPTIONAL_LOCKS='0',
           GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='core.fsmonitor', GIT_CONFIG_VALUE_0='false')
ENV.pop('MOZ_LOG', None)
ENV.pop('MOZ_LOG_FILE', None)
GIT = ['git', '-c', 'core.fsmonitor=false']
BINARIES = ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
            'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def command(name, args):
    with (HERE / (name + '.log')).open('w') as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + '.json', {'command': args, 'exit': result.returncode})
    return result.returncode

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('link', 'script', 'img'):
            value = attrs.get('href') or attrs.get('src')
            if value:
                self.links.append(value)

def resource_paths(tests, virtual=False):
    paths = set(tests + CONFIG['support_paths'])
    for test in tests:
        meta = ROOT / 'testing/web-platform/meta' / Path(test).relative_to('testing/web-platform/tests')
        paths.add(str(meta.relative_to(ROOT)) + '.ini')
        paths.update(str((parent / '__dir__.ini').relative_to(ROOT)) for parent in meta.parents
                     if parent == ROOT / 'testing/web-platform/meta'
                     or ROOT / 'testing/web-platform/meta' in parent.parents)
    pending = list(tests)
    scanned = set()
    while pending:
        name = pending.pop()
        if name in scanned:
            continue
        scanned.add(name)
        source = HERE / CONFIG['install'][name] if virtual and name in CONFIG['install'] else ROOT / name
        parser = Links()
        parser.links = []
        parser.feed(source.read_text())
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            rel = unquote(url.path)
            target = ((ROOT / 'testing/web-platform/tests' / rel.lstrip('/'))
                      if rel.startswith('/') else (ROOT / name).parent / rel).resolve()
            if ROOT not in target.parents:
                continue
            relative = str(target.relative_to(ROOT))
            exists = target.is_file() or (virtual and relative in CONFIG['install'])
            if not exists:
                continue
            paths.add(relative)
            if target.suffix in ('.html', '.xhtml'):
                pending.append(relative)
    return sorted(paths)

def pins(paths, virtual=False):
    result = {}
    for name in paths:
        path = HERE / CONFIG['install'][name] if virtual and name in CONFIG['install'] else ROOT / name
        result[name] = sha(path) if path.is_file() else None
    return result

def test_run(kind, tests, expected_resources):
    directory = HERE / kind
    directory.mkdir()
    resources = resource_paths(tests)
    need(set(resources) <= set(expected_resources), 'unprepared resource discovery')
    paths = sorted(set(resources + CONFIG['guard_sources'] + BINARIES))
    before = pins(paths)
    need(all(before[n] == h for n,h in expected_resources.items() if n in before), 'prepared test/resource pins')
    for name, pin in before.items():
        if pin is None or name in BINARIES:
            continue
        target = directory / 'inputs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    code = command(kind + '-wpt', ['./mach', 'wpt', '--headless', '--processes=1',
                   '--log-raw=' + str(directory / 'raw.json'), *tests])
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    rows = [r for r in events if r.get('action') == 'test_status']
    ends = [r for r in events if r.get('action') == 'test_end']
    expected = {'/' + str(Path(t).relative_to('testing/web-platform/tests')) for t in tests}
    complete = (code in (0,1) and len(ends) == len(tests) and {r['test'] for r in ends} == expected
                and len({(r['test'],r['subtest']) for r in rows}) == len(rows)
                and all(r['test'] in expected and r['status'] in ('PASS','FAIL') for r in rows)
                and all(r['status'] == 'OK' for r in ends)
                and sum(r.get('action') == 'suite_end' for r in events) == 1)
    for test in expected:
        complete = complete and [r['subtest'] for r in rows if r['test'] == test] == CONFIG['expected_subtests'][test]
    result = {'exit':code,'complete':complete,'before':before,'after':pins(paths),'rows':rows,'ends':ends}
    (directory/'RUN.json').write_text(json.dumps(result,indent=2)+'\n')
    need(complete and before == result['after'], 'complete exact roster/stable pins')
    return {'exit':code,'complete':complete,'subtests':len(rows),'files':len(ends)}

def snapshot():
    return {'head':git('rev-parse','HEAD').decode().strip(),
            'index_diff_sha256':hashlib.sha256(git('diff','--cached','--binary')).hexdigest(),
            'index_entries_sha256':hashlib.sha256(git('ls-files','--stage','-z')).hexdigest(),
            'native_diff_sha256':hashlib.sha256(git('diff','--binary','--','layout','dom','servo')).hexdigest(),
            'sources':pins(CONFIG['guard_sources'])}
