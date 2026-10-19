import re
TAGS=['en-US', 'en', 'xx', 'ja', 'zh', 'de', 'bad_tag', '', 'ja-Jpan', 'ja-jpan', 'und-Hans', 'zh-Hant', 'invalid--tag', 'th', 'und-Hrkt']
def parse_state(line):
    line, limits = line.split(" LIMITS ")
    if " CAPTURED " in limits:
        limits, captured = limits.split(" CAPTURED ")
    else:
        captured = None
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
    if captured is not None:result["captured_limits"] = tuple(map(int,captured.split(":")))
    return result
def tag_json(name):
 return None if name=='<null>' else {'identity':TAGS.index(name),'text':name}
def native_observations(raw):
 cases={};events=[];pending=None;lookup=None
 for line in raw.splitlines():
  identity=line.split(' ',1)[0]
  if identity=='shutdown':continue
  result=cases.setdefault(identity,{'id':identity,'steps':[]})
  if ' OP 'in line:pending=line.split()[-1];continue
  if ' EVENT resolver request 'in line:events.append({'kind':'resolve','tag':tag_json(line.split(' EVENT resolver request ')[1])})
  elif ' EVENT provider input 'in line:
   width,word,strict,script,*units=map(int,line.split(' EVENT provider input ')[1].split());events.append({'kind':'segment','width':width,'word':word,'line':strict,'script':bool(script),'units':units})
  elif ' LOOKUP 'in line:
   lookup=tag_json(line.split(' LOOKUP ')[1]);events.append({'kind':'lookup','tag':lookup})
  elif ' CAPITALIZE'in line:events.append({'kind':'capitalize','units':list(map(int,line.split(' CAPITALIZE')[1].split()))})
  elif ' HYPHEN 'in line:
   limits,rest=line.split(' HYPHEN ')[1].split(' UNITS');units,old=rest.split(' BEFORE ');events.append({'kind':'hyphenate','tag':lookup,'limits':list(map(int,limits.split(':'))),'units':list(map(int,units.split())),'old':list(map(int,old))})
  elif ' CALLBACK 'in line:
   kind,*values=line.split(' CALLBACK ')[1].split();instance,owner,base,offset,n,*values=map(int,values);assert n==len(values);events.append({'kind':kind,'identity':instance,'owner':owner,'offset':base+offset,'values':values if kind=='B'else list(map(bool,values))})
  elif ' STATE 'in line:
   if pending=='P':assert not events;pending=None;continue
   rawstate=parse_state(line);items=[]
   for sink,offset,length,flags in rawstate['items']:
    instance,owner,base=sink if sink is not None else (None,None,0)
    items.append({'identity':instance,'owner':owner,'offset':base+offset if sink is not None else 0,'chunk_offset':offset,'length':length,'flags':flags})
   state={'script':bool(rawstate['script']),'mixed':bool(rawstate['mixed']),'language':tag_json(rawstate['language']),'might':bool(rawstate['might']),'continuation':bool(rawstate['continuation']),'after_space':bool(rawstate['after_space']),'break_here':bool(rawstate['break_here']),'word':rawstate['word_mode'],'line':rawstate['line_mode'],'units':list(rawstate['word']),'items':items,'limits':list(rawstate['limits']),'captured_limits':list(rawstate['captured_limits'])}
   result['steps'].append({'state':state,'events':events});events=[];pending=None
 return list(cases.values())
