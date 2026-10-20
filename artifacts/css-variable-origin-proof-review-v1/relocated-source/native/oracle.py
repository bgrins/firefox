"""Restricted independent grammar for the declared native witness corpus."""
import json
from pathlib import Path

WS = ' \t\n\r\f'

def ident(c):
    return c.isascii() and (c.isalnum() or c in '_-') or ord(c) >= 128

def complete(text):
    result = ''
    stack = []
    i = 0
    while i < len(text):
        if text.startswith('/*', i):
            end = text.find('*/', i + 2)
            assert end >= 0
            result += text[i:end+2]
            i = end + 2
        elif text[i] in '\"\'':
            quote = text[i]
            result += quote
            i += 1
            while i < len(text) and text[i] != quote:
                if text[i] == '\\':
                    if i + 1 == len(text):
                        i += 1
                        break
                    result += text[i:i+2]
                    i += 2
                else:
                    result += text[i]
                    i += 1
            result += quote
            if i < len(text):
                i += 1
        else:
            c = text[i]
            if c == '(':
                stack.append(')')
            elif c == ')':
                assert stack and stack.pop() == c
            result += c
            i += 1
    return result.rstrip(WS) + ''.join(reversed(stack))

def parse(text):
    # The independent grammar traverses every function, retaining ordinary wrappers.
    def sequence(start, stop):
        nodes = []
        i = start
        while i < stop:
            if text.startswith('/*', i):
                end = text.index('*/', i + 2) + 2
                nodes.append(('raw', i, end))
            elif text[i] in '\"\'':
                quote = text[i]
                end = i + 1
                while text[end] != quote:
                    end += 2 if text[end] == '\\' else 1
                end += 1
                nodes.append(('raw', i, end))
            elif ident(text[i]):
                j = i + 1
                while j < stop and ident(text[j]):
                    j += 1
                if j < stop and text[j] == '(':
                    depth, end = 1, j + 1
                    quote = None
                    while depth:
                        if quote:
                            if text[end] == '\\':
                                end += 2
                                continue
                            if text[end] == quote:
                                quote = None
                        elif text.startswith('/*', end):
                            end = text.index('*/', end+2) + 2
                            continue
                        elif text[end] in '\"\'':
                            quote = text[end]
                        elif text[end] == '(':
                            depth += 1
                        elif text[end] == ')':
                            depth -= 1
                        end += 1
                    if text[i:j] == 'var':
                        comma = text.find(',', j+1, end-1)
                        name_end = end-1 if comma < 0 else comma
                        name = text[j+1:name_end].strip(WS)
                        assert name.startswith('--') and all(ident(c) for c in name)
                        fallback = None
                        if comma >= 0:
                            f = comma+1
                            while f < end-1 and text[f] in WS:
                                f += 1
                            fallback = (f, sequence(f, end-1))
                        nodes.append(('var',i,end,name[2:],fallback))
                    else:
                        nodes.append(('wrapper',i,end,j+1,sequence(j+1,end-1)))
                else:
                    end = j
                    nodes.append(('raw',i,end))
            else:
                end = i+1
                nodes.append(('raw',i,end))
            i = end
        return nodes
    return sequence(0,len(text))

def expected(case):
    raw = case['css'].encode()[case.get('start',0):].decode()
    text = complete(raw.lstrip(WS))
    nodes = parse(text)
    byte = lambda i: len(text[:i].encode())
    refs=[]
    def collect(ns):
        for n in ns:
            if n[0]=='var':
                refs.append([byte(n[1]),byte(n[2]),0 if n[4] is None else byte(n[4][0])])
                if n[4] is not None:
                    collect(n[4][1])
            elif n[0]=='wrapper':
                collect(n[4])
    collect(nodes)
    # Provenance belongs to complete selected replacements, including fallback text.
    def resolve(ns):
        pieces=[]
        for n in ns:
            if n[0]=='raw':
                pieces.append((text[n[1]:n[2]],False,False))
            elif n[0]=='wrapper':
                pieces.append((text[n[1]:n[3]],False,False))
                pieces.extend(resolve(n[4]))
                pieces.append((')',False,False))
            else:
                if n[3]=='present': value,taint='known',False
                elif n[3]=='tainted': value,taint='é中𐐀',True
                elif n[4] is not None:
                    value,_,taint = assemble(resolve(n[4][1]))
                else:
                    raise ValueError('missing provider and fallback')
                pieces.append((value,taint,True))
        return pieces
    def assemble(pieces):
        out='';ranges=[];aggregate=False
        previous_replacement=False
        for value,taint,replacement in pieces:
            aggregate |= taint
            if not value:
                continue
            if out and (replacement or previous_replacement) and ident(out[-1]) and ident(value[0]):
                out+='/**/'
            start=len(out.encode());out+=value
            if taint:ranges.append([start,len(out.encode())])
            previous_replacement=replacement
        return out,ranges,aggregate
    try:
        output,ranges,aggregate=assemble(resolve(nodes)); status='OK'
    except ValueError:
        output,ranges,aggregate,status='',[],False,'ERR'
    return {'css_hex':text.encode().hex(),'length':len(text.encode()),'refs':refs,
            'observed':bool(refs),'status':status,'output_hex':output.encode().hex(),'taint':ranges,'aggregate':aggregate}

def unique_object(pairs):
    result={}
    for key,value in pairs:
        assert key not in result, 'duplicate JSON key'
        result[key]=value
    return result

def check_rows(directory, cases):
    expectations=[dict(index=i,**expected(c)) for i,c in enumerate(cases)]
    results={}
    for variant in ['original','candidate','late-origin-mutant','no-reset-mutant','skip-comments-mutant','character-offset-mutant']:
        rows=[json.loads(line,object_pairs_hook=unique_object) for line in (directory/(variant+'.jsonl')).read_text().splitlines()]
        assert len(rows)==len(cases)
        assert [r['index'] for r in rows]==list(range(len(cases)))
        differences=[]
        for i,(row,expect) in enumerate(zip(rows,expectations)):
            assert set(row)==set(expect) or set(row)=={'index','parse'}
            if json.dumps(row,sort_keys=True) != json.dumps(expect,sort_keys=True):differences.append(i)
        if variant=='candidate':assert not differences, differences
        else:
            assert differences, variant
            witness = {'original':3,'late-origin-mutant':3,'no-reset-mutant':0,
                'skip-comments-mutant':2,'character-offset-mutant':2}[variant]
            assert witness in differences
            if variant in ['original','late-origin-mutant']:
                assert rows[witness]['status']=='PANIC'
                assert rows[witness]['refs'][0][1] > rows[witness]['length']
            elif variant=='no-reset-mutant':
                assert rows[witness]['css_hex']==b'--present)'.hex()
            elif variant=='skip-comments-mutant':
                assert rows[witness]['css_hex']==b'var(--present)'.hex()
            elif variant=='character-offset-mutant':
                assert rows[witness]['refs'][0][0]==7 and expectations[witness]['refs'][0][0]==13
        results[variant]={'differences':differences,'panic_rows':[r['index'] for r in rows if r.get('status')=='PANIC']}
    return {'status':'PASS','rows_per_variant':len(cases),'results':results,'expectations':expectations}

if __name__=='__main__':
    import sys
    directory=Path(sys.argv[1]);cases=json.loads((Path(__file__).parent/'CASES.json').read_text())
    result=check_rows(directory,cases)
    (directory/'ORACLE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='expectations'}))
