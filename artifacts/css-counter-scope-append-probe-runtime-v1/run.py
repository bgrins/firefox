import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import types

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OBJ = ROOT / 'objdir-full.noindex'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(OBJ), MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZ_HEADLESS='1', PYTHONDONTWRITEBYTECODE='1')
FIXTURE = 'testing/web-platform/tests/css/css-contain/counter-scoping-append-invalidation.html'
SOURCE = ROOT / 'artifacts/css-counter-scope-append-adjacent-audit-v1/counter-scoping-append-invalidation.html'
stopped = False


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def stop(signum, frame):
    global stopped
    stopped = True


def main():
    h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
    controller = load('quote_controller', 'artifacts/css-quote-scope-append-coc-runtime-v2/compare.py')
    tests = load('counter_tests', str((HERE / 'tests.py').relative_to(ROOT)))
    processes = load('counter_processes', str((HERE / 'process_control.py').relative_to(ROOT)))
    epoch = json.loads((ROOT / 'artifacts/css-local-signing-20261027-v6/CURRENT-EPOCH.json').read_text())
    before = a.verify_current(h, ROOT, ENV, epoch)
    save('BEFORE.json', before)
    need(not (ROOT / FIXTURE).exists() and not (ROOT / FIXTURE).is_symlink(), 'new fixture absent')
    need(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '7ff43e6c250949fe9b092b9e0059884d7ca0b8d74f800f864fcd8e988246b3bc', 'reviewed diagnostic body')
    with (ROOT / FIXTURE).open('xb') as stream:
        stream.write(SOURCE.read_bytes())
    current = copy.deepcopy(epoch)
    additions = {FIXTURE, FIXTURE + '.headers',
                 'testing/web-platform/meta/css/css-contain/counter-scoping-append-invalidation.html.ini',
                 'layout/base/nsCounterManager.cpp', 'layout/base/nsCounterManager.h'}
    parent = Path(FIXTURE).parent
    while str(parent).startswith('testing/web-platform/tests'):
        additions.add(str(parent / '__dir__.headers'))
        parent = parent.parent
    for name in additions:
        value = h.fingerprint(ROOT, name)
        need(name not in current['pins'] or current['pins'][name] == value, 'consistent new role')
        current['pins'][name] = value
    current['counts']['roles'] = len(current['pins'])
    a.verify_current(h, ROOT, ENV, current)
    save('INSTALLED-EPOCH.json', current)
    test = '/css/css-contain/counter-scoping-append-invalidation.html'
    names = [f'{op}; {mode}; nested={nested}; trailing={trailing}'
             for op in ['reset', 'set', 'increment'] for mode in ['single', 'stack']
             for nested in ['false', 'true'] for trailing in ['false', 'true']]
    config = {'tests': [test[1:]], 'expected_subtests': {test: names},
              'reftests': [], 'expected_end_only': {}, 'guard_sources': list(current['pins'])}
    save('CONFIG.json', config)
    flags = {label: controller.index_flags(h, repo, ENV)
             for label, repo in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    adapter = types.SimpleNamespace(CONFIG=config, HERE=HERE, ROOT=ROOT, ENV=ENV,
        PYTHON='/Users/bgrins/venvs/firefox/bin/python',
        BINARY=OBJ / 'dist/Nightly.app/Contents/MacOS/firefox',
        BINARIES=controller.BINARY_ROLES,
        WPT_CONFIG=OBJ / '_tests/web-platform/wptrunner.local.ini',
        PREFS_ROOT=ROOT / 'testing/profiles',
        pins=lambda names: {n: h.fingerprint(ROOT, n) for n in names},
        need=need, cancelled=lambda: stopped, owned_group=None, process_control=processes)
    error = None
    result = None
    try:
        controller.ports_free(json.loads((ROOT / 'testing/web-platform/tests/config.json').read_text()))
        result = tests.run(adapter, 'observation', current['pins'])
    except BaseException as failure:
        error = repr(failure)
    finally:
        state = h.index_state(ROOT, ENV)
        need(h.semantic_index(state) == current['semantic_index'], 'root semantics preserved')
        for label, repo in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            need(controller.index_flags(h, repo, ENV) == flags[label], 'index flags preserved')
        current['raw_index_observation']['current'] = state['raw_index']
        after = a.verify_current(h, ROOT, ENV, current)
        save('AFTER.json', after)
        save('CURRENT-EPOCH.json', current)
        save('RESULT.json', {'error': error, 'success': error is None,
            'counts': {status: sum(r['status'] == status for r in result['rows'])
                       for status in ['PASS', 'FAIL']} if result else None,
            'owned_group_absent': adapter.owned_group is None,
            'native_changed': False, 'accepted_fix': False,
            'raw_index_changed': before['index']['raw_index'] != state['raw_index'],
            'raw_index_change_cause_established': False})
    need(error is None, error)


if __name__ == '__main__':
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    main()
