import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
commands=[]
def run(name,args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180);(OUT/(name+'.log')).write_text(r.stdout+r.stderr);commands.append({'name':name,'args':list(map(str,args)),'exit':r.returncode});(OUT/'scan-build-commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0,(name,r.stderr)
run('extract-admission',[sys.executable,ROOT/'native/extract-admission.py'])
run('extract-scan',[sys.executable,ROOT/'native/extract-scan.py'])
run('compile-scan',['/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++','-std=c++20','-isysroot','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk','-isystem','/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1','-O1','-g','-fsanitize=undefined',OUT/'scan.cpp','-o',OUT/'scan'])
