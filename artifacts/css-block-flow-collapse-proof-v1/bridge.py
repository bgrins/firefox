from pathlib import Path
import hashlib

BASE=Path(__file__).resolve().parent
SIGNATURE='bool nsBlockReflowContext::ComputeCollapsedBStartMargin('


def extract(text, signature):
    start=text.index(signature)
    end=text.index('{',start)+1
    depth=1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}')
        end += 1
    return text[start:end]


def preservation(before,candidate):
    guard=(BASE/'guard.txt').read_text()
    if candidate.count(guard)!=1 or candidate.replace(guard,'',1)!=before:
        raise ValueError('whole-file changes exceed exact guard insertion')
    a=extract(before,SIGNATURE)
    b=extract(candidate,SIGNATURE)
    if b.replace(guard,'',1)!=a:
        raise ValueError('function preservation failure')
    return {'original_function_sha256':hashlib.sha256(a.encode()).hexdigest(),
            'candidate_function_sha256':hashlib.sha256(b.encode()).hexdigest(),
            'allowed_change':'exact late guard insertion only, whole file'}


def source(native):
    coord=(BASE/'nsCoord.h').read_text()
    constants=(BASE/'LayoutConstants.h').read_text()
    sentinel='inline constexpr nscoord NS_UNCONSTRAINEDSIZE = nscoord_MAX;'
    maximum='inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;'
    if constants.count(sentinel)!=1 or coord.count(maximum)!=1:
        raise ValueError('sentinel identity mismatch')
    margin=extract((BASE/'ReflowOutput.h').read_text(),'class CollapsingMargin final')+';'
    declaration='struct nsBlockReflowContext { Metrics mMetrics; bool ComputeCollapsedBStartMargin(const ReflowInput&, CollapsingMargin*, nsIFrame*, bool*, bool*); };'
    return '\n'.join([(BASE/'adapter-prefix.cpp').read_text(),maximum,sentinel,margin,declaration,extract(native,SIGNATURE),(BASE/'adapter-suffix.cpp').read_text()])
