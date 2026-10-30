import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('saved_review',HERE/'review.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
config,owner=r.authenticate();assert not config['execution_enabled']
policy=r.read(owner/'POLICY.json');roles=r.read(owner/'SOURCE-ROLES.json')
pair=r.ROOT/config['runtime_directory']
pre,app,extra,backup=(r.read(pair/name) for name in ('CANDIDATE-PRE.json','APP-PRE.json','EXTRA-PRE.json','BACKUPS.json'))
admission=r.read(r.ROOT/policy['source_equivalence']['path'])
size=r.saved_inventory(pre,app,extra,backup,roles,policy,admission)
assert size==1008605176
negatives=0
for kind in ('wrong-file-hash','wrong-source-identity','missing-mapping','extra-backup'):
    changed_pre=copy.deepcopy(pre);changed_backup=copy.deepcopy(backup)
    file=next(name for name,row in changed_backup['owned_inventory'].items() if row['kind']=='file')
    if kind=='wrong-file-hash':changed_backup['owned_inventory'][file]['sha256']='0'*64
    elif kind=='wrong-source-identity':changed_pre['sources'][next(iter(roles))]['identity'][1]+=1
    elif kind=='missing-mapping':changed_backup['app'].pop(next(iter(changed_backup['app'])))
    else:changed_backup['owned_inventory']['unowned']=copy.deepcopy(changed_backup['owned_inventory'][file])
    try:r.saved_inventory(changed_pre,app,extra,changed_backup,roles,policy,admission)
    except AssertionError:negatives+=1
    else:raise AssertionError(kind+' accepted')
assert negatives==4
print(json.dumps({'saved_receipts_authenticated':True,'backup_inventory_bytes':size,'negative_cases':negatives,'live_checks_run':False,'deletion_performed':False}))
