import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        manifest = ROOT / name
        assert sha(manifest) == digest, name
        for rel, pin in json.loads(manifest.read_text()).items():
            assert sha(manifest.parent / rel) == pin, rel
    cases = json.loads((HERE / 'CASES.json').read_text())
    producers, consumers = cases['producer'], cases['consumer']
    assert len({c['id'] for c in producers}) == len(producers)
    assert len({c['id'] for c in consumers}) == len(consumers)
    producer_input = ''.join(c['id']+' '+c['mode']+' '+str(len(c['terms']))+' '+
                             ' '.join(f'{kind} {groups} {count}' for kind,groups,count in c['terms'])+'\n' for c in producers)
    consumer_input = ''.join(f"{c['id']} {c['mode']} {c['cap']} {c['stored']} {c['fill']}\n" for c in consumers)
    (out/'producer-input.txt').write_text(producer_input)
    (out/'consumer-input.txt').write_text(consumer_input)
    tools = {'rust':Path('/Users/bgrins/.cargo/bin/rustc'), 'cpp':Path('/usr/bin/clang++')}
    tool_receipts = {}
    for role, executable in tools.items():
        version = subprocess.check_output([str(executable),'--version'],text=True,timeout=10)
        tool_receipts[role] = {'path':str(executable),'sha256':sha(executable),'version':version}
    sysroot = Path(subprocess.check_output([str(tools['rust']),'--print','sysroot'],text=True,timeout=10).strip())
    tool_receipts['rust']['actual_rustc'] = str(sysroot/'bin/rustc')
    tool_receipts['rust']['actual_rustc_sha256'] = sha(sysroot/'bin/rustc')
    (out/'TOOLS.json').write_text(json.dumps(tool_receipts,indent=2)+'\n')
    def run(label, command, stdin=None):
        result = subprocess.run(command,input=stdin,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,
                                env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
        (out/(label+'.stdout')).write_text(result.stdout)
        (out/(label+'.stderr')).write_text(result.stderr)
        (out/(label+'.json')).write_text(json.dumps({'command':list(map(str,command)),'exit':result.returncode},indent=2)+'\n')
        assert result.returncode == 0 and not result.stderr, (label,result.returncode,result.stderr)
        return result.stdout
    output_maps = {}
    with tempfile.TemporaryDirectory(prefix='subgrid-cache-helpers-') as temporary:
        temp=Path(temporary)
        for opt in (0,2):
            rust_exe=temp/f'producer-{opt}'
            run(f'rust-build-{opt}',[str(tools['rust']),'--edition=2021','-C','overflow-checks=yes','-C',f'opt-level={opt}',str(HERE/'producer.rs'),'-o',str(rust_exe)])
            rust_output=run(f'rust-run-{opt}',[str(rust_exe)],producer_input)
            cpp_exe=temp/f'consumer-{opt}'
            run(f'cpp-build-{opt}',[str(tools['cpp']),'-std=c++17',f'-O{opt}','-fsanitize=undefined,integer','-fno-sanitize-recover=all','-fno-omit-frame-pointer',str(HERE/'consumer.cpp'),'-o',str(cpp_exe)])
            cpp_output=run(f'cpp-run-{opt}',[str(cpp_exe)],consumer_input)
            rust_lines=rust_output.splitlines();cpp_lines=cpp_output.splitlines()
            assert rust_lines.pop(0)==cpp_lines.pop(0)=='host_bits 64'
            assert len(rust_lines)==len(producers) and len(cpp_lines)==len(consumers)
            actual_p={};actual_c={}
            for line,case in zip(rust_lines,producers):
                identity,value=line.split();assert identity==case['id'];value=int(value)
                exact=sum(1 if kind==0 else groups*count if kind==1 else 0 for kind,groups,count in case['terms'])
                expected=min(2**case['width']-1,exact)
                assert exact==case['total'] and expected==case['expected_cache']==value
                actual_p[identity]=value
            for line,case in zip(cpp_lines,consumers):
                fields=line.split();assert fields.pop(0)==case['id'];values=list(map(int,fields))
                expected=max(0,case['cap']-case['stored'])
                assert values==case['expected']==[expected,expected%case['fill'],expected-expected%case['fill']]
                actual_c[case['id']]=values
            consumer_index={(c['mode'],c['cap'],c['stored'],c['fill']):c for c in consumers}
            for case in producers:
                for cap in (-1,3,2**31-1):
                    target=consumer_index[(case['mode'],cap,actual_p[case['id']],3)]
                    assert actual_c[target['id']][0]==max(0,cap-case['total'])
            output_maps[opt]=(actual_p,actual_c)
    assert output_maps[0]==output_maps[2]
    INTMAX=2**31-1
    def old_math(cap,cache):
        low=cache%2**32
        narrowed=low if low<2**31 else low-2**32
        difference=cap-narrowed
        defined=-2**31<=difference<=INTMAX
        return {'cache':cache,'narrowed_modulo_model':narrowed,'exact_signed_subtraction':difference,
                'signed_subtraction_representable':defined,'old_remaining_if_representable':max(0,difference) if defined else None}
    old_rows=[{'id':case['id'],'mode':case['mode'],'cap':case['cap'],**old_math(case['cap'],case['stored'])} for case in consumers]
    (out/'OLD-MATHEMATICAL-CLASSIFICATION.json').write_text(json.dumps(old_rows,indent=2)+'\n')
    witnesses=[]
    for label,terms in [('INTMAX-times-two',[(1,2,INTMAX)]),('1431655766-times-three',[(1,3,1431655766)]),('INTMAX-times-two-plus-two',[(1,2,INTMAX),(0,1,1),(0,1,1)])]:
        term_lists=[list(t) for t in terms]
        by_mode={c['mode']:c for c in producers if c['terms']==term_lists}
        assert set(by_mode)=={'width32','width64','host'}
        total=by_mode['host']['total']
        assert old_math(3,total)['signed_subtraction_representable']
        witnesses.append({'label':label,'terms':terms,'exact_total':total,'new_remaining_at_cap3':0,
                          'widths':{mode:{'case_id':case['id'],'cache':actual_p[case['id']]} for mode,case in by_mode.items()},
                          'old64':old_math(3,total),'old32_product_or_sum_exceeds_width':total>2**32-1})
    assert [w['old64']['old_remaining_if_representable'] for w in witnesses]==[5,1,3]
    assert old_math(3,2**31)['signed_subtraction_representable'] is False
    assert old_math(-2**31,1)['signed_subtraction_representable'] is False
    (out/'WITNESSES.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    negative_controls={'wrap_before_cap_product':min(INTMAX,(INTMAX*3)%2**32)!=min(INTMAX,INTMAX*3),
                       'wrap_prefix_sum':((INTMAX*2+2)%2**32)!=min(2**32-1,INTMAX*2+2),
                       'saturate_without_consumer_guard':old_math(3,2**64-1)['old_remaining_if_representable']!=0}
    assert all(negative_controls.values())
    result={'status':'PASS','optimizations':[0,2],'rust_overflow_checks':True,'cpp_sanitizers':['undefined','integer'],
            'all_run_and_compile_stderr_empty':True,'host_pointer_bits':64,'fixed_width_facades':[32,64],
            'actual_32_bit_target_compiled':False,'producer_cases_per_optimization':len(producers),
            'consumer_cases_per_optimization':len(consumers),'producer_consumer_joins_per_optimization':len(producers)*3,
            'output_maps_equal_across_optimizations':True,'negative_controls':negative_controls,
            'old_subtraction_native_executions':0,'old_mathematically_unrepresentable_rows':sum(not c['signed_subtraction_representable'] for c in old_rows),
            'temporary_products_removed':True,'full_native_pipeline':False,'source_refinement_proved':False}
    (out/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
