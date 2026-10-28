import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
r=load('publication_runner',HERE/'run.py'); b=load('publication_bindings',HERE/'bindings.py')
p=r.read(HERE/'POLICY.json'); original=b.validate_original(ROOT,HERE,p,r)
parser=r.load('publication_assessor',HERE/'assess.py');checks=r.load('publication_checks',ROOT/p['helpers']['checks'])
directory=ROOT/p['paired_runtime']/'candidate-wpt'
events=[json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines()]
policy=dict(p,original_binding={'historical_original':p['paired_runtime']+'/original-wpt'})
assessment=parser.assess(events,r.read(directory/'RESULT.json')['exit'],policy,checks,original=original,run_binding=r.read(directory/'APPLICATION-METADATA.json'))
assert assessment['complete'] and assessment['comparison_gate_passed']
published=r.augment_assessment(assessment,phase='candidate-1',capsule_sha='a'*64,epoch_sha='b'*64,policy=policy,capsule_directory=str(HERE.relative_to(ROOT)),experiment_sha=r.sha(HERE/'EXPERIMENT.json'),execution_preserved=True)
assert all(json.loads(json.dumps(published))[k]==json.loads(json.dumps(v)) for k,v in assessment.items())
try:
 r.augment_assessment(dict(assessment,phase='wrong'),phase='candidate-1',capsule_sha='a'*64,epoch_sha='b'*64,policy=policy,capsule_directory='control',experiment_sha='c'*64,execution_preserved=True)
except RuntimeError: pass
else: raise AssertionError('publication collision accepted')
report={'historical_candidate_raw_assessment_replayed':34,'historical_comparison_gate':True,'actual_augmentation_preserves_all_assessor_fields':True,'publication_collision_rejected':True,'new_final_browser_run':False}
(HERE/'PUBLICATION-CONTROLS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
