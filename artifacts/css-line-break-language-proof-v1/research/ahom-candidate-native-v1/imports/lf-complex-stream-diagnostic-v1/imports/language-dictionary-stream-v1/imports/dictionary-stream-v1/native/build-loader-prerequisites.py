import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full';OUT.mkdir(parents=True,exist_ok=True)
BRIDGE=ROOT/'provider-bridge-v1';SDK=Path('/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk');CLANG='/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++'
commands=[]
def run(name,args):
 args=list(map(str,args));r=subprocess.run(args,capture_output=True,text=True,timeout=180);(OUT/(name+'.log')).write_text(r.stdout+r.stderr);commands.append({'name':name,'args':args,'exit':r.returncode});(OUT/'loader-prerequisites.json').write_text(json.dumps(commands,indent=2)+'\n');print(name,r.returncode,flush=True);assert r.returncode==0,(name,r.stdout,r.stderr)
for name in ['unicode','provider','locale','glyph']:
 run('extract-'+name,[sys.executable,BRIDGE/f'native/extract-{name}.py'])
for name in ['transform','range-providers','stream']:
 run('extract-'+name,[sys.executable,ROOT/f'native/extract-{name}.py'])
flags=[CLANG,'-std=c++20','-isysroot',SDK,'-isystem',SDK/'usr/include/c++/v1','-O1','-g','-fsanitize=undefined','-I',OUT,'-I',ROOT/'native','-I',BRIDGE/'development-build/provider','-I',BRIDGE/'provider-crates/icu_capi/bindings/cpp','-I',BRIDGE/'source/providers/intl/icu/source/common','-I',BRIDGE/'native/hyphen-producer-input','-I',BRIDGE/'native']
for name in ['provider','locale']:
 run('compile-'+name,[*flags,'-c',BRIDGE/f'native/{name}-library.cpp','-o',OUT/f'{name}.o'])
