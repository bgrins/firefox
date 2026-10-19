import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"development-build/full"
BRIDGE=ROOT/"provider-bridge-v1"
TOOL=Path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr")
SDK=Path("/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk")
records=[]
def run(name,args):
    args=list(map(str,args))
    result=subprocess.run(args,capture_output=True,text=True,timeout=120)
    (OUT/(name+".log")).write_text(result.stdout+result.stderr)
    records.append({"name":name,"args":args,"exit":result.returncode})
    (OUT/"stream-build-commands.json").write_text(json.dumps(records,indent=2)+"\n")
    print(name,result.returncode,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
run("extract-stream",[sys.executable,ROOT/"native/extract-stream.py"])
flags=[TOOL/"bin/clang++","-std=c++20","-isysroot",SDK,"-isystem",TOOL/"include/c++/v1","-g","-O1","-fsanitize=undefined","-I",OUT,"-I",ROOT/"native","-I",BRIDGE/"development-build/provider","-I",BRIDGE/"provider-crates/icu_capi/bindings/cpp","-I",BRIDGE/"source/providers/intl/icu/source/common","-I",BRIDGE/"native/hyphen-producer-input","-I",BRIDGE/"native"]
libs=[OUT/"provider.o",OUT/"locale.o",ROOT/"development-build/icu/debug/liblanguage_break_provider.a",ROOT/"development-build/rust/libmapped_hyph.a","-licucore","-framework","CoreFoundation","-framework","Security"]
for flavor in ["original","candidate","standalone"]:
    run("compile-stream-"+flavor,[*flags,OUT/f"stream-{flavor}.cpp",*libs,"-o",OUT/f"stream-{flavor}"])
for name in ["provider-reference","locale-reference"]:
    run("compile-"+name,[*flags,ROOT/f"stream-model-v1/native/{name}.cpp",ROOT/"development-build/icu/debug/liblanguage_break_provider.a","-licucore","-framework","CoreFoundation","-framework","Security","-o",OUT/name])
run("compile-dictionary-reference",[*flags,ROOT/"native/dictionary-reference.cpp",ROOT/"development-build/rust/libmapped_hyph.a","-o",OUT/"dictionary-reference"])
