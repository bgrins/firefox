import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-git', action='store_true')
    args=parser.parse_args()
    roles=json.loads((HERE/'ROLES.json').read_text())
    assert len(roles['files']) == 5
    originals=0
    for name, role in roles['files'].items():
        assert digest((HERE/'candidate'/name).read_bytes()) == role['after_sha256'], name
        if role['before_sha256'] is None:
            assert not (HERE/'source'/name).exists()
            if args.check_git:
                result=subprocess.run(['git','-c','core.fsmonitor=false','cat-file','-e',roles['revision']+':'+name],cwd=HERE,capture_output=True)
                assert result.returncode != 0
        else:
            original=(HERE/'source'/name).read_bytes()
            assert digest(original) == role['before_sha256'], name
            if args.check_git:
                assert original == subprocess.check_output(['git','-c','core.fsmonitor=false','show',roles['revision']+':'+name],cwd=HERE)
            originals+=1
    context=json.loads((HERE/'EXPOSURE-SOURCES.json').read_text())
    for name, expected in context['files'].items():
        data=(HERE/'context'/name).read_bytes()
        assert digest(data) == expected
        if args.check_git:
            assert data == subprocess.check_output(['git','-c','core.fsmonitor=false','show',context['revision']+':'+name],cwd=HERE)
    with tempfile.TemporaryDirectory(prefix='clip-delivery-replay-') as directory:
        scratch=Path(directory)
        for name, role in roles['files'].items():
            dest=scratch/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            if role['before_sha256'] is not None:
                shutil.copyfile(HERE/'source'/name,dest)
        for reverse in [False, True]:
            command=['patch','--batch','-p1','-i',str(HERE/'delivery.patch')]
            if reverse:
                command.append('-R')
            subprocess.run(command,cwd=scratch,check=True,capture_output=True)
            for name, role in roles['files'].items():
                path=scratch/name
                expected=role['before_sha256' if reverse else 'after_sha256']
                assert not path.exists() if expected is None else digest(path.read_bytes()) == expected, name
    meta='testing/web-platform/meta/web-animations/animation-model/keyframe-effects/effect-value-iteration-composite-operation.html.ini'
    removed='  [iteration composition of incompatible clip rects (accumulation skipped at 0%, allowed at 50%)]\n    expected: FAIL\n\n'
    assert (HERE/'source'/meta).read_text().replace(removed,'') == (HERE/'candidate'/meta).read_text()
    print(json.dumps({'status':'PASS','delivery_files':5,'existing_source_pins':originals,'new_WPT':1,
                      'exposure_source_pins':len(context['files']),'git_objects_checked':args.check_git,
                      'forward_reverse_patch_replay':True,'only_clip_failure_stanza_removed':True},indent=2))


if __name__ == '__main__':
    main()
