import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'development-build'
RUST=OUT/'hyphen-rust'
RUST.mkdir(exist_ok=True)
commands=[]


def run(name,args):
    args=list(map(str,args))
    r=subprocess.run(args,text=True,capture_output=True,timeout=120)
    (ROOT/'evidence'/f'{name}-development.log').write_text(r.stdout+r.stderr)
    commands.append(dict(name=name,args=args,exit=r.returncode))
    (ROOT/'evidence/DEVELOPMENT-COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode:
        print(r.stdout+r.stderr)
        raise SystemExit(r.returncode)
    print(name,'PASS',flush=True)


rustc=subprocess.check_output(['rustup','which','rustc'],text=True).strip()
for name,edition,extra in [
    ('arrayref','2015',[]),('log','2021',[]),
    ('libc','2021',['--cfg','feature="std"']),
    ('memmap2','2021',['--extern',f'libc={RUST}/liblibc.rlib']),
    ('mapped_hyph','2018',['--extern',f'arrayref={RUST}/libarrayref.rlib','--extern',f'log={RUST}/liblog.rlib','--extern',f'memmap2={RUST}/libmemmap2.rlib']),
]:
    final=name=='mapped_hyph'
    run('hyphen-rust-'+name,[rustc,'--edition',edition,'--crate-name',name,'--crate-type','staticlib' if final else 'rlib','-L',f'dependency={RUST}',ROOT/'hyphen-vendor'/name/'src/lib.rs','-o',RUST/('lib'+name+('.a' if final else '.rlib')),*extra])
for name in ['provider','locale','glyph','stream']:
    run('extract-'+name,[sys.executable,ROOT/f'native/extract-{name}.py'])
flags=['clang++','-std=c++20','-g','-O1','-fsanitize=undefined','-I',OUT/'provider','-I',ROOT/'provider-crates/icu_capi/bindings/cpp','-I',ROOT/'source/providers/intl/icu/source/common','-I',ROOT/'native/hyphen-producer-input','-I',ROOT/'native']
for name in ['provider','locale']:
    run('compile-'+name,[*flags,'-c',ROOT/f'native/{name}-library.cpp','-o',OUT/f'{name}.o'])
for flavor in ['original','candidate']:
    run('compile-stream-'+flavor,[*flags,OUT/f'stream/stream-{flavor}.cpp',OUT/'provider.o',OUT/'locale.o',OUT/'icu/debug/liblanguage_break_provider.a',RUST/'libmapped_hyph.a','-licucore','-framework','CoreFoundation','-framework','Security','-o',OUT/f'stream-{flavor}'])
