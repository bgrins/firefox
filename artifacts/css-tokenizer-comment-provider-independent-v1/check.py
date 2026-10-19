from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
PRODUCER_FREEZE='7b36017f4b4c711bd71c38deae9e20fc558c98b301b75f1aa3fb9f2eeb6c6179'
PRODUCER_MANIFEST='87786e24bb6d34c90661e4b7d4f82594547e0c08590c1ec3ca3a49b6cba4166b'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def body_end(source,start):
    i=source.index('{',start);depth=0
    while i<len(source):
        if source.startswith('//',i):
            end=source.find('\n',i);i=len(source) if end<0 else end;continue
        if source.startswith('/*',i):
            nested=1;i+=2
            while nested:
                if source.startswith('/*',i):nested+=1;i+=2
                elif source.startswith('*/',i):nested-=1;i+=2
                else:i+=1
                assert i<=len(source)
            continue
        if source[i]=='"':
            match=re.match(r'"(?:\\.|[^"\\])*"',source[i:],re.S)
            assert match
            i+=match.end();continue
        if source[i]=="'":
            match=re.match(r"'(?:\\(?:u\{[a-fA-F0-9]+\}|.)|[^'\\\n])'",source[i:])
            if match:i+=match.end();continue
        if source[i]=='{':depth+=1
        elif source[i]=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    raise AssertionError('unclosed body')

def independently_check(parent):
    assert digest(parent/'FREEZE.json')==PRODUCER_FREEZE
    assert digest(parent/'MANIFEST.json')==PRODUCER_MANIFEST
    manifest=json.loads((parent/'MANIFEST.json').read_text())
    for name,pin in manifest.items():assert digest(parent/name)==pin,name
    expected={
      'parser.rs':['position','source_location','line_number','advance_line_number'],
      'tokenizer.rs':['position','slice_from','slice','next_byte','is_eof','has_at_least','advance','next_byte_unchecked','byte_at','consume_4byte_intro','consume_continuation_byte','consume_newline','check_for_source_map','consume_comment']}
    records=json.loads((parent/'EXTRACTIONS.json').read_text())
    witness=(parent/'observer-witness.rs').read_text()
    seen={key:[] for key in expected}
    for row in records:
        source=(parent/'source/third_party/rust/cssparser/src'/row['source']).read_text()
        start=row['start'];end=body_end(source,start)
        assert end==row['end'],row
        body=source[start:end]
        assert hashlib.sha256(body.encode()).hexdigest()==row['sha256']
        assert body in witness
        assert re.search(r'fn '+row['name']+r'[<(]',body.split('{',1)[0])
        seen[row['source']].append(row['name'])
    assert seen==expected
    names=[]
    modules=json.loads((parent/'TOOLCHAIN.json').read_text())['modules']
    for name in modules:
        source=(parent/'lean'/f'{name}.lean').read_text()
        names.extend(name+'.'+n for n in re.findall(r'^theorem (\w+)',source,re.M))
    audits=json.loads((parent/'AUDIT-NAMES.json').read_text())
    assert names==audits and len(set(names))==100
    cases=json.loads((parent/'CASES.json').read_text())
    count=0;multi=0;url_changes=[0,0];empty_overwrites=[0,0]
    for case in cases:
        raw=case['input'].encode();cursor=4;urls=['initial.map','initial.css']
        assert raw[:4]==b'seed'
        if len(case['steps'])>1:multi+=1
        for step in case['steps']:
            assert raw[cursor:cursor+2]==b'/*'
            start=cursor
            closing=re.search(rb'\*/',raw[cursor+2:])
            body_end_at=len(raw) if closing is None else cursor+2+closing.start()
            body=raw[cursor+2:body_end_at]
            cursor=len(raw) if closing is None else body_end_at+2
            left,separator,value=body.partition(b'=')
            choices={b'# sourceMappingURL':0,b'@ sourceMappingURL':0,b'# sourceURL':1,b'@ sourceURL':1}
            if separator and left in choices:
                slot=choices[left]
                stop=next((i for i,b in enumerate(value) if b in (9,10,12,13,32)),len(value))
                updated=value[:stop].decode()
                if urls[slot]!=updated:url_changes[slot]+=1
                if updated=='':empty_overwrites[slot]+=1
                urls[slot]=updated
            prefix=raw[:cursor].decode().replace('\r\n','\n').replace('\r','\n').replace('\f','\n')
            parts=prefix.split('\n')
            line=3+len(parts)-1
            column=1+sum(1+(ord(c)>0xffff) for c in parts[-1])
            expected_step={'body':body.decode(),'start':start,'position':cursor,'line':line,'column':column,'urls':urls.copy()}
            assert step==expected_step,(count,step,expected_step)
            count+=1
        assert cursor==len(raw)
    assert len(cases)==395 and count==405 and multi==5
    return {'authenticated':len(manifest),'complete_native_definitions':len(records),'exact_theorem_inventory':len(names),'histories':len(cases),'calls':count,'multi_call_histories':multi,'url_changes':url_changes,'empty_overwrites':empty_overwrites,'independent_rows':'all match'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--producer',type=Path,default=ROOT.parent/'css-tokenizer-comment-provider-proof-v1')
    parser.add_argument('--replay-output',type=Path)
    args=parser.parse_args()
    for name,pin in json.loads((ROOT/'MANIFEST.json').read_text()).items():assert digest(ROOT/name)==pin,name
    result=independently_check(args.producer.resolve())
    if args.replay_output:
        subprocess.run([sys.executable,str(args.producer.resolve()/'gates.py'),'--output',str(args.replay_output.resolve())],check=True)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
