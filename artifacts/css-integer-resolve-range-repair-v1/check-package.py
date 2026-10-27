#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path
P=Path(__file__).resolve().parent

def run(args,cwd):
    p=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert p.returncode==0,(args,p.stdout)
    return p.stdout

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists()
    receipt={'transport':{},'fixtures':{},'metadata_changed':False}
    native='servo/components/style/values/specified/number.rs'
    wpt='testing/web-platform/tests/css/css-easing/timing-functions-calculated-step-range.html'
    with tempfile.TemporaryDirectory(prefix='integer-range-package-') as td:
        t=Path(td)
        for role,source in [('head90','number-head90.rs'),('installed118','number-118.rs')]:
            root=t/role;root.mkdir();run(['git','init','-q'],root)
            dest=root/native;dest.parent.mkdir(parents=True);dest.write_bytes((P/'sources'/source).read_bytes())
            old=dest.read_bytes();new=(P/(role+'-candidate-number.rs')).read_bytes()
            assert old.replace(b'let value = calc.as_number()?.get();',b'let value = calc.clamping_mode.clamp(calc.as_number()?.get());',1)==new
            patch=str(P/(role+'-standalone.patch'))
            run(['git','apply','--check',patch],root);run(['git','apply',patch],root)
            assert dest.read_bytes()==new
            assert (root/wpt).read_bytes()==(P/'timing-functions-calculated-step-range.html').read_bytes()
            run(['git','apply','--reverse','--check',patch],root);run(['git','apply','--reverse',patch],root)
            assert dest.read_bytes()==old and not (root/wpt).exists()
            receipt['transport'][role]={'apply_reverse':'PASS','native_sha256':hashlib.sha256(new).hexdigest(),'paths':[native,wpt]}
        for name,count in [('timing-functions-calculated-step-range.html',24),('subgrid-calc-zero-diagnostic.html',1)]:
            html=(P/name).read_text();scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
            js=t/(name+'.js');js.write_text('\n'.join(scripts));run(['/opt/homebrew/bin/node','--check',str(js)],t)
            registration=t/'register.js';registration.write_text('const names=[]; global.test=(f,n)=>names.push(n);\n'+js.read_text()+'\nconsole.log(JSON.stringify(names));')
            names=json.loads(run(['/opt/homebrew/bin/node',str(registration)],t));assert len(names)==count==len(set(names))
            receipt['fixtures'][name]={'count':count,'names':names,'syntax':'PASS','callbacks_executed':False}
    receipt['temporary_products_removed']=True
    args.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
