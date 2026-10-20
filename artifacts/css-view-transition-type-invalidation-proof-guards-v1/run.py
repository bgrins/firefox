import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,os,shutil,subprocess
root=Path(sys.argv[1]).resolve();out=Path(__file__).resolve().parent
results=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(label,cmd,cwd,forbidden=()):
    r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    result=dict(label=label,command=cmd,exit=r.returncode,stdout=r.stdout,stderr=r.stderr,
        forbidden_created=[str(p) for p in forbidden if p.exists()])
    results.append(result);(out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    if r.returncode==0 or result['forbidden_created']:raise RuntimeError('negative failed '+label)
entries=['check.py','compile.py','native/build.py','source_extract.py','calibration.py','oracle.py']
modes=[[],['-S'],['-I'],['-I','-S','-O'],['-I','-S','-OO']]
for index,entry in enumerate(entries):
    for modeindex,mode in enumerate(modes):
        case=out/('mode-'+str(index)+'-'+str(modeindex));case.mkdir();script=case/'entry.py';shutil.copyfile(root/entry,script)
        marker=case/'shadow-executed';(case/'json.py').write_text("from pathlib import Path\nPath("+repr(str(marker))+").write_text('executed')\n")
        output=case/'forbidden-output';run('guard '+entry+' '+repr(mode),[sys.executable,*mode,str(script),'--output',str(output)],case,[marker,output])
        shutil.rmtree(case)
def reseal(case):
    rows=[dict(path=str(p.relative_to(case)),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(case.rglob('*')) if p.is_file() and p.name not in ['FILES.json','FREEZE.json']]
    (case/'FILES.json').write_text(json.dumps(rows,indent=2)+'\n');(case/'FREEZE.json').write_text(json.dumps(dict(FILES_sha256=digest(case/'FILES.json'),check_sha256=digest(case/'check.py')))+'\n')
for label in ['empty-directory','fifo','directory-symlink','nested-root-seal','changed-input','case-actor','case-bool','case-frame','case-omission','case-duplicate']:
    case=out/label;shutil.copytree(root,case);output=out/(label+'-forbidden-output')
    if label=='empty-directory':(case/'unexpected').mkdir()
    elif label=='fifo':os.mkfifo(case/'unexpected')
    elif label=='directory-symlink':(case/'unexpected').symlink_to(case/'lean',target_is_directory=True)
    elif label=='nested-root-seal':(case/'lean/FILES.json').write_text('{}')
    elif label=='changed-input':(case/'lean/Invalidation.lean').write_text((case/'lean/Invalidation.lean').read_text()+'\n')
    else:
        file=case/'native/CASES.json';cases=json.loads(file.read_text())
        if label=='case-actor':cases[18]['actions'][0][1]=2
        if label=='case-bool':cases[18]['actions'][0][1]=False
        if label=='case-frame':cases[18]['actions'][0].pop()
        if label=='case-omission':cases.pop()
        if label=='case-duplicate':cases[19]=cases[18]
        file.write_text(json.dumps(cases)+'\n');reseal(case)
    run(label,[sys.executable,'-I','-S',str(case/'check.py'),'--output',str(output)],out,[output]);shutil.rmtree(case)
r=subprocess.run([sys.executable,'-I','-S',str(root/'check.py'),'--help'],text=True,capture_output=True)
if r.returncode:raise RuntimeError(r.stderr)
results.append(dict(label='intact positive help',exit=r.returncode,stdout=r.stdout,stderr=r.stderr));(out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
(out/'SUMMARY.json').write_text(json.dumps(dict(complete=True,negative=40,positive=1,source_FILES_sha256=digest(root/'FILES.json'),source_FREEZE_sha256=digest(root/'FREEZE.json'),copied_guard_and_case_trees_cleaned=True),indent=2)+'\n')
print('40 negative controls and 1 positive control passed')
