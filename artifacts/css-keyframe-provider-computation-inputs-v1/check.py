import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    here = Path(__file__).resolve().parent
    pre = json.loads((here / 'PREIMAGES.json').read_text())
    post = json.loads((here / 'POSTIMAGES.json').read_text())
    assert pre.keys() == post.keys() and len(pre) == 4
    for name in pre:
        assert digest(here / 'original' / name) == pre[name]
        assert digest(here / 'candidate' / name) == post[name]
    for path, expected in json.loads((here / 'REFERENCES.json').read_text()).items():
        assert digest(here.parents[1] / path) == expected

    glue = 'servo/ports/geckolib/glue.rs'
    old = (here / 'original' / glue).read_text()
    new = (here / 'candidate' / glue).read_text()
    begin = 'pub extern "C" fn Servo_AnimationRuleSample_Compose('
    end = '\n#[unsafe(no_mangle)]'
    old_start, new_start = old.index(begin), new.index(begin)
    assert old[:old_start] == new[:new_start]
    assert old[old.index(end, old_start):] == new[new.index(end, new_start):]
    body = new[new_start:new.index(end, new_start)]
    assert 'property_segments: &nsTArray<structs::AnimationPropertySegment>' in body
    assert 'else if let Some(inputs) = computation_inputs' in body
    assert body.index('else if let Some(inputs)') > body.index('if !inserted')
    assert 'if value.is_null()' in body and 'else if endpoint.is_null()' in body
    assert 'resolve_registered' not in body
    assert 'FrozenAnimationRule<std::convert::Infallible>' in (
        here / 'candidate/servo/components/style/animation_rule_sample.rs').read_text()

    for witness in json.loads((here / 'WITNESSES.json').read_text()):
        selected = witness['selected_segment'] + witness['last_segment']
        a, b = witness['original'], witness['changed']
        assert a != b and [a[i] for i in selected] == [b[i] for i in selected]
        assert len(a) == len(b) == 5 and a[2] != b[2]
        assert witness['cyclic_numeric_oracle'] is None

    logs = []
    with tempfile.TemporaryDirectory(prefix='provider-input-transport-') as temporary:
        work = Path(temporary)
        shutil.copytree(here / 'original', work, dirs_exist_ok=True)
        for reverse, expected in [(False, post), (True, pre)]:
            command = ['patch', '--batch', '-p1'] + (['-R'] if reverse else [])
            result = subprocess.run(command, cwd=work, input=(here / 'native.patch').read_bytes(),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logs.append({'command': command, 'exit': result.returncode,
                         'output': result.stdout.decode()})
            assert result.returncode == 0, logs[-1]
            assert all(digest(work / name) == value for name, value in expected.items())
    args.output.write_text(json.dumps({
        'status': 'STATIC_TRANSPORT_AND_PROJECTION_PASS',
        'native_compilation': False, 'native_tests': False, 'browser_execution': False,
        'pending_production_enabled': False, 'scratch_removed': not work.exists(),
        'transport': logs,
        'scope': 'Exact four-file transport; unchanged public glue; two source-derived input-loss witnesses. No scheduler or cycle verdict.'
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
