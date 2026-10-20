import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TRUSTED_SOURCE_PINS = {'original/nsLayoutUtils.cpp': '4c8af5a446595014cbd2718436af2da40ac33721a24f987cb3ef0ea16a5fc6e1', 'original/DOMRect.cpp': '7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5', 'candidate/nsLayoutUtils.cpp': '4cdfa396de48968c0598d8252599f216ff9a0838771c5d7b44164c316e54fd05', 'candidate/DOMRect.cpp': '340a676a79f33faa6f6243bd1c5af4c4bba99310142ee0b24a6ecbf2da1bfc9e', 'providers/RelativeTo.h': '18a5af5345f70c44f0a8203d5e8cb51a1a55f0a52ee0ab0324f377b7acc9918b', 'providers/DOMRect.h': '2874c65025dac6c0291bd63b98c459d7b7e359d7e8c2a11b20231c43fd4d6cc8', 'providers/CheckedInt.h': '87929406797868021f19b3db5949463f5a1038dfe7de69b968a99b5a3c7dcd58', 'providers/nsIFrame.cpp': 'd5040d4caffa237141a2d76aa2964f1e1b0046ac2abea3f18b34763dafd4b316', 'providers/nsCoord.h': '3a88c7bd12e238ec8f76711a3121313c779179567500f83f5fee32cb6d361343', 'providers/nsIFrame.h': '75c701ea858955468d5c5dc8ebbde16be17845a5fcc454279502156b50efb5d2', 'providers/nsLayoutUtils.h': '826ed6b4f2e576b505a35e46f2add1b8b4c6f26a203827978276c2731bfc2bfc', 'include/mozilla/Assertions.h': '15fd622fe0592e00e1dbee77e19d968158a283f76c1b77b9efd24da52a860580', 'include/mozilla/Types.h': '88970f13f974a52e7cd70f30bb19c65bd063aab99f8565822afdcfc63e3728e1', 'include/mozilla/Attributes.h': '527c4e5203e77cb334970407546a60aeb9bcc189a24d466b91fdb2d2c0f5f9d4', 'include/mozilla/MacroArgs.h': 'de52abf49d91971f2c8487730ec2edd321a57d4334b7bf4a00307ebba8ad5879', 'include/mozilla/CheckedInt.h': '87929406797868021f19b3db5949463f5a1038dfe7de69b968a99b5a3c7dcd58', 'include/mozilla/Likely.h': 'ddf2022fde669f2325b967f6a84094478304f10124a664fd64874a2ed19dd8af', 'include/mozilla/CheckedArithmetic.h': 'bba42f0614eadf19f0777c1cbeb94f8c21a73e9dce0dfc4d85b5d016d780dfb7', 'include/mozilla/Fuzzing.h': 'f50c84bd473f6c561c95461efabaf43273900aa614a03bba1f440c97e236e1b1', 'include/mozilla/StaticAnalysisFunctions.h': '24b4edd0ef56db1bfdeb6b2333d6aeb027daa126ab45b1f0f6027593ddc1d802'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    manifest = json.loads((ROOT/'FILES.json').read_text())
    freeze = json.loads((ROOT/'FREEZE.json').read_text())
    assert digest(ROOT/'FILES.json') == freeze['FILES_sha256'], 'FREEZE'
    paths = [r['path'] for r in manifest['files']]
    assert len(paths) == len(set(paths)) == freeze['payload_count'], 'ROSTER_DUPLICATE'
    for name in paths:
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts, 'PATH'
    expected_files = set(paths) | {'FILES.json', 'FREEZE.json'}
    expected_dirs = {str(p) for f in expected_files for p in Path(f).parents if str(p) != '.'}
    actual_files, actual_dirs = set(), set()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(), 'SYMLINK'
        rel = str(path.relative_to(ROOT))
        assert '__pycache__' not in path.relative_to(ROOT).parts and path.suffix not in ('.pyc', '.olean', '.o'), 'CACHE_OR_COMPILER_PRODUCT'
        if path.is_file(): actual_files.add(rel)
        elif path.is_dir(): actual_dirs.add(rel)
        else: raise AssertionError('SPECIAL_FILE')
    assert actual_files == expected_files, 'CLOSED_FILES'
    assert actual_dirs == expected_dirs, 'CLOSED_DIRECTORIES'
    for row in manifest['files']:
        path = ROOT/row['path']
        assert path.stat().st_size == row['bytes'], 'SIZE'
        assert digest(path) == row['sha256'], 'HASH'
    for path, pin in TRUSTED_SOURCE_PINS.items():
        assert digest(ROOT/path) == pin, 'SOURCE_ROLE_PIN'
    print(json.dumps({'verified': len(paths), 'source_roles': len(TRUSTED_SOURCE_PINS)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay-out', type=Path)
    args = parser.parse_args()
    verify()
    if args.replay_out:
        output = args.replay_out.resolve()
        assert output != ROOT and ROOT not in output.parents, 'REPLAY_OUTSIDE_CAPSULE'
        subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT/'calibrate.py'), str(output)], check=True)
