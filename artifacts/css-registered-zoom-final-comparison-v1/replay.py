import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def replay():
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize,'isolated Python')
    refs=read(HERE/'REFERENCES.json');evidence=read(HERE/'EVIDENCE.json')
    for name,pin in refs.items():need(sha(ROOT/name)==pin,'frozen evidence:'+name)
    final_cap=ROOT/evidence['phases'][-1]['capsule'];helper=load('helper',final_cap/'run.py')
    assessments=[];provenance=[];prior_inputs={};final_inputs=None
    for record in evidence['phases']:
        capsule=ROOT/record['capsule'];runtime=ROOT/record['runtime']
        helper.authenticate(capsule,record['manifest_sha256'])
        files={};links={}
        for path in runtime.rglob('*'):
            if path.is_symlink():links[str(path.relative_to(runtime))]=str(path.readlink())
            elif path.is_file():files[str(path.relative_to(runtime))]=sha(path)
        need(files==record['files'] and links==record['symlinks'],'complete immutable runtime inventory')
        assessment,result,epoch=[read(runtime/name) for name in ['ASSESSMENT.json','RESULT.json','EPOCH.json']]
        policy=read(capsule/'POLICY.json')
        need(assessment['complete'] and assessment['execution_preserved'] and not assessment['errors'] and not assessment['comparison_errors'],'complete preserved lifecycle')
        need(result['execution_error'] is None and result['preservation_error'] is None,'no wrapper error')
        need(assessment['capsule_manifest_sha256']==record['manifest_sha256'] and assessment['epoch_sha256']==sha(runtime/'EPOCH.json'),'capsule and actual epoch')
        need(assessment['native_sources']==policy['source_roles']['candidate'] and all(epoch['pins'].get(n)==pin for n,pin in assessment['native_sources'].items()),'actual native source map')
        need(read(runtime/'PRE.json')==read(runtime/'POST.json'),'full saved preservation')
        cleanup=read(runtime/'CLEANUP.json');need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'],'owned cleanup complete')
        metadata=read(runtime/'APPLICATION-METADATA.json')
        need(metadata==read(runtime/'APPLICATION-METADATA-POST.json')==assessment['run_binding'] and metadata['revision']==epoch['semantic_index']['head'],'actual unchanged metadata')
        need(read(runtime/'NORMAL-BINARIES.json')==policy['phase_binaries'] and all(epoch['pins'].get(n)==pin for n,pin in policy['phase_binaries'].items()),'actual binary pins')
        build=read(ROOT/policy['build_epoch']);build_result=read(ROOT/policy['build_result'])
        need(sha(ROOT/policy['build_epoch'])==policy['build_epoch_sha256'] and sha(ROOT/policy['build_result'])==policy['build_result_sha256'],'actual named build receipts')
        need(build_result['source_role']=='candidate' and build_result['command_success'] and build_result['preservation_verified'] and not build_result['owned_processes'] and not build_result['publication_errors'],'successful preserved candidate build')
        need(build['registered_number_transition']==epoch['registered_number_transition'] and epoch['registered_number_transition']['compiled'] and not epoch['registered_number_transition']['accepted'],'actual compiled unaccepted role')
        need(epoch['registered_number_transition']['last_phase']==Path(policy['build_result']).parent.name,'build path joins compiled phase')
        need({n:v for n,v in build['pins'].items() if not n.startswith('artifacts/')}=={n:v for n,v in epoch['pins'].items() if not n.startswith('artifacts/')} and build['installed_identities']==epoch['installed_identities'],'compiled body/identity continuity')
        need(read(runtime/'metadata/MANIFEST.json')==read(capsule/'SUBSET-MANIFEST.json'),'actual runtime manifest')
        inputs=read(capsule/'SOURCE-PINS.json')
        for name,item in inputs.items():
            relative=name.removeprefix('testing/web-platform/')
            path=runtime/('metadata/'+relative[5:] if relative.startswith('meta/') else relative)
            if item['exists']:
                need(path.is_file() and not path.is_symlink() and sha(path)==sha(capsule/item['capture'])==item['sha256'],'actual copied fixture/resource')
            else:need(not path.exists() and not path.is_symlink(),'absent copied input')
            abstract={'exists':item['exists'],'sha256':item.get('sha256')}
            if record['label']!='final668':
                need(name not in prior_inputs or prior_inputs[name]==abstract,'prior union consistent inputs');prior_inputs[name]=abstract
        if record['label']=='final668':final_inputs={name:{'exists':item['exists'],'sha256':item.get('sha256')} for name,item in inputs.items()}
        parser=load('assessor',capsule/'assess.py');checks=load('checks',ROOT/policy['helpers']['checks'])
        raw=[json.loads(line) for line in (runtime/'raw.jsonl').read_text().splitlines()]
        generated=parser.assess(raw,result['exit'],policy,checks,original=None,run_binding=metadata)
        need(generated['complete'] and all(assessment.get(k)==v for k,v in generated.items() if k not in {'subtest_cardinality_policy','oracle_caveat'}),'exact raw parser replay')
        assessments.append(assessment);provenance.append({'label':record['label'],'runtime':record['runtime'],'assessment_sha256':sha(runtime/'ASSESSMENT.json'),'raw_sha256':sha(runtime/'raw.jsonl'),'epoch_sha256':sha(runtime/'EPOCH.json'),'build_result':policy['build_result'],'build_result_sha256':policy['build_result_sha256'],'build_head':build['semantic_index']['head'],'observation_head':epoch['semantic_index']['head'],'metadata':metadata})
    need(prior_inputs==final_inputs,'same31 fixture/resource/metadata bytes')
    normalizer_dir=ROOT/evidence['normalizer'];helper.authenticate(normalizer_dir,refs[str((normalizer_dir/'FILES.json').relative_to(ROOT))]);normalizer=load('strict_ports',normalizer_dir/'replay.py')
    experiment=read(final_cap/'EXPERIMENT.json');declared=normalizer.references(read(final_cap/'SUBSET-MANIFEST.json'),experiment)
    previous={'rows':assessments[0]['rows']+assessments[1]['rows'],'ends':assessments[0]['ends']+assessments[1]['ends']}
    verdict=load('comparison',HERE/'compare.py').compare(previous,assessments[2],experiment,normalizer,declared)
    payload_dir=ROOT/evidence['payload'];helper.authenticate(payload_dir,refs[str((payload_dir/'FILES.json').relative_to(ROOT))]);payload=read(payload_dir/'PAYLOAD.json')
    payload_pins={n:r['candidate_sha256'] for n,r in payload['source_roles'].items()}
    for name,role in payload['source_roles'].items():need(sha(payload_dir/role['payload'])==payload_pins[name],'sealed final payload body')
    final_epoch=read(ROOT/evidence['phases'][-1]['runtime']/'EPOCH.json')
    need(all(final_epoch['pins'].get(n)==pin and n in final_epoch['installed_identities'] for n,pin in payload_pins.items()),'actual final14 payload pins and identities')
    final_policy=read(final_cap/'POLICY.json');need({n:p for n,p in payload_pins.items() if n.startswith('testing/')}==final_policy['installed_tests'],'exact seven installed final WPTs')
    lint=read(ROOT/evidence['lint']/'RESULT.json')
    need(lint['exit']==0 and lint['native_and_wpt_bodies_preserved'] and lint['source_pins']==payload_pins,'successful actual payload WPT lint')
    need(set(lint['tests'])==set(final_policy['installed_tests']),'exact seven lint targets')
    verdict.update(status_counts=dict(Counter(row['status'] for row in assessments[2]['rows'])),same31_fixture_resource_metadata_bytes=True,three_raw_lifecycles_replayed=True,actual_final_payload_and_build_bound=True,actual_seven_WPT_lint_passed=True)
    for name,pin in refs.items():need(sha(ROOT/name)==pin,'evidence unchanged after replay:'+name)
    return {'verdict':verdict,'provenance':provenance}

if __name__=='__main__':
    print(json.dumps(replay(),indent=2,sort_keys=True))
