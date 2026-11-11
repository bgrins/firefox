import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-git',action='store_true')
    args=parser.parse_args()
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in pins['files'].items():
        data=(HERE/'source'/name).read_bytes()
        assert sha(data)==digest,name
        if args.check_git:
            assert data==subprocess.check_output(['git','-c','core.fsmonitor=false','show',pins['revision']+':'+name],cwd=HERE)
    tests=json.loads((HERE/'TEST-SOURCES.json').read_text())
    for name,digest in tests['files'].items():
        if digest is None:
            assert not (HERE/'test-source'/name).exists()
            if args.check_git:
                result=subprocess.run(['git','-c','core.fsmonitor=false','cat-file','-e',tests['revision']+':'+name],cwd=HERE,capture_output=True)
                assert result.returncode != 0
        else:
            data=(HERE/'test-source'/name).read_bytes()
            assert sha(data)==digest,name
            if args.check_git:
                assert data==subprocess.check_output(['git','-c','core.fsmonitor=false','show',tests['revision']+':'+name],cwd=HERE)
    roles=json.loads((HERE/'ROLES.json').read_text())
    assert roles['revision']==pins['revision'] and len(roles['files'])==2
    for name,role in roles['files'].items():
        assert role['before_sha256']==pins['files'][name]
        assert sha((HERE/'candidate'/name).read_bytes())==role['after_sha256']
    with tempfile.TemporaryDirectory(prefix='pseudo-snapshot-replay-') as directory:
        scratch=Path(directory)
        for name in roles['files']:
            dest=scratch/name;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE/'source'/name,dest)
        for reverse,expected in [(False,'candidate'),(True,'source')]:
            command=['patch','--batch','-p1','-i',str(HERE/'snapshot.patch')]
            if reverse:command.append('-R')
            subprocess.run(command,cwd=scratch,check=True,capture_output=True)
            for name in roles['files']:
                assert (scratch/name).read_bytes()==(HERE/expected/name).read_bytes()
    name='dom/animation/KeyframeEffect.cpp'
    before=(HERE/'source'/name).read_text();after=(HERE/'candidate'/name).read_text()
    start=before.index('nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(')
    end=before.index('\ntemplate <typename FrameEnumFunc>',start)
    newstart=after.index('KeyframeEffect::PropertyInputSnapshot KeyframeEffect::CapturePropertyInputs()')
    newend=after.index('\ntemplate <typename FrameEnumFunc>',newstart)
    assert before[:start]==after[:newstart] and before[end:]==after[newend:], 'unrelated implementation changed'
    original=before[start:end]
    snapshot=after[newstart:after.index('/* static */',newstart)]
    static_start=after.index('nsTArray<AnimationProperty> KeyframeEffect::BuildPropertiesFromInputs(',newstart)
    wrapper_start=after.index('nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(',static_start)
    helper=after[static_start:wrapper_start]
    wrapper=after[wrapper_start:newend]
    assert original.count('mKeyframes.Clone()')==snapshot.count('mKeyframes.Clone()')==1
    assert after[newstart:newend].count('mKeyframes.Clone()')==1
    assert snapshot.count('GetComputedKeyframes(computedKeyframes)')==1
    assert snapshot.index('mKeyframes.Clone()')<snapshot.index('GetComputedKeyframes(computedKeyframes)')<snapshot.index('return {mTarget, mEffectOptions.mComposite')
    prefix=original[:original.index('  // When GetComputedKeyframeValues')]
    assert wrapper.startswith(prefix), 'style/attribute/null-target admission changed'
    old_suffix=original[original.index('#ifdef DEBUG'):].replace('keyframesCopy','inputs.mSpecifiedKeyframes')
    assert compact(old_suffix)==compact(wrapper[wrapper.index('#ifdef DEBUG'):]), 'debug check or unconditional move-back changed'
    assert 'aReferencesAttributes = false;' in helper and 'aReferencesAttributes' in helper
    expected='return KeyframeUtils::GetAnimationPropertiesFromKeyframes(\n      keyframes, aInputs.mTarget.mElement, aInputs.mTarget.mPseudoRequest,\n      aStyle, aInputs.mComposite, aTimeline, aReferencesAttributes);'
    assert compact(expected) in compact(helper)
    assert compact('aInputs.mHasComputedKeyframes ? aInputs.mComputedKeyframes : aInputs.mSpecifiedKeyframes') in compact(helper)
    assert 'mReferencesAttributes' not in helper and 'mProperties' not in helper and 'RequestRestyle' not in helper
    print(json.dumps({'status':'PASS','source_pins':len(pins['files']),'git_objects_checked':args.check_git,
                      'test_source_presence_pins':len(tests['files']), 'copied_native_files':2,'forward_reverse_replay':True,
                      'unrelated_cpp_and_GetKeyframes_unchanged':True,'single_specified_clone':True,
                      'virtual_capture_order_preserved':True,'renderer_admission_debug_and_writeback_preserved':True,
                      'native_compilation_or_browser_execution':False},indent=2))


if __name__=='__main__':main()
