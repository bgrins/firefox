import hashlib
import itertools
from pathlib import Path

BASE = Path(__file__).resolve().parent
NAMES = {
    'missing': 'static nscoord ComputeMissingDimension(',
    'none': 'static Maybe<nsSize> MaybeComputeObjectFitNoneSize(',
    'concrete': 'static nsSize ComputeConcreteObjectSize(',
    'constrained': 'nsSize nsImageRenderer::ComputeConstrainedSize(',
}
COMMENT = '  // (Also: if there\'s no valid intrinsic ratio, then we have the "fill"\n  // behavior & just use the constraint size.)\n'
OLD = 'if (MOZ_LIKELY(aObjectFit == StyleObjectFit::Fill) || !aIntrinsicRatio)'
NEW = 'if (MOZ_LIKELY(aObjectFit == StyleObjectFit::Fill))'


def extract(text, signature):
    start = text.index(signature)
    end = text.index('{',start)+1
    depth = 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def expected_candidate(before):
    original = extract(before,NAMES['concrete'])
    if original.count(COMMENT) != 1 or original.count(OLD) != 1:
        raise ValueError('original guard identity mismatch')
    changed = original.replace(COMMENT,'').replace(OLD,NEW)
    return before.replace(original,changed,1)


def preservation(before,candidate,renderer):
    if expected_candidate(before) != candidate:
        raise ValueError('whole-file preservation mismatch')
    return {'functions': {name:hashlib.sha256(extract(renderer if name=='constrained' else candidate,sig).encode()).hexdigest() for name,sig in NAMES.items()},
            'allowed_change':'only remove absent-ratio disjunct and two explanatory comment lines from concrete sizing function',
            'helper_preservation':all(extract(before,NAMES[n])==extract(candidate,NAMES[n]) for n in ['missing','none'])}


def source(layout,renderer):
    enum = 'enum ObjectDimensionType { eWidth, eHeight };'
    if layout.count(enum) != 1:
        raise ValueError('dimension enum mismatch')
    parts = [(BASE/'bridge-prefix.cpp').read_text(),enum,extract(renderer,NAMES['constrained'])]
    parts += [extract(layout,NAMES[n]) for n in ['missing','none','concrete']]
    parts.append((BASE/'bridge-suffix.cpp').read_text())
    return '\n'.join(parts)


def fixture(fit,cw,ch,w,h,ratio,domain):
    present = ratio is not None
    p,q = ratio or (1,1)
    record = {'input':' '.join(map(str,[fit,cw,ch,int(w is not None),w or 0,int(h is not None),h or 0,int(present),p,q])),
              'domain':domain,'fit':fit,'constraint':[cw,ch],'natural':[w,h],'ratio':ratio}
    if not present:
        none = [cw if w is None else w,ch if h is None else h]
        concrete = [cw,ch] if fit in [0,1,2] else none if fit==3 else [min(cw,none[0]),min(ch,none[1])]
        record['candidate_expected'] = ' '.join(map(str,concrete+[0]))
        record['original_expected'] = f'{cw} {ch} 0'
        record['normative_oracle'] = domain=='absent-partial' or fit != 4
    else:
        record['normative_oracle'] = False
    return record


def fixtures():
    result = []
    options = [None,0,1,40,100,140,600]
    for cw,ch,w,h,fit in itertools.product([0,1,60,100,600],[0,1,60,100,600],options,options,range(5)):
        if w is None or h is None:
            result.append(fixture(fit,cw,ch,w,h,None,'absent-partial'))
    for w,h,fit in itertools.product([200],[50],range(5)):
        result.append(fixture(fit,100,100,w,h,None,'absent-both-boundary'))
    for fit in range(5):
        result.append(fixture(fit,100,100,0,0,None,'absent-both-boundary'))
    positive_sizes = [(None,None),(40,None),(None,40),(0,None),(None,0),(40,20),(20,40),(0,0),(200,50)]
    for (cw,ch),(w,h),ratio,fit in itertools.product([(0,0),(100,100),(240,120),(121,59)],positive_sizes,[(1,1),(2,1),(1,2),(3,2)],range(5)):
        result.append(fixture(fit,cw,ch,w,h,ratio,'positive-ratio-preservation'))
    return result
