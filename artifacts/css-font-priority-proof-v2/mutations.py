import argparse
import json
from pathlib import Path
import bridge
import cases
import provider_oracle
import run

BASE=Path(__file__).resolve().parent


def replace_one(source,old,new):
    assert source.count(old)==1,(old,source.count(old))
    return source.replace(old,new)


def mutated(source,name):
    if name in ('weighted-addition','float-combined-key'):
        cast='float' if name=='float-combined-key' else 'double'
        for relation in ('<','=='):
            old=f'return mKey {relation} aOther.mKey;'
            expr=lambda key:f'{cast}(std::get<1>({key}) * 100000000.0 + std::get<2>({key}) * 10000.0 + std::get<3>({key}))'
            new=f'return std::make_tuple(std::get<0>(mKey), {expr("mKey")}) {relation} std::make_tuple(std::get<0>(aOther.mKey), {expr("aOther.mKey")});'
            source=replace_one(source,old,new)
    elif name=='swap-width-style':source=replace_one(source,'mKey(0, aWidth, aStyle, aWeight)','mKey(0, aStyle, aWidth, aWeight)')
    elif name=='swap-style-weight':source=replace_one(source,'mKey(0, aWidth, aStyle, aWeight)','mKey(0, aWidth, aWeight, aStyle)')
    elif name=='float-coordinates':source=replace_one(source,'mKey(0, aWidth, aStyle, aWeight)','mKey(0, float(aWidth), float(aStyle), float(aWeight))')
    elif name=='sentinel-rank-zero':source=replace_one(source,'mKey{2, 0.0, 0.0, 0.0}','mKey{0, 0.0, 0.0, 0.0}')
    elif name=='drop-presentation':source=replace_one(source,'std::get<0>(mKey) = 1;','std::get<0>(mKey) = 0;')
    elif name=='mismatched-zero-perfect':source=replace_one(source,'return mKey == std::make_tuple(0, 0.0, 0.0, 0.0);','return std::get<1>(mKey) == 0.0 && std::get<2>(mKey) == 0.0 && std::get<3>(mKey) == 0.0;')
    elif name=='shared-nonstrict':
        old=bridge.block(source,'void Family::SearchAllFontsForChar(')
        new=replace_one(old,'if (distance < aMatchData->mMatchDistance) {','if (!(aMatchData->mMatchDistance < distance)) {')
        source=replace_one(source,old,new)
    elif name in ('drop-equal','remove-clearing','reverse-unshared'):
        old=bridge.block(source,'void gfxFontFamily::FindAllFontsForStyle(')
        if name=='drop-equal':new=replace_one(old,'} else if (distance == minDistance) {','} else if (false && distance == minDistance) {')
        elif name=='remove-clearing':new=replace_one(old,'aFontEntryList.Clear();','(void)0;')
        else:new=replace_one(old,'for (uint32_t i = count; i > 0;) {\n    fe = mAvailableFonts[--i];','for (uint32_t i = 0; i < count;) {\n    fe = mAvailableFonts[i++];')
        source=replace_one(source,old,new)
    else:raise ValueError(name)
    assert source!=bridge.generate('A',(BASE/'driver.cpp').read_text())
    return source


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(BASE/'mutation-development'));args=p.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    tc=json.loads((BASE/'support_b/TOOLCHAIN-v1.json').read_text())
    all_cases=cases.generate();source=bridge.generate('A',(BASE/'driver.cpp').read_text())
    requested={
        'weighted-addition':'mutation-width-priority:1',
        'swap-width-style':'mutation-width-priority:1',
        'swap-style-weight':'mutation-style-priority:1',
        'float-combined-key':'mutation-float-key:1',
        'sentinel-rank-zero':'provider:mismatch-only:op=3',
        'drop-presentation':'global:mismatch-does-not-stop:op=11',
        'mismatched-zero-perfect':'global:mismatch-does-not-stop:op=11',
        'shared-nonstrict':'provider:tie:op=4',
        'drop-equal':'provider:tie:op=1',
        'remove-clearing':'provider:improvement-clears-ties:op=1',
        'reverse-unshared':'provider:tie:op=1',
    }
    results=[]
    for name,witness in requested.items():
        c=next(c for c in all_cases if c['name']==witness)
        binary=run.compile_native(mutated(source,name),name,out,tc)
        actual=run.execute(binary,[c],out,name)[0];expected=provider_oracle.expected(c,'A')
        assert actual['selected']!=expected['selected'],(name,expected,actual)
        if name=='float-combined-key':
            control=run.execute(out/'weighted-addition',[c],out,'exact-combined-key-control')[0]
            assert control==expected
            (out/'EXACT-COMBINED-CONTROL.json').write_text(json.dumps(dict(case=c,control=control,expected=expected),indent=2)+'\n')
        results.append(dict(name=name,case=c,expected=expected,mutant=actual,status='COMPILED-RAN-SEMANTIC-DIFFERENCE'))
        print(name,expected['selected'],'->',actual['selected'],flush=True)
    binary=run.compile_native(mutated(source,'float-coordinates'),'float-coordinates',out,tc)
    actual=run.execute(binary,all_cases,out,'float-coordinates')
    assert actual==[provider_oracle.expected(c,'A') for c in all_cases]
    (out/'MUTATIONS.json').write_text(json.dumps(results,indent=2)+'\n')
    (out/'FLOAT-COORDINATES.json').write_text(json.dumps(dict(status='SEMANTIC-NO-OP-ON-VALID-DOMAIN',cases=len(all_cases),reason='All helper distances are nonnegative multiples of 1/256 below 2048. Their scaled integers are below 2^19, within binary32 precision; widening them back to double changes no coordinate.'),indent=2)+'\n')

if __name__=='__main__':main()
