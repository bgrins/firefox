import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'development-build/full'
OUT.mkdir(parents=True, exist_ok=True)
BRIDGE = ROOT / 'provider-bridge-v1'
TOOL = Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr')
SDK = Path('/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk')
commands = [
    [sys.executable, BRIDGE / 'native/extract-unicode.py'],
    [sys.executable, ROOT / 'native/extract-transform.py'],
    [TOOL / 'bin/clang++', '-std=c++20', '-isysroot', SDK, '-isystem', TOOL / 'include/c++/v1', '-g', '-O1', '-fsanitize=undefined', '-I', BRIDGE / 'source/providers/intl/icu/source/common', OUT / 'transform.cpp', '-licucore', '-o', OUT / 'transform'],
    [sys.executable, ROOT / 'check-transform-development.py'],
]
receipts = []
for i, args in enumerate(commands):
    args = list(map(str, args))
    run = subprocess.run(args, capture_output=True, text=True, timeout=60)
    (OUT / f'transform-stage-{i}.log').write_text(run.stdout + run.stderr)
    receipts.append({'args':args,'exit':run.returncode})
    (OUT / 'transform-build-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(i,run.returncode,flush=True)
    if run.returncode:
        raise SystemExit(run.returncode)
