import copy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/css-prioritary-selection-suite-v1'
NEW = ROOT / 'artifacts/css-prioritary-appearance-self-probe-v1'
PAGE = '/_mozilla/css/css-cascade/prioritary-appearance-self-selection.html'
META = 'css/css-cascade/prioritary-appearance-self-selection.html.ini'
NATIVE_META = 'testing/web-platform/mozilla/meta/' + META
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pin = lambda p: {'path': str(p.relative_to(ROOT)), 'sha256': sha(p)}


def authenticate(directory, digest):
    assert sha(directory / 'FILES.json') == digest
    for name, value in read(directory / 'FILES.json').items():
        path = directory / name
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert not path.is_symlink() and path.stat().st_size == value['bytes']
        assert sha(path) == value['sha256']


def expected():
    authenticate(OLD, 'c93d4a7aa610113e33cd368103eb0b526cc9888e6b358358607febdd48e31031')
    authenticate(NEW, '4effa8f9a40c16fcba3c714f02a9d18dd59f0c8a4808d4fd43ff840f67a79c12')
    for entry in read(HERE/'REFERENCES.json'):
        assert sha(ROOT/entry['path']) == entry['sha256']
    authenticate(ROOT/'artifacts/css-prioritary-zoom-capture-v1', 'ed0ed2222d90e2e04437dc033bbcd4a62f6264f89a1135b82a10051e99da0de2')
    old = read(OLD / 'INPUTS.json')
    addition = read(NEW / 'INPUTS.json')
    roster = read(OLD / 'ROSTER.json')
    extra = read(NEW / 'ROSTER.json')
    assert set(extra) == {PAGE} and len(extra[PAGE]) == 3 and PAGE not in roster
    roster.update(extra)
    result = copy.deepcopy(old)
    result.update(callbacks=77, pages=12, signatures=89, sealed_resource_count=16)
    result['packages']['predecessor74'] = str(OLD.relative_to(ROOT))
    result['packages']['appearance_self3'] = str(NEW.relative_to(ROOT))
    for url, entry in addition['resources'].items():
        if url in old['resources']:
            assert entry['sha256'] == old['resources'][url]['sha256']
        else:
            assert url == PAGE
            result['resources'][url] = pin(HERE / 'mozilla/tests' / url[len('/_mozilla/'):])
            result['copy_resources'][url] = result['resources'][url]
            result['source_resources'][url] = entry
    pref = addition['metadata']['mozilla/' + META]
    assert (ROOT / pref['path']).read_bytes() == (OLD / 'mozilla/meta/css/css-cascade/prioritary-appearance-selection.html.ini').read_bytes()
    result['metadata']['mozilla'][META] = pin(HERE / 'mozilla/meta' / META)
    result['metadata_admission'][NATIVE_META] = {'sha256':None, 'source':'new artifact-only metadata path; future owner must verify absence', 'absence_requires_future_owner_check':True}
    result['metadata_overlays']['mozilla/' + META] = {'required_absent':{'path':NATIVE_META,'sha256':None}, 'runtime_overlay':pref}
    lanes = read(OLD / 'LANES.json')
    lanes['mozilla_appearance']['roster'].update(extra)
    lanes['mozilla_appearance'].update(callbacks=6,pages=2)
    assert sum(map(len, roster.values())) == result['callbacks'] == 77
    assert len(roster) == result['pages'] == 12
    assert result['callbacks'] + result['pages'] == result['signatures'] == 89
    assert len(result['resources']) == 16
    assert [(lanes[k]['callbacks'],lanes[k]['pages']) for k in ['ordinary','forced_colors','mozilla_appearance']] == [(68,8),(3,2),(6,2)]
    return result, roster, lanes


def verify(inputs, roster, lanes):
    desired, desired_roster, desired_lanes = expected()
    assert inputs == desired and roster == desired_roster and lanes == desired_lanes
    for tree in ['tests','meta','mozilla/tests','mozilla/meta']:
        for source in (OLD/tree).rglob('*'):
            if source.is_file():
                assert (HERE/source.relative_to(OLD)).read_bytes() == source.read_bytes()
    old = read(OLD/'INPUTS.json')
    for group in ['resources','copy_resources','source_resources','metadata_admission','metadata_overlays']:
        assert all(inputs[group][k] == v for k,v in old[group].items())
    for group in ['install_managed_resource_pins','install_managed_resources','runtime_generated_not_presealed','capture_helper','sole_page_replacement','original45_metadata','current_binding','expected_statuses','execution']:
        assert inputs[group] == old[group]
    for lane, values in old['metadata'].items():
        assert all(inputs['metadata'][lane][k] == v for k,v in values.items())
    for url, entry in inputs['resources'].items():
        assert sha(ROOT/entry['path']) == entry['sha256']
        local = HERE/('mozilla/tests/'+url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else 'tests/'+url[1:])
        assert sha(local) == entry['sha256']
    actual = {'/'+str(p.relative_to(HERE/'tests')) for p in (HERE/'tests').rglob('*') if p.is_file()}
    actual |= {'/_mozilla/'+str(p.relative_to(HERE/'mozilla/tests')) for p in (HERE/'mozilla/tests').rglob('*') if p.is_file()}
    assert actual == set(inputs['resources'])
    assert sha(ROOT/inputs['capture_helper']['path']) == inputs['capture_helper']['sha256']
    assert (HERE/'MANIFEST.json').read_bytes() == (OLD/'MANIFEST.json').read_bytes()
    merged = read(OLD/'MOZILLA-MANIFEST.json')
    extra = read(NEW/'MOZILLA-MANIFEST.json')
    old_items = merged['items']['testharness']['css']['css-cascade']
    new_items = extra['items']['testharness']['css']['css-cascade']
    assert not set(old_items)&set(new_items)
    old_items.update(new_items)
    assert read(HERE/'MOZILLA-MANIFEST.json') == merged
    for page in lanes['mozilla_appearance']['roster']:
        rel = page[len('/_mozilla/'):]
        node = merged['items']['testharness']
        for part in rel.split('/'):node=node[part]
        body=(HERE/'mozilla/tests'/rel).read_bytes()
        assert node[0] == hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
    for name, value in {'METADATA.json':inputs['metadata'],'METADATA-ADMISSION.json':inputs['metadata_admission'],'METADATA-OVERLAYS.json':inputs['metadata_overlays']}.items():
        assert read(HERE/name) == value


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    inputs,roster,lanes = (read(HERE/n) for n in ['INPUTS.json','ROSTER.json','LANES.json'])
    verify(inputs,roster,lanes)
    negatives=0
    for mutate in [lambda a,b,c:a.update(callbacks=74),lambda a,b,c:b.pop(PAGE),lambda a,b,c:c['mozilla_appearance'].update(pages=1),lambda a,b,c:a['metadata_admission'].pop(NATIVE_META)]:
        a,b,c=map(copy.deepcopy,(inputs,roster,lanes));mutate(a,b,c)
        try:verify(a,b,c)
        except (AssertionError,KeyError):negatives+=1
        else:raise AssertionError('invalid suite accepted')
    print(json.dumps({'callbacks':77,'pages':12,'signatures':89,'sealed_resources':16,'exact74_subset':True,'source_packages':2,'negative_controls':negatives,'live_admission':False}))
