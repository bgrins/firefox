import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LAB=ROOT/'artifacts/css-keyframe-custom-property-probe-20261110-v1'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(LAB/'RUN-INPUTS.json')=='261cb17d27f8bcd032d50f6c3effd5adf39aa34ee4628177dbfc92634a5a32d8'
    assert all(sha(LAB/n)==d for n,d in load(LAB/'RUN-INPUTS.json').items())
    plan=load(LAB/'RUN-PLAN.json');directory=LAB/'baseline1';before=load(directory/'BEFORE.json');result=load(directory/'RESULT.json')
    assert result['head']==plan['head']==before['head']
    assert result['runner_inputs_sha256']==sha(LAB/'RUN-INPUTS.json')
    assert set(result['commands'])=={'lint'} and result['commands']['lint']['exit_code']==1
    assert 'WPT lint failed' in result['error']
    assert result['restoration_verified'] and result['restoration_errors']==[]
    assert result['sampled_binaries'] is None and result['observation_count'] is None
    assert not (directory/'wpt-raw.jsonl').exists() and not (directory/'BUILD.json').exists()
    log=(directory/'lint.log').read_text();assert 'CONSOLE' in log and 'console' in log
    spec=importlib.util.spec_from_file_location('review_bundle',LAB/'bundle.py');bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
    assert bundle.semantic(bundle.scan(ROOT/'objdir-full.noindex/dist/Nightly.app'))==bundle.semantic(before['app'])
    assert bundle.semantic({p:bundle.entry(ROOT/p) for p in before['extras']})==bundle.semantic(before['extras'])
    retained=load(LAB/'runtime-inputs/retained-build.json')
    assert all(sha(ROOT/n)==d for n,d in retained['sources'].items())
    assert all(sha(ROOT/n)==d for n,d in retained['binaries'].items())
    assert sha(ROOT/'mozconfig')==plan['mozconfig_sha256']
    for n,d in load(LAB/'runtime-inputs/test-source-pins.json').items():
        assert not ((ROOT/n).exists() or (ROOT/n).is_symlink()) if d is None else sha(ROOT/n)==d
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=ROOT)
    assert git('rev-parse','HEAD').decode().strip()==plan['head']
    assert hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==before['index']
    assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
    assert not (directory/'backups').exists() and not (LAB/'runtime.lock').exists()
    assert load(directory/'RESTORED.json')['backup_removed']
    process=load(directory/'lint.process.json');assert process['state']=='terminal' and process['group_absent']
    alive={int(parts[0]) for line in (HERE/'process-snapshot.txt').read_text().splitlines() if len(parts:=line.split())==3 and not parts[1].startswith('Z')}
    assert process['pgid'] not in alive
    print(json.dumps({'status':'PASS','lint_failure_only':True,'browser_executed':False,'application_entries_restored':len(before['app']),'extras_restored':len(before['extras']),'source_test_binary_config_HEAD_index_restored':True,'owned_group_absent':True,'temporary_fixture_backups_lock_absent':True},indent=2))
if __name__=='__main__':main()
