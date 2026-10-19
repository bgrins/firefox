import argparse
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--lean',required=True);p.add_argument('--modules',type=Path,required=True);p.add_argument('--native',type=Path,required=True);a=p.parse_args()
cases=json.loads((ROOT/'native/CASES.json').read_text())
rows=[]
for i,c in enumerate(cases):
 if c['model']:rows.append((i,c['css'].encode()))
code='''import NumericScanner
set_option maxRecDepth 10000
set_option maxHeartbeats 10000000
open NumericDigits
 def hexDigit (n : Nat) : String := String.singleton (Char.ofNat (if n<10 then 48+n else 87+n))
 def hexBytes (xs : List Byte) : String := String.join (xs.map fun b => hexDigit (b.val/16) ++ hexDigit (b.val%16))
 def observe (i : Nat) (xs : List Byte) : IO Unit := do
  if !NumericEntry.nativeStart xs then throw (IO.userError "unadmitted numeric input")
  let r := NumericToken.native xs
  let independent := NumericToken.reference xs
  if r != independent then throw (IO.userError "reference mismatch")
  let kind := match r.kind with | .number => "number" | .percentage => "percentage" | .dimension => "dimension"
  IO.println s!"{i}\\t{kind}\\t{r.count}\\t{hexBytes r.unit}\\t{NumericUnits.tokenFlags r}\\t{r.numeric.hasSign}\\t{r.numeric.isInteger}\\t{hexBytes r.rest}"
'''
for i,b in rows:code+='#eval observe '+str(i)+' ['+','.join(str(n) for n in b)+']\n'
path=a.modules.resolve()/'Observations.lean';path.write_text(code)
r=subprocess.run([a.lean,str(path)],cwd=a.modules,env={**__import__('os').environ,'LEAN_PATH':str(a.modules.resolve())},capture_output=True,text=True)
(a.modules/'OBSERVATIONS.stdout').write_text(r.stdout);(a.modules/'OBSERVATIONS.stderr').write_text(r.stderr)
assert r.returncode==0,r.stdout+r.stderr
native=a.native.read_text().splitlines();observed=r.stdout.splitlines();assert len(observed)==len(rows)
for line in observed:
 f=line.split('\t');i=int(f[0]);n=native[i].split('\t')
 assert f[1:]==n[:6]+[n[8]],(cases[i],f,n)
print(json.dumps({'status':'PASS','native_to_lean_rows':len(observed),'fields':['token_kind','consumed_byte_count','decoded_unit_bytes','native_unit_flags','has_sign','syntactic_integer','remaining_bytes'],'payload':'not compared to mathematical real'}))
