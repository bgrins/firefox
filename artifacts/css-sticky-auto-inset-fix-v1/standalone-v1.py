import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CPP = 'layout/generic/StickyScrollContainer.cpp'
TEST = 'testing/web-platform/tests/css/css-position/sticky/position-sticky-auto-inset-reduction.html'
BASES = ['32226ddf3a29d58a52291babebdff2a5a7ce46c6',
         '11482ee213bf63c749b6d205c2c7591d783bdaa8']
patch = ''.join(difflib.unified_diff((OUT / 'StickyScrollContainer-before.cpp').read_text().splitlines(True), (ROOT / CPP).read_text().splitlines(True), fromfile='a/' + CPP, tofile='b/' + CPP))
(OUT / 'native-combined-v1.patch').write_text(patch)
patch += ''.join(difflib.unified_diff([], (ROOT / TEST).read_text().splitlines(True),
                                    fromfile='/dev/null', tofile='b/' + TEST))
(OUT / 'fix-candidate-v1.patch').write_text(patch)
results = []
for revision in BASES:
    original = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show',
                                        revision + ':' + CPP], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='sticky-auto-standalone-') as directory:
        temp = Path(directory)
        path = temp / CPP
        path.parent.mkdir(parents=True)
        path.write_bytes(original)
        subprocess.run(['git', 'apply', '--check', '-'], input=patch.encode(), cwd=temp, check=True)
        subprocess.run(['git', 'apply', '-'], input=patch.encode(), cwd=temp, check=True)
        candidate = path.read_bytes()
        assert (temp / TEST).read_bytes() == (ROOT / TEST).read_bytes()
        subprocess.run(['git', 'apply', '--reverse', '-'], input=patch.encode(), cwd=temp, check=True)
        assert path.read_bytes() == original and not (temp / TEST).exists()
        hashes = {}
        for name, data in [(CPP, candidate), (TEST, (ROOT / TEST).read_bytes())]:
            dest = OUT / 'standalone-candidate-v1' / revision / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        results.append({'revision': revision, 'check_exit': 0, 'apply_exit': 0,
                        'reverse_restores_original': True,
                        'original_native_sha256': hashlib.sha256(original).hexdigest(),
                        'candidate_sha256': hashes, 'isolated_build_performed': False})
result = {'patch_sha256': hashlib.sha256(patch.encode()).hexdigest(),
          'files': [CPP, TEST], 'checks': results,
          'scope': 'Only auto-inset normalization and view-size reduction; standalone patch excludes existing sticky/view-timeline project changes. Browser gates run combined worktree.'}
(OUT / 'standalone-apply-v1.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
