import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from controls_v2 import MUTATIONS, MODULES
from diagnostics import errors
from expectations_v2 import EXPECTED_CALLS, EXPECTED_AXIOMS
import source_check_v2

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(name, index, source, path, code, stdout, stderr):
    expected = EXPECTED_CALLS[name][index]
    inventory = errors(source, path, stdout)
    actual = {'module': path.name, 'exit_code': code, 'stderr': stderr, 'errors': inventory}
    if actual != expected:
        raise ValueError('Unexpected compilation record')
    if code == 0 and stdout != EXPECTED_AXIOMS[path.name]:
        raise ValueError('Axiom audit mismatch')
    return actual


def guards(positive, negative):
    name, index, source, path, code, stdout, stderr = positive
    n, i, s, p, c, out, err = negative
    tests = {
        'positive-nonzero': (name,index,source,path,1,stdout,stderr),
        'positive-stderr': (name,index,source,path,code,stdout,'unexpected'),
        'missing-audit': (name,index,source,path,code,'\n'.join(stdout.splitlines()[1:])+'\n',stderr),
        'extra-audit': (name,index,source,path,code,stdout+'extra\n',stderr),
        'unchecked-axiom': (name,index,source,path,code,stdout.replace('Quot.sound','sorryAx',1),stderr),
        'mutation-success': (n,i,s,p,0,out,err),
        'mutation-no-error': (n,i,s,p,c,'',err),
        'mutation-stderr': (n,i,s,p,c,out,'unexpected'),
        'foreign-path': (n,i,s,p,c,out.replace(str(p),'/foreign/Candidate.lean'),err),
        'unlocated-error': (n,i,s,p,c,out+'error: unlocated\n',err),
        'outside-proof-error': (n,i,s,p,c,out+f'{p}:1:1: error: injected\n',err),
        'unexpected-error-text': (n,i,s,p,c,out.replace('Application type mismatch','unexpected diagnostic'),err),
    }
    rejected=[]
    for label, args in tests.items():
        try:
            validate(*args)
        except (ValueError, KeyError):
            rejected.append(label)
        else:
            raise ValueError('Poisoned record accepted: '+label)
    return rejected


def main():
    if sys.flags.optimize or len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--live'):
        raise ValueError('Usage: python3 check_v2.py NEW_OUTPUT_DIRECTORY [--live]')
    out=Path(sys.argv[1]).resolve()
    out.mkdir()
    manifest=json.loads((BASE/'SOURCE-v2.json').read_text())
    for name,expected in manifest['companion_hashes'].items():
        if sha(BASE/name)!=expected:
            raise ValueError('Frozen companion mismatch: '+name)
    pins=[BASE/name for name in manifest['companion_hashes']]+[BASE/'SOURCE-v2.json',LEAN]
    if len(sys.argv)==3:
        native=json.loads((BASE/'NATIVE-v2.json').read_text())
        pins += [ROOT/native['generic_path']] + [ROOT/path for path in native['helper_sha256']]
    before={str(path):sha(path) for path in pins}
    native_out=out/'native'
    native_out.mkdir()
    binding=source_check_v2.run(native_out,len(sys.argv)==3)
    (out/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    base_result=subprocess.run([sys.executable,str(BASE/'check.py'),str(out/'preparation')],capture_output=True,text=True)
    (out/'preparation.stdout.log').write_text(base_result.stdout)
    (out/'preparation.stderr.log').write_text(base_result.stderr)
    if base_result.returncode != 0 or base_result.stderr:
        raise ValueError('Frozen preparation replay failed')
    preparation=json.loads((out/'preparation/report.json').read_text())
    models={name:(BASE/name).read_text() for name in MODULES}
    for model in models.values():
        if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',model.replace('#print axioms','')):
            raise ValueError('Unchecked model construct')
    cases=[]
    records={}
    for name, mutation in {'positive':None,**MUTATIONS}.items():
        folder=out/name
        folder.mkdir()
        for module,source in models.items():
            if mutation and module==mutation[0]:
                old,new=mutation[1:]
                if source.count(old)!=1:
                    raise ValueError('Mutation target count: '+name)
                source=source.replace(old,new)
            (folder/module).write_text(source)
        calls=[]
        for index,module in enumerate(MODULES):
            path=folder/module
            env=os.environ.copy()
            env['LEAN_PATH']=str(folder)
            env.pop('LEAN_SRC_PATH',None)
            command=[str(LEAN),'-DwarningAsError=true','-Dlinter.unusedVariables=false',
                     '-Dlinter.unusedSimpArgs=false','-o',str(path.with_suffix('.olean')),str(path)]
            result=subprocess.run(command,capture_output=True,text=True,env=env)
            path.with_suffix('.stdout.log').write_text(result.stdout)
            path.with_suffix('.stderr.log').write_text(result.stderr)
            args=(name,index,path.read_text(),path,result.returncode,result.stdout,result.stderr)
            record=validate(*args)
            records[(name,module)]=args
            calls.append({**record,'command':command,'source_sha256':sha(path),
                          'stdout_sha256':sha(path.with_suffix('.stdout.log')),
                          'stderr_sha256':sha(path.with_suffix('.stderr.log'))})
            if result.returncode:
                break
        if len(calls)!=len(EXPECTED_CALLS[name]):
            raise ValueError('Incomplete compiler sequence: '+name)
        cases.append({'name':name,'calls':calls})
    rejected=guards(records[('positive','Candidate.lean')],records[('WrongLowerWinner','Candidate.lean')])
    after={str(path):sha(path) for path in pins}
    if before!=after:
        raise ValueError('Inputs changed during proof run')
    report={'status':'pass','live_native_verified':len(sys.argv)==3,'inputs':before,'inputs_after':after,
            'axiom_audits':sum(len(value.splitlines()) for value in EXPECTED_AXIOMS.values()),
            'compiled_mutations':len(MUTATIONS)+preparation['compiled_mutations'],
            'record_guards':len(rejected)+len(preparation['record_guards']),
            'new_record_guard_names':rejected,'source_controls':len(binding['source_controls']),
            'preparation_exit_code':base_result.returncode,'cases':cases,'native_binding':binding,
            'limits':manifest['limits']}
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'inputs','inputs_after','cases','native_binding'}},sort_keys=True))


if __name__=='__main__':
    main()
