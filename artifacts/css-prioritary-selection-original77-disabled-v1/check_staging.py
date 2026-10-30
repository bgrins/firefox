import configparser
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('staged_wpt', HERE/'wpt.py')
wpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
policy=read(HERE/'POLICY.json')
results=[]
with tempfile.TemporaryDirectory(prefix='css-original77-stage-',dir='/private/tmp') as scratch:
    scratch_path=Path(scratch)
    root=scratch_path/'root';root.mkdir()
    (root/'testing/web-platform/tests/tools').mkdir(parents=True)
    settings_list=copy.deepcopy(policy['wpt_lanes'])
    for settings in settings_list.values():
        pins=list(settings['resources'].values())+list(settings['manifests'].values())+list(settings['install_managed_resources'].values())
        pins += [record for entries in settings['metadata'].values() for record in entries.values() if record['sha256'] is not None]
        for record in pins:
            source=ROOT/record['path'];target=root/record['path'];target.parent.mkdir(parents=True,exist_ok=True)
            assert sha(source)==record['sha256'];target.write_bytes(source.read_bytes())
        server=root/settings['server_config']['path'];server.parent.mkdir(parents=True,exist_ok=True)
        server.write_text(json.dumps({'ports':{}}));settings['server_config']['sha256']=sha(server)
        config=root/settings['wpt_config'];config.parent.mkdir(parents=True,exist_ok=True)
        config.write_text('[paths]\n[web-platform-tests]\n[manifest:unused]\ntests=unused\n')
    capture_dir=Path(policy['capture_binding']['directory'])
    for name in ['capture.py','candidate.html','record.js','receive.py']:
        target=root/capture_dir/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/capture_dir/name).read_bytes())
    for lane in policy['lane_order']:
        output=scratch_path/lane;output.mkdir()
        path,capture=wpt.prepare_inputs(root,output,settings_list[lane],'original')
        config=configparser.ConfigParser(interpolation=None);config.read(path)
        assert set(s for s in config.sections() if s.startswith('manifest:'))=={'manifest:upstream','manifest:mozilla'}
        assert config['manifest:upstream']['url_base']=='/' and config['manifest:mozilla']['url_base']=='/_mozilla/'
        assert (output/'tests/resources/testharness.js').is_file()
        assert (output/'mozilla-tests/css/css-cascade/prioritary-appearance-selection.html').is_file()
        assert 'expected: FAIL' in (output/'metadata/forced-colors-mode/forced-colors-mode-51.html.ini').read_text()
        assert 'layout.css.appearance-base.enabled:true' in (output/'mozilla-metadata/css/css-cascade/prioritary-appearance-selection.html.ini').read_text()
        staged=read(output/'STAGED-RESOURCES.json')
        assert all(sha(output/name)==digest for name,digest in staged.items())
        assert (capture is not None)==(lane=='ordinary')
        assert (output/'tests/__research__/zoom/CONFIG.json').exists()==(lane=='ordinary')
        if capture:
            binding=read(output/'ZOOM-BINDING.json')
            assert binding['role']=='original'
            assert set(binding['resources'])=={'record.js','receive.py','CONFIG.json'}
        results.append({'lane':lane,'staged_hashes':len(staged),'two_roots':True,'expected_FAIL_preserved':True,'capture_installed':capture is not None})
assert not scratch_path.exists()
result={'lanes':results,'owned_scratch_removed':True,'processes_started':False,'browser_execution':False}
(HERE/'STAGING-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
