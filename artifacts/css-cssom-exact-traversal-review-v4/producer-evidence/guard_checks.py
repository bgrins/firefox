import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
CAPSULE = ROOT / 'capsule'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def reseal(root):
    files = {p.relative_to(root).as_posix(): sha(p)
             for p in sorted(root.rglob('*')) if p.is_file()
             and p.relative_to(root).as_posix() not in ['FILES.json', 'FREEZE.json']}
    (root / 'FILES.json').write_text(json.dumps(files, indent=2) + '\n')
    pin = sha(root / 'FILES.json')
    (root / 'FREEZE.json').write_text(json.dumps(
        {'files_sha256': pin, 'payload_count': len(files)}, indent=2) + '\n')
    return pin

def main():
    records = []
    names = ['wrong-pin', 'extra-directory', 'changed-source', 'inside-output',
             'optimized', 'double-optimized', 'nonisolated-shadow',
             'site-enabled', 'source-symlink', 'wrong-driver-pin']
    for name in names:
        with tempfile.TemporaryDirectory(prefix='css-v4-guard-') as temp:
            work = Path(temp)
            source = work / 'capsule'
            shutil.copytree(CAPSULE, source)
            output = work / 'output'
            pin = sha(source / 'FILES.json')
            modes = ['-I', '-S']
            marker = work / 'SHADOW-EXECUTED'
            if name == 'wrong-pin': pin = '0' * 64
            if name == 'extra-directory': (source / '__pycache__').mkdir()
            if name == 'changed-source':
                with (source / 'candidate/nsIFrame.cpp').open('a') as f: f.write('\n')
            if name == 'inside-output': output = source / 'output'
            if name == 'optimized': modes.append('-O')
            if name == 'double-optimized': modes.append('-OO')
            if name == 'nonisolated-shadow':
                modes = ['-S']
                (source / 'json.py').write_text('open(' + repr(str(marker)) + ', "w").write("executed")\n')
            if name == 'site-enabled': modes = ['-I']
            if name == 'source-symlink':
                target = source / 'facade.cpp'
                copied = work / 'facade.cpp'
                target.rename(copied)
                target.symlink_to(copied)
            if name == 'wrong-driver-pin':
                p = source / 'TOOLCHAIN.json'
                tool = json.loads(p.read_text())
                tool['compiler_sha256'] = '0' * 64
                p.write_text(json.dumps(tool, indent=2) + '\n')
                pin = reseal(source)
            command = [sys.executable, *modes, str(source / 'replay.py'),
                       '--files-sha256', pin, str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            assert result.returncode != 0 and not output.exists() and not marker.exists(), name
            records.append({'name': name, 'command': command, 'exit': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr,
                            'output_created': False, 'shadow_executed': False})
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
