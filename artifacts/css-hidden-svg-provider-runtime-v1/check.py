import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(mapping, root):
    for name, digest in mapping.items():
        path = root / name
        assert path.is_file() and not path.is_symlink() and sha(path) == digest, name

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

settings = read(HERE / 'CONFIG.json')
assert settings['ready_for_execution'] is False
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
for name in ('run.py', 'validate.py', 'check.py'):
    compile((HERE / name).read_text(), name, 'exec')
script = ast.parse((HERE / 'run.py').read_text())
node = next(n for n in script.body if isinstance(n, ast.FunctionDef) and n.name == 'restored_epoch')
namespace = dict(ROOT=ROOT, read=read, sha=sha, authenticate=authenticate, load=load)
exec(compile(ast.Module(body=[node], type_ignores=[]), 'run.py', 'exec'), namespace)
epoch = ROOT / settings['epoch']
assert sha(epoch / 'FILES.json') == settings['epoch_manifest_sha256']
authenticate(read(epoch / 'FILES.json'), epoch)
expected, pins, config, owned = namespace['restored_epoch'](epoch)
assert len(expected['sources']) == 49 and len(pins) == 337
assert len(owned) == len(config['existing_tests']) == 2 and config['install'] == {}
assert len(config['modified_native_paths']) == 26
proposal = ROOT / settings['proposal']
assert sha(proposal / 'FILES.json') == '5b2b762fdf3424332c9f3a8e662ea0a5270be1c685618bb0d6a34f2bb81e4b7d'
authenticate(read(proposal / 'FILES.json'), proposal)
assert all((HERE / n).read_bytes() == (proposal / n).read_bytes() for n in ('probe.html', 'validate.py'))
assert not any((HERE / n).exists() for n in ('STATE.json', 'capture', 'BEFORE.json', 'FINAL.json', 'SUMMARY.json'))
receipt = {'disabled': True, 'syntax_valid': True, 'historical_epoch_authenticated': True,
           'source_guards': len(expected['sources']), 'historical_pins': len(pins),
           'native_modified_paths': len(config['modified_native_paths']),
           'installed_tests_read_only': len(owned), 'install': config['install'],
           'exact_svg_fixture_and_validator': True, 'browser_executed': False,
           'live_source_index_binary_checks_executed': False}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
