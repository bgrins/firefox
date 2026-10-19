import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
args=['/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++','-std=c++20','-isysroot','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk','-isystem','/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1','-O1','-g','-fsanitize=undefined',ROOT/'native/dictionary-reference.cpp',ROOT/'development-build/rust/libmapped_hyph.a','-o',OUT/'dictionary-reference']
r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120);(OUT/'dictionary-reference-build.log').write_text(r.stdout+r.stderr);(OUT/'dictionary-reference-build.json').write_text(json.dumps({'args':list(map(str,args)),'exit':r.returncode},indent=2)+'\n');raise SystemExit(r.returncode)
