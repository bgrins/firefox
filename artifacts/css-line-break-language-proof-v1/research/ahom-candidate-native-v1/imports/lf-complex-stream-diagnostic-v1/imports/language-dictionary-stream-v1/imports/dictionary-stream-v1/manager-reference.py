def keys(locale):
    result=[locale]
    parts=locale.split('-')
    if parts[-1]=='*':parts.pop()
    while len(parts)>1:
        parts.pop()
        base='-'.join(parts)
        if len(base)<=1:break
        result.append(base+'-*')
    return result


def evaluate(operations):
    patterns={};aliases={};cache={};preferences={};loads=[];pref_reads=[];gets=[]
    for op,*args in operations:
        if op=='P':patterns[args[0]]=(args[1],bool(args[2]))
        elif op=='A':aliases[args[0]]=args[1]
        elif op=='C':preferences[args[0]]=bool(args[1])
        elif op=='M':cache={}
        elif op=='G':
            requested=args[0];answer=('-',False)
            for key in keys(requested):
                if key in cache:
                    answer=cache[key];break
                selected=key if key in patterns else aliases.get(key)
                if selected is None:continue
                if selected in cache:
                    answer=cache[selected];break
                if selected not in patterns:continue
                path,valid=patterns[selected]
                loads.append(path);pref_reads.append('intl.hyphenate-capitalized.'+selected)
                if valid:
                    answer=(path,preferences.get(selected,False));cache[selected]=answer
                else:del patterns[selected]
                break
            gets.append((requested,*answer))
    return {'gets':gets,'loads':loads,'prefs':pref_reads,'cache':sorted(cache),'patterns':sorted(patterns)}
