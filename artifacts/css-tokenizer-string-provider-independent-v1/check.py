from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parent
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

def raw_reference(raw):
    quote=raw[0]; assert quote in ('"', "'")
    i=1;value=[];bad=False;allocated=False
    def newline_end(j):
        return j+2 if raw[j:j+2]=='\r\n' else j+1
    while i<len(raw):
        ch=raw[i]
        if ch==quote:i+=1;break
        if ch in '\n\r\f':bad=True;break
        if ch=='\0':allocated=True;value.append('\ufffd');i+=1;continue
        if ch!='\\':value.append(ch);i+=1;continue
        allocated=True;i+=1
        if i==len(raw):break
        if raw[i] in '\n\r\f':i=newline_end(i);continue
        digits=''
        while i<len(raw) and len(digits)<6 and raw[i] in '0123456789abcdefABCDEF':
            digits+=raw[i];i+=1
        if digits:
            number=int(digits,16)
            value.append(chr(number) if 0<number<=0x10ffff and not 0xd800<=number<=0xdfff else '\ufffd')
            if i<len(raw) and raw[i] in ' \t\n\r\f':i=newline_end(i) if raw[i] in '\n\r\f' else i+1
        else:value.append('\ufffd' if raw[i]=='\0' else raw[i]);i+=1
    prefix=('seed'+raw[:i]).replace('\r\n','\n').replace('\r','\n').replace('\f','\n')
    pieces=prefix.split('\n')
    return dict(raw=raw,bad=bad,value=''.join(value),position=4+len(raw[:i].encode()),line=3+len(pieces)-1,column=1+sum(1+(ord(c)>0xffff) for c in pieces[-1]),allocated=allocated,remainder=raw[i:])

def check(parent):
    assert digest(parent/'FREEZE.json')=='1c7c5f53915fb2f1df7a81a610e6959ac522e68d4d3452142aade57de819f892'
    assert digest(parent/'MANIFEST.json')=='930e1006722cfa937deae6d09bde0d698ec502446050d169bb5357081f82f9dd'
    manifest=json.loads((parent/'MANIFEST.json').read_text())
    for name,pin in manifest.items():assert digest(parent/name)==pin,name
    records=json.loads((parent/'EXTRACTIONS.json').read_text());witness=(parent/'string-witness.rs').read_text()
    assert len(records)==25
    expected=['position','source_location','line_number','advance_line_number','position','slice_from','slice','next_byte','is_eof','has_at_least','advance','next_byte_unchecked','byte_at','consume_4byte_intro','consume_continuation_byte','next_char','consume_newline','consume_char','consume_string','consume_quoted_string','byte_to_hex_digit','consume_hex_digits','consume_escape_and_write','consume_escape','from_utf8_release_unchecked']
    assert [r['name'] for r in records]==expected
    for row in records:
        source=(parent/'source/third_party/rust/cssparser/src'/row['source']).read_text()
        end=body_end(source,row['start']);assert end==row['end'],row
        body=source[row['start']:end]
        assert hashlib.sha256(body.encode()).hexdigest()==row['sha256']
        assert body in witness
    cow=parent/'source/third_party/rust/cssparser/src/cow_rc_str.rs'
    assert digest(cow)=='b5aacf0d6cf39e0f916d9933c992a8aaed2cd6698a99746912f3975b92d66fa1'
    assert 'include!("source/third_party/rust/cssparser/src/cow_rc_str.rs")' in witness
    modules=json.loads((parent/'TOOLCHAIN.json').read_text())['modules'];names=[]
    for name in modules:
        text=(parent/'lean'/f'{name}.lean').read_text()
        names.extend(name+'.'+n for n in re.findall(r'^theorem (\w+)',text,re.M))
    assert names==json.loads((parent/'AUDIT-NAMES.json').read_text()) and len(set(names))==152
    assert len([n for n in names if n.startswith('String')])==52
    cases=json.loads((parent/'CASES.json').read_text())
    assert len(cases)==len({c['raw'] for c in cases})==808
    for i,row in enumerate(cases):assert raw_reference(row['raw'])==row,(i,row,raw_reference(row['raw']))
    return dict(authenticated=len(manifest),complete_native_bodies=len(records),actual_CowRcStr=True,modules=len(modules),exact_audits=len(names),new_audits=52,independent_raw_reference_rows=len(cases),bad_strings=sum(c['bad'] for c in cases),owned_strings=sum(c['allocated'] for c in cases),result='PASS')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--producer',type=Path,default=ROOT.parent/'css-tokenizer-string-provider-proof-v1');parser.add_argument('--replay-output',type=Path)
    args=parser.parse_args()
    for name,pin in json.loads((ROOT/'MANIFEST.json').read_text()).items():assert digest(ROOT/name)==pin,name
    result=check(args.producer.resolve())
    names=json.loads((args.producer/'AUDIT-NAMES.json').read_text())
    audit=(ROOT/'evidence/Audit.log').read_text()
    found=re.findall(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms:)",audit,re.M)
    assert found==names
    for line in audit.splitlines():
        if 'depends on axioms:' in line:assert set(re.search(r'\[(.*)\]',line)[1].split(', ')) <= {'propext','Quot.sound','Classical.choice'}
    roster=(ROOT/'PRODUCER-COMMIT-FILES.txt').read_text().splitlines()
    pins=json.loads((ROOT/'PRODUCER-PINS.json').read_text())
    assert roster==list(pins) and len(roster)==135
    if args.replay_output:subprocess.run([sys.executable,str(args.producer.resolve()/'gates.py'),'--output',str(args.replay_output.resolve())],check=True)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
