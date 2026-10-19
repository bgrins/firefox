import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r'''//[^\n]*|/\*.*?\*/|b'(?:\\.|[^'\\])*'|'(?:\\(?:u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^'\\])'|"(?:\\.|[^"\\])*"|=>|\.\.=|\.\.|[A-Za-z_][A-Za-z_0-9]*|\d+|[^\s]''',re.S)

def tokens(text):
    out=[]
    for m in TOKEN.finditer(text):
        if m.group().startswith(('//','/*')):continue
        out.append((m.group(),m.start(),m.end()))
    return out

def pair(ts,start):
    close={'{':'}','(':')','[':']'}[ts[start][0]]
    pos=start+1
    while pos<len(ts):
        t=ts[pos][0]
        if t in ['{','(','[']:pos=pair(ts,pos)+1;continue
        if t==close:return pos
        pos+=1
    raise AssertionError('unterminated')

def lower(ts):
    # Parse the supported Rust pattern grammar rather than replacing textual operators.
    i=0; out=[]
    while i<len(ts):
        tok=ts[i]
        if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',tok):
            assert len(ts)==1,ts
            lo=hi=None;i+=1;out.append((0,255))
        else:
            assert tok.startswith("b'"),ts
            literal=ast.literal_eval(tok)
            assert isinstance(literal,bytes) and len(literal)==1
            lo=hi=literal[0];i+=1
            if i<len(ts) and ts[i] in ['..','..=']:
                assert ts[i]=='..=',('exclusive range',ts)
                hi=ast.literal_eval(ts[i+1])[0];i+=2
                assert lo<=hi
            out.append((lo,hi))
        if i<len(ts):assert ts[i]=='|',ts;i+=1
    return out

def independent_literal(text):
    assert text.startswith("b'") and text.endswith("'")
    raw = text[2:-1]
    if len(raw) == 1:
        assert ord(raw) < 128
        return bytes([ord(raw)])
    escapes = {r"\n":10, r"\r":13, r"\t":9, r"\0":0,
               r"\\":92, r"\'":39, r'\"':34}
    if raw in escapes:return bytes([escapes[raw]])
    assert re.fullmatch(r"\\x[0-9a-fA-F]{2}",raw),raw
    digits = "0123456789abcdef"
    return bytes([16 * digits.index(raw[2].lower()) + digits.index(raw[3].lower())])

def independent_match(pattern,b):
    # Direct textual membership, separate from the AST/numeric range lowering.
    pattern = re.sub(r'//[^\n]*', '', pattern)
    for text in re.split(r'\s+\|\s+', pattern):
        text=text.strip()
        if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',text):return True
        match=re.fullmatch(r"(b'(?:\\.|[^'\\])*')(?:\s*\.\.=\s*(b'(?:\\.|[^'\\])*'))?",text)
        assert match,text
        lo=independent_literal(match[1])
        hi=independent_literal(match[2]) if match[2] else lo
        if lo <= bytes([b]) <= hi:return True
    return False

def main(out):
    records=[]
    files=list((ROOT/'source/cssparser/src').glob('*.rs'))
    for path in sorted(files):
        source=path.read_text();ts=tokens(source)
        for start in range(len(ts)-2):
            if [x[0] for x in ts[start:start+3]]!=['match_byte','!','{']:continue
            end=pair(ts,start+2);cursor=start+3
            while ts[cursor][0]!=',':
                if ts[cursor][0] in ['{','(','[']:cursor=pair(ts,cursor)
                cursor+=1
            cursor+=1;arms=[];named_bindings=[]
            while cursor<end:
                begin=cursor
                while ts[cursor][0]!='=>':cursor+=1
                pattern=source[ts[begin][1]:ts[cursor][1]].strip()
                pattern_tokens=[x[0] for x in ts[begin:cursor]]
                ranges=lower(pattern_tokens)
                if len(pattern_tokens)==1 and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',pattern_tokens[0]) and pattern_tokens[0]!='_':
                    named_bindings.append(pattern_tokens[0])
                    assert len(named_bindings)<=1,('multiple named bindings',named_bindings)
                cursor+=1;body_start=cursor
                if ts[cursor][0]=='{':cursor=pair(ts,cursor)+1
                else:
                    while cursor<end and ts[cursor][0]!=',':
                        if ts[cursor][0] in ['{','(','[']:cursor=pair(ts,cursor)
                        cursor+=1
                arms.append({'pattern':pattern,'ranges':ranges,'body_sha256':hashlib.sha256(source[ts[body_start][1]:ts[cursor-1][2]].encode()).hexdigest()})
                if cursor<end and ts[cursor][0]==',':cursor+=1
            assert 0<len(arms)<=256
            table=[None]*256
            for idx,arm in enumerate(arms):
                for lo,hi in arm['ranges']:
                    for b in range(lo,hi+1):
                        if table[b] is None:table[b]=idx
            reference=[next((idx for idx,arm in enumerate(arms) if independent_match(arm['pattern'],b)),None) for b in range(256)]
            assert table==reference and None not in table
            records.append({'path':str(path.relative_to(ROOT)), 'source_character_start':ts[start][1],
                'byte_start':len(source[:ts[start][1]].encode('utf-8')),
                'line':source.count('\n',0,ts[start][1])+1,
                'invocation_sha256':hashlib.sha256(source[ts[start][1]:ts[end][2]].encode()).hexdigest(),
                'arms':arms,'table':table})
    assert len(records)==22,len(records)
    out.mkdir(parents=True,exist_ok=True)
    (out/'INVOCATIONS.json').write_text(json.dumps(records,indent=2)+'\n')
    lean=['import ByteDispatch','open ByteDispatch','set_option maxRecDepth 10000','set_option maxHeartbeats 3000000']
    for i,r in enumerate(records):
        patterns='['+', '.join('['+', '.join(f'({lo}, {hi})' for lo,hi in a['ranges'])+']' for a in r['arms'])+']'
        expected='['+', '.join(str(x) for x in r['table'])+']'
        lean += [f'def patterns{i} : List Pattern := {patterns}',
          f'example : patterns{i}.length ≤ 256 := by decide',
          f'example : (List.range 256).map (fun b => first patterns{i} 0 b) = ({expected} : List Nat).map some := by decide',
          f'example (b : Nat) : build patterns{i} 0 (fun _ => none) b = first patterns{i} 0 b := fresh_table _ _']
    (out/'CurrentInvocations.lean').write_text('\n'.join(lean)+'\n')
    print(json.dumps({'invocations':len(records),'bytes_per_invocation':256,'table_entries':len(records)*256}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)
