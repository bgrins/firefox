import json
import os
from pathlib import Path
import subprocess

from mutations import replace_once

MUTATIONS={
    'omit-start-entry-restore':('width := if candidate then s.start.intrinsic else s.start.width','width := s.start.width'),
    'omit-end-entry-restore':('width := if candidate then s.finish.intrinsic else s.finish.width','width := s.finish.width'),
    'omit-canonical-restore':('def canonical (m : Marker) : Marker := { reset m with width := m.intrinsic }','def canonical (m : Marker) : Marker := reset m'),
    'retry-reset-destroys-clipping':('def reset (m : Marker) : Marker := { m with overflow := false, block := -1, edge := false }','def reset (m : Marker) : Marker := { m with width := m.intrinsic, overflow := false, block := -1, edge := false }'),
}
WITNESS='''import LineModel
open LineModel
def c : Config := {id := 0,start := 0,width := 100,styles := #[⟨2,11,1⟩,⟨2,13,1⟩],seed := true,ellipsisWidth := 0,ellipsisFailure := false,scroll := none,snap := false,units := 1,lines := []}
def s : Pair := ⟨{width := 3,intrinsic := 11,initialized := true,active := true,overflow := true,edge := true}, {width := 7,intrinsic := 13,style := 1,initialized := true,active := true,overflow := true,edge := true}⟩
def main : IO Unit := do
  for values in [markers (entry c s true),packed (canonical s.start),packed (reset s.start)] do
    IO.println ("[" ++ String.intercalate "," (values.map toString) ++ "]")
'''


def check(base,out,lean,command):
    source=(base/'LineModel.lean').read_text()
    witness=out/'Witness.lean';witness.write_text(WITNESS)
    env={**os.environ,'LEAN_PATH':str(out)}
    command([lean,'--run',witness],out/'witness-baseline.jsonl',env=env)
    expected=[json.loads(x) for x in (out/'witness-baseline.jsonl').read_text().splitlines()]
    receipts={}
    for name,(old,new) in MUTATIONS.items():
        target=out/('lean-mutant-'+name);target.mkdir()
        model=target/'LineModel.lean';model.write_text(replace_once(source,old,new))
        env={**os.environ,'LEAN_PATH':str(target)}
        command([lean,'-o',target/'LineModel.olean',model],target/'compile.log',env=env)
        with (target/'proof-rejection.log').open('w') as log:
            result=subprocess.run([str(lean),str(base/'LineTheorems.lean')],stdout=log,stderr=subprocess.STDOUT,env=env,timeout=60)
        assert result.returncode!=0,name
        rejection=(target/'proof-rejection.log').read_text()
        assert 'error:' in rejection or 'error(' in rejection
        command([lean,'--run',witness],target/'witness.jsonl',env=env)
        actual=[json.loads(x) for x in (target/'witness.jsonl').read_text().splitlines()]
        changed=[i for i in range(len(expected)) if expected[i]!=actual[i]]
        assert changed,name
        receipts[name]={'model_compile_exit':0,'proof_exit':result.returncode,
          'theorem_elided_execution_exit':0,'changed_records':changed,
          'expected':expected,'actual':actual}
    return receipts
