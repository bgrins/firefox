import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(root, here, output, policy, env, verify, owned, cancelled):
    wpt = load('broader_wpt',here / 'wpt.py')
    comparison = load('broader_comparison',here / 'comparison.py')
    assert policy['reduced_binding'] and policy['phases']['reduced']
    initial = verify()
    wpt.save(output / 'PHASES-PRE.json',initial)
    results, app = {}, None
    for kind in ('normative','reftest','inactive','restyles','reduced'):
        if kind == 'restyles':
            restyles = load('broader_restyles',here / 'restyles.py')
            results[kind] = restyles.run(root,output / 'restyles',policy,env,verify,owned,cancelled,app)
            assert not owned and verify() == initial
            continue
        current = dict(policy,wpt=policy['phases'][kind],phase_kind=kind)
        original = comparison.original_directory(root,current)
        phase = output / (kind + '-wpt')
        results[kind] = wpt.run(root,here,phase,'candidate',current,env,verify,owned,cancelled,original)
        assert not owned and read(phase / 'PRE.json') == read(phase / 'POST.json') == initial
        metadata = read(phase / 'APPLICATION-METADATA.json')
        assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
        if app is None:
            app = metadata
        assert app == metadata
        assert read(phase / 'BINARY-PINS.json') == read(output / 'candidate-build/RESULT.json')['binaries']
    assert not owned and verify() == initial
    wpt.save(output / 'PHASES-POST.json',initial)
    return results
