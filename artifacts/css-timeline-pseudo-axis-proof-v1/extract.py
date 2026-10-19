from pathlib import Path
import hashlib

BASE = Path(__file__).resolve().parent

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def close_brace(text, opening):
    depth = 0
    state = 'code'
    i = opening
    while i < len(text):
        c = text[i]
        n = text[i:i+2]
        if state == 'line':
            if c == '\n': state = 'code'
        elif state == 'block':
            if n == '*/': state = 'code'; i += 1
        elif state in ['"', "'"]:
            if c == '\\': i += 1
            elif c == state: state = 'code'
        elif n == '//': state = 'line'; i += 1
        elif n == '/*': state = 'block'; i += 1
        elif c in ['"', "'"]: state = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if not depth: return i + 1
        i += 1
    raise AssertionError('unclosed body')

def definition(text, signature, body_marker=None, semicolon=False):
    assert text.count(signature) == 1, signature
    start = text.index(signature)
    opening = text.index(body_marker, start) + len(body_marker) - 1 if body_marker else text.index('{', start)
    assert text[opening] == '{'
    end = close_brace(text, opening)
    if semicolon:
        assert text[end] == ';'; end += 1
    return text[start:end], dict(signature=signature, start=start, end=end, sha256=sha(text[start:end]),byte_start=len(text[:start].encode()),byte_end=len(text[:end].encode()))

FUNCTIONS = [
 ('Element* ScrollTimeline::GetSource()', None),
 ('ScrollTimeline::StateSnapshot ScrollTimeline::ComputeSnapshot()', None),
 ('ScrollTimeline::StateSnapshot ScrollTimeline::GetSnapshot()', None),
 ('ScrollTimeline::ScrollTimeline(Document*', 'mAxis(aAxis) {'),
 ('std::pair<const Element*, PseudoStyleRequest>\nScrollTimeline::FindNearestScroller(', None),
 ('already_AddRefed<ScrollTimeline> ScrollTimeline::MakeAnonymous(', None),
 ('already_AddRefed<ScrollTimeline> ScrollTimeline::MakeNamed(', None),
 ('Nullable<TimeDuration> ScrollTimeline::GetCurrentTimeAsDuration()', None),
 ('void ScrollTimeline::GetCurrentTime(', None),
 ('ScrollTimeline::StateSnapshot::StateSnapshot(', 'mIsRoot{aIsRoot} {'),
 ('layers::ScrollDirection ScrollTimeline::StateSnapshot::ComputePhysicalAxis(', None),
 ('const ScrollContainerFrame*\nScrollTimeline::StateSnapshot::GetScrollContainerFrame()', None),
 ('bool ScrollTimeline::UpdateCachedCurrentTime()', None),
 ('void ScrollTimeline::TimelineDataDidChange()', None),
 ('Maybe<ScrollTimeline::ComputedTimelineData>\nScrollTimeline::ComputeTimelineData()', None),
 ('NonOwningAnimationTarget ScrollTimeline::ScrollerInfo::Source()', None),
]

def build(variant):
    source = (BASE/'source'/variant/'ScrollTimeline.cpp').read_text()
    header = (BASE/'source'/variant/'ScrollTimeline.h').read_text()
    binding = []
    declarations = []
    for sig in ['struct ScrollerInfo {','class StateSnapshot {','struct ComputedTimelineData {','struct CurrentTimeData {']:
        body, pin = definition(header,sig,semicolon=True)
        pin['source'] = variant+'/ScrollTimeline.h';binding.append(pin);declarations.append(body)
    expose, pin = definition(header,'Element* SourceElement() const { return mScrollerInfo.Source().mElement; }')
    pin['source'] = variant+'/ScrollTimeline.h';binding.append(pin)
    methods=[]
    for sig, marker in FUNCTIONS:
        body,pin=definition(source,sig,marker);pin['source']=variant+'/ScrollTimeline.cpp';binding.append(pin);methods.append(body)
    providers = []
    for path,sigs in [
        ('dom/animation/AnimationUtils.cpp',['std::pair<const Element*, PseudoStyleRequest>\nAnimationUtils::GetElementPseudoPair(']),
        ('layout/base/nsLayoutUtils.cpp',['nsIFrame* nsLayoutUtils::GetScrollContainerFrameFromContent(', 'ScrollContainerFrame* nsLayoutUtils::FindScrollContainerFrameFor(\n    nsIContent*'])]:
        text=(BASE/'source/providers'/path).read_text()
        for sig in sigs:
            body,pin=definition(text,sig);pin['source']='providers/'+path;binding.append(pin);providers.append(body)
    result=(BASE/'adapter-prefix.cpp').read_text()
    result += '\nclass ScrollTimeline : public AnimationTimeline { public:\n'+'\n'.join(declarations)+'\n'+expose+'\n'
    result += (BASE/'adapter-class.cpp').read_text()+'\n};\n'
    result += '\n'.join(providers)+'\n'+'\n'.join(methods)+'\n'+(BASE/'adapter-suffix.cpp').read_text()
    return result,binding
