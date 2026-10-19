import re
TAGS = ["en-US", "en", "xx", "ja", "zh", "de", "bad_tag", "", "ja-Jpan",
        "ja-jpan", "und-Hans", "zh-Hant", "invalid--tag", "th", "und-Hrkt"]

def parse_state(line):
    line, limits = line.split(" LIMITS ")
    prefix, rest = line.split(" LANG ")
    language, rest = rest.split(" WORD")
    word, items = rest.split(" ITEMS")
    keys = ["script", "mixed", "might", "after_space", "break_here",
            "word_mode", "line_mode", "continuation"]
    values = list(map(int, prefix.split(" STATE ")[1].split()))
    result = dict(zip(keys, values))
    result.update(language=language, word=tuple(map(int, word.split())))
    contributions = []
    for item in items.split():
        owner, offset, length, flags = item.split(":")
        contributions.append((None if owner == "null" else tuple(map(int, owner.split("@"))),
                              int(offset), int(length), int(flags)))
    result["items"] = tuple(contributions)
    result["limits"] = tuple(map(int,limits.split(":")))
    return result

def parsed_tag(text):
    return None if text=='<null>' else {'identity':TAGS.index(text),'text':text}

def native_events(lines):
    events=[]
    current_tag=None
    for line in lines:
        if ' EVENT resolver request ' in line:
            events.append({'kind':'resolve','tag':parsed_tag(line.split(' EVENT resolver request ')[1])})
        elif ' EVENT provider input ' in line:
            width,word,strictness,script,*units=map(int,line.split(' EVENT provider input ')[1].split())
            events.append({'kind':'segment','width':width,'word':word,'line':strictness,'script':bool(script),'units':units})
        elif ' EVENT hyphenator lookup ' in line:
            current_tag=parsed_tag(line.split(' EVENT hyphenator lookup ')[1]);events.append({'kind':'lookup','tag':current_tag})
        elif ' EVENT filter input ' in line:
            limits,rest=line.split(' EVENT filter input ')[1].split(' TEXT');units,old=rest.split(' OLD')
            assert current_tag is not None
            events.append({'kind':'hyphenate','tag':current_tag,'limits':list(map(int,limits.split())),
              'units':list(map(int,units.split())),'old':list(map(int,old.split()))})
        elif ' EVENT capitalize input' in line:
            events.append({'kind':'capitalize','units':list(map(int,line.split(' EVENT capitalize input')[1].split()))})
        elif ' CALLBACK_ID ' in line:
            kind,*rest=line.split(' CALLBACK_ID ')[1].split();identity,owner,base,start,size,*values=map(int,rest);assert size==len(values)
            events.append({'kind':kind,'identity':identity,'owner':owner,'offset':base+start,'values':list(map(bool,values)) if kind=='C' else values})
    return events

def native_state(lines):
    state=parse_state(next(line for line in lines if ' STATE ' in line))
    ids=next(line for line in lines if ' ITEM_IDS' in line).split(' ITEM_IDS')[1].split()
    items=[]
    for identity,(sink,offset,length,flags) in zip(ids,state['items'],strict=True):
        owner,base=sink if sink is not None else (None,0)
        items.append({'identity':None if identity=='null' else int(identity),'owner':owner,'offset':base+offset,
          'chunk_offset':offset,'length':length,'flags':flags})
    return {'script':bool(state['script']),'mixed':bool(state['mixed']),'might':bool(state['might']),
      'continuation':bool(state['continuation']),'after_space':bool(state['after_space']),'break_here':bool(state['break_here']),
      'language':parsed_tag(state['language']),'word':state['word_mode'],'line':state['line_mode'],
      'units':list(state['word']),'items':items,'limits':list(state['limits'])}

def observations(raw):
    cases={}
    for line in raw.splitlines():cases.setdefault(line.split()[0],[]).append(line)
    results=[]
    for identity,lines in cases.items():
        if identity == "shutdown":
            assert all(" EVENT atom release " in line for line in lines)
            continue
        groups=[];active=[]
        for line in lines:
            if ' OP ' in line:
                if active:groups.append(active)
                active=[line]
            else:active.append(line)
        groups.append(active)
        steps=[]
        for group in groups:
            end=next(i for i,line in enumerate(group) if ' ITEM_IDS' in line)+1
            current=group[:end]
            if not group[0].endswith(' P'):
                steps.append({'state':native_state(current),'events':native_events(current)})
        final=groups[-1][next(i for i,line in enumerate(groups[-1]) if ' ITEM_IDS' in line)+1:]
        steps.append({'state':native_state(final),'events':native_events(final)})
        results.append({'id':identity,'steps':steps})
    return results
