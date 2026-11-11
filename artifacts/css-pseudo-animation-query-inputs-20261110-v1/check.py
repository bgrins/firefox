import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for name, expected in pins['files'].items():
        data = (HERE / 'source' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        assert subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', pins['revision'] + ':' + name], cwd=ROOT) == data
    prerequisites = json.loads((HERE / 'PREREQUISITES.json').read_text())
    for name, expected in prerequisites.items():
        assert sha(ROOT / name) == expected
        assert subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', pins['revision'] + ':' + name], cwd=ROOT) == (ROOT / name).read_bytes()
    roles = json.loads((HERE / 'ROLES.json').read_text())
    assert len(roles) == 8
    for name, hashes in roles.items():
        for directory, key in [('source', 'before'), ('prerequisite', 'prerequisite'), ('candidate', 'candidate')]:
            assert sha(HERE / directory / name) == hashes[key]
    with tempfile.TemporaryDirectory(prefix='pseudo-query-source-check-') as directory:
        scratch = Path(directory)
        for name in roles:
            dest = scratch / 'foundation' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'source' / name, dest)
        for name in prerequisites:
            subprocess.run(['patch', '--batch', '-p1', '-i', str(ROOT / name)], cwd=scratch / 'foundation', check=True, capture_output=True)
        assert all((scratch / 'foundation' / n).read_bytes() == (HERE / 'prerequisite' / n).read_bytes() for n in roles)
        for f in (scratch / 'foundation').rglob('*.orig'):
            f.unlink()
        assert not list((scratch / 'foundation').rglob('*.rej'))
        for patch, basis in [('query-inputs.patch', 'prerequisite'), ('candidate.patch', 'source')]:
            work = scratch / patch
            for name in roles:
                dest = work / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / basis / name, dest)
            for reverse, expected in [(False, 'candidate'), (True, basis)]:
                command = ['patch', '--batch', '-p1', '-i', str(HERE / patch)]
                if reverse:
                    command.append('-R')
                subprocess.run(command, cwd=work, check=True, capture_output=True)
                assert all((work / n).read_bytes() == (HERE / expected / n).read_bytes() for n in roles)
        generated = scratch / 'generated'
        subprocess.run([sys.executable, '-B', str(HERE / 'prepare.py'), '--out', str(generated)], check=True, capture_output=True)
        assert all((generated / 'candidate' / n).read_bytes() == (HERE / 'candidate' / n).read_bytes() for n in roles)
        assert all((generated / n).read_bytes() == (HERE / n).read_bytes() for n in ['query-inputs.patch', 'candidate.patch', 'FORMAT.json'])
    before = (HERE / 'prerequisite/dom/animation/Animation.cpp').read_text()
    after = (HERE / 'candidate/dom/animation/Animation.cpp').read_text()
    helper_start = after.index('Nullable<TimeDuration> Animation::GetHoldTimeForComposition(')
    compose_start = after.index('void Animation::ComposeStyle(', helper_start)
    helper = after[helper_start:compose_start]
    old_start = before.index('    if (pending && mHoldTime.IsNull()', before.index('void Animation::ComposeStyle('))
    old_end = before.index('\n\n    KeyframeEffect* keyframeEffect', old_start)
    branch = before[old_start:old_end]
    expected = branch.replace('pending &&', 'Pending() &&').replace('mHoldTime = CurrentTimeFromTimelineTime(', 'holdTime = CurrentTimeFromTimelineTime(').replace('TimeStamp::Now()', 'aSampleTime ? *aSampleTime : TimeStamp::Now()')
    assert compact(helper) == compact('Nullable<TimeDuration> Animation::GetHoldTimeForComposition(const TimeStamp* aSampleTime) const { auto holdTime = mHoldTime; ' + expected + ' return holdTime; }')
    restored = after[:helper_start] + after[compose_start:]
    restored = restored.replace('    mHoldTime = GetHoldTimeForComposition();', branch)
    assert compact(restored) == compact(before)
    before = (HERE / 'prerequisite/dom/animation/EffectCompositor.cpp').read_text()
    after = (HERE / 'candidate/dom/animation/EffectCompositor.cpp').read_text()
    start = after.index('bool EffectCompositor::ComposeServoAnimationRulesForMissingPseudo(')
    end = after.index('bool EffectCompositor::HasPendingStyleUpdates()', start)
    body = after[start:end]
    assert after[:start] + after[end:] == before
    for forbidden in ['UpdateProperties(', 'UpdateCascadeResults(', 'WillComposeStyle(', 'Tick(', 'TryTrigger', 'mHoldTime =', 'PropertiesForAnimationsLevel(', 'GetBaseContextForElement(', 'RequestRestyle(', 'GetComputedStyle(', 'effect->Properties(']:
        assert forbidden not in body, forbidden
    assert '&aAnimationValues == &aTransitionValues' in body
    assert 'aAnimationValues || aTransitionValues' in body
    assert 'GetPseudoElement(aTarget.mPseudoRequest)' in body
    assert 'effectTarget.mElement != target.mElement' in body
    assert 'effectTarget.mPseudoRequest != target.mPseudoRequest' in body
    assert 'animation->GetEffect() != effect.get()' in body
    capture_end = body.index('  AnimatedPropertyIDSet allProperties;')
    assert body.index('sortedEffects.Sort(') < body.index('inputs.RefreshComputedOffsets(') < capture_end
    assert body.index('animation->CascadeLevel()') < capture_end
    assert body.index('GetHoldTimeForComposition(&sampleTime)') < capture_end
    assert 'BuildPropertiesFromInputs(' not in body[:capture_end]
    assert 'effect->' not in body[capture_end:]
    conversion = body.index('KeyframeEffect::BuildPropertiesFromInputs(')
    base = body.index('Servo_ComputedValues_ExtractAnimationValue(baseStyle, &property)')
    maps = body.index('aAnimationValues.reset(Servo_AnimationValueMap_Create())')
    composition = body.index('KeyframeEffect::ComposeProperties(')
    assert capture_end < conversion < base < maps < composition
    assert compact('effect.mInputs, endpointStyle, effect.mTimeline, referencesAttributes') in compact(body)
    assert 'animationSkip.Setup(&animationProperties, true)' in body
    assert 'transitionSkip.Setup(&animationProperties, false)' in body
    assert compact('if (effect.mLevel == CascadeLevel::Transitions) { KeyframeEffect::ComposeProperties(*aTransitionValues') in compact(body)
    assert 'dom::EndpointBehavior::Exclusive' in body and 'EndpointBehavior::Inclusive' not in body
    assert 'if (!timeline || !timeline->IsUnresolvedTimeline())' in body
    tests = json.loads((HERE / 'TESTS.json').read_text())
    for name, record in tests['fixtures'].items():
        assert sha(HERE / 'fixtures' / name) == record['sha256']
        assert subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', tests['revision'] + ':' + record['origin']], cwd=ROOT) == (HERE / 'fixtures' / name).read_bytes()
    print(json.dumps({'status': 'PASS', 'source_revision': pins['revision'], 'source_pins': len(pins['files']), 'prerequisites': 2, 'candidate_files': 8, 'incremental_files': 4, 'retained_fixtures': 2, 'ordinary_pending_selector_source_correspondence': True, 'query_snapshot_before_conversion': True, 'distinct_owned_output_maps': True, 'fresh_base_and_level_masks': True, 'renderer_publication_calls_absent': True, 'deterministic_formatted_generation': True, 'forward_reverse_patches': True, 'native_compilation': False, 'query_path_runtime_executed': False, 'native_refinement_proved': False}, indent=2))


if __name__ == '__main__':
    main()
