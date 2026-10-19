from pathlib import Path
import json
from extract import definition, digest
ROOT=Path(__file__).resolve().parent

def generate(variant='candidate', mutant=None):
    records=[]
    def get(path, marker, semi=False, log=None):
        source=(ROOT/('sources' if path!='dom/animation/KeyframeEffect.cpp' else variant)/path).read_text()
        raw=definition(source,marker,semi)
        records.append({'path':path,'variant':variant if path.endswith('KeyframeEffect.cpp') else 'shared','marker':marker,'sha256':digest(raw),'bytes':len(raw.encode())})
        text=raw
        if mutant:
            marker_filter, old,new=mutant
            if marker==marker_filter:
                assert text.count(old)==1,(marker,old,text.count(old));text=text.replace(old,new)
        if log:
            at=text.index('{')+1;text=text[:at]+'\n  event("'+log+'");'+text[at:]
        return text
    chunks=[(ROOT/'adapter-prefix.cpp').read_text()]
    chunks += ['namespace mozilla {']
    for marker in ['struct PropertyValuePair {','enum class KeyframeOffsetsHasRangeOffset {','struct Keyframe {']:
        chunks.append(get('dom/animation/Keyframe.h',marker,True))
    chunks.append(get('dom/animation/AnimationPropertySegment.h','struct AnimationPropertySegment {',True))
    chunks.append(get('dom/animation/KeyframeEffect.h','struct AnimationProperty {',True))
    middle=(ROOT/'adapter-middle.cpp').read_text().replace('/*GET_COMPUTED*/',get('dom/animation/KeyframeEffect.h','virtual bool GetComputedKeyframes(',log='ordinary-keyframes'))
    chunks += ['}',middle,'namespace mozilla {']
    chunks.append(get('dom/animation/KeyframeEffect.cpp','bool PropertyValuePair::operator==('))
    chunks += ['}']
    chunks.append(get('dom/animation/KeyframeUtils.cpp','static nsTArray<ComputedKeyframeValues> GetComputedKeyframeValues(',log='computed-values'))
    for marker in ['struct KeyframeValueEntry {','static void DistributeRange(','static void DoComputeMissingKeyframeOffsets(','static void AppendInitialSegment(','static void AppendFinalSegment(','static AnimationProperty* HandleMissingInitialKeyframe(','static void HandleMissingFinalKeyframe(','static void BuildSegmentsFromValueEntries(']:
        chunks.append(get('dom/animation/KeyframeUtils.cpp',marker,marker.startswith('struct')))
    for marker,log in [('double KeyframeUtils::GetComputedOffset(',None),('KeyframeOffsetsHasRangeOffset KeyframeUtils::ComputeMissingKeyframeOffsets(','compute'),('nsTArray<AnimationProperty> KeyframeUtils::GetAnimationPropertiesFromKeyframes(',None)]:
        chunks.append(get('dom/animation/KeyframeUtils.cpp',marker,log=log))
    for marker,log in [('static bool KeyframesEqualIgnoringComputedOffsets(',None),('void KeyframeEffect::SetKeyframes(nsTArray<Keyframe>&&',None),('void KeyframeEffect::SetKeyframes(JSContext*',None),('nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(','build'),('void KeyframeEffect::EnsureBaseStyle(',None),('void KeyframeEffect::EnsureBaseStyles(','base-styles'),('void KeyframeEffect::UpdateProperties(','update'),('void KeyframeEffect::MaybeUpdateKeyframeComputedOffsets(','refresh'),('void KeyframeEffect::SetComposite(',None),('void KeyframeEffect::GetKeyframes(','get')]:
        chunks.append(get('dom/animation/KeyframeEffect.cpp',marker,log=log))
    chunks.append((ROOT/'adapter-main.cpp').read_text())
    return '\n\n'.join(chunks),records
if __name__=='__main__':
    import sys
    destination=Path(sys.argv[1]);destination.mkdir(parents=True,exist_ok=True)
    for v in ['original','candidate']:
        text, records=generate(v);(destination/(v+'.cpp')).write_text(text)
        (destination/(v+'-extraction.json')).write_text(json.dumps(records,indent=2)+'\n')
