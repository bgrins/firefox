import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, json, shutil, subprocess
from pathlib import Path
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists() and not out.is_relative_to(R)
out.mkdir(parents=True)
receipts = []
for mode in ['changed-lean', 'shadow-module', 'symlink', 'duplicate', 'escape']:
    copy = out / mode
    shutil.copytree(R, copy)
    if mode == 'changed-lean':
        f = copy / 'lean/DeclarationCurly.lean'
        f.write_text(f.read_text() + '\n-- mutation\n')
    elif mode == 'shadow-module':
        (copy / 'json.py').write_text('raise RuntimeError("shadow module executed")\n')
    elif mode == 'symlink':
        f = copy / 'lean/DeclarationCurly.lean'
        f.unlink()
        f.symlink_to(R / 'lean/DeclarationCurly.lean')
    else:
        f = copy / 'MANIFEST.json'
        records = json.loads(f.read_text())
        if mode == 'duplicate':
            records.append(records[0])
        else:
            records[0]['path'] = '../escape'
        f.write_text(json.dumps(records))
    replay = out / (mode + '-replay')
    result = subprocess.run([sys.executable, '-I', '-S', str(copy / 'check.py'), '--output', str(replay)], capture_output=True, text=True)
    assert result.returncode != 0 and not replay.exists()
    assert 'shadow module executed' not in result.stderr
    receipts.append(dict(mode=mode, exit=result.returncode, stdout=result.stdout, stderr=result.stderr, replay_started=False))
(out / 'RESULT.json').write_text(json.dumps(receipts, indent=2) + '\n')
print(json.dumps(dict(rejected=len(receipts), replay_started=False)))
