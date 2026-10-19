import argparse,json,os,subprocess
from pathlib import Path
args=argparse.ArgumentParser();args.add_argument('--root',required=True);args.add_argument('--lean',required=True);args=args.parse_args()
root=Path(args.root).resolve();out=root/'build';out.mkdir(exist_ok=True)
raw=(root/'consumer/seeds/measurement-coordinate-input.txt').read_text();rows=[]
header="""import MeasurementMachine
open HyphenMeasurementClassification HyphenMeasurementSelection HyphenMeasurementMachine
abbrev Glyph := Nat × Bool × Bool × Bool × Bool × Int × Int × Int × Kind
def priority : Priority → Nat | .none => 0 | .wordWrap => 1 | .normal => 2
def execute (id : String) (config : Configuration Int) (glyphs : List Glyph) (hyphenWidth : Int) : IO Unit := do
  let get : Nat → Glyph := fun index => glyphs[index]?.getD ⟨0,false,false,false,true,0,0,0,.none⟩
  let providers : Providers Int Int := {arithmetic := integerArithmetic, glyphKind := fun i => (get i).1, clusterStart := fun i => (get i).2.2.2.2.1, isSpace := fun i => (get i).2.1, isTab := fun i => (get i).2.2.1, isNewline := fun i => (get i).2.2.2.1, glyphAdvance := fun i => (get i).2.2.2.2.2.1, partialAdvance := fun i => (get i).2.2.2.2.2.1, spacing := fun first last => ((glyphs.drop first).take (last-first)).map (fun x => (x.2.2.2.2.2.2.1,x.2.2.2.2.2.2.2.1)), hyphenation := fun first last => ((glyphs.drop first).take (last-first)).map (fun x => x.2.2.2.2.2.2.2.2), allocation := fun _ _ _ => true, hyphenWidth := hyphenWidth, measure := fun first last => (((glyphs.drop first).take (last-first)).map (fun x => x.2.2.2.2.2.1)).foldl (·+·) 0}
  let result := run config providers
  IO.println s!"{id} {result.fit} {if result.usedHyphenation then 1 else 0} {result.lastBreak} {priority result.priority} {result.trimCount} {result.trimAdvance} {result.metrics}"
def main : IO Unit := do
"""
for line in raw.splitlines():
 tok=line.split();ident=tok[0];v=list(map(int,tok[1:]));start,length,width,option,suppress,linebefore,wordwrap,whitewrap,breakspaces,trim,flags,hywidth,letter,n=v[:14]
 assert len(v)==14+n*10
 glyphs=[v[14+i*10:24+i*10]for i in range(n)]
 assert flags==0 and letter==0 and all(x[5]and x[7]==0 and x[8]==0 for x in glyphs)
 assert all(abs(x[6])<2**30 for x in glyphs)
 kinds=['.none','.explicit','.soft','.autoWithManual','.autoWithoutManual'];boolean=lambda x:str(bool(x)).lower()
 encoded=','.join('⟨'+','.join([str(x[0]),boolean(x[1]),boolean(x[2]),boolean(x[3]),boolean(x[4]),str(x[6]),str(x[7]),str(x[8]),kinds[x[9]]])+'⟩'for x in glyphs)
 config=','.join(map(str,[start,length,n,width,boolean(linebefore),boolean(suppress==2),boolean(suppress==1),boolean(wordwrap),boolean(whitewrap),boolean(breakspaces),boolean(trim),'false','false',['.none','.manual','.auto'][option],start,min(start+length,n),'.none',4294967295,'false']))
 rows.append('  execute '+json.dumps(ident)+' ⟨'+config+'⟩ ['+encoded+'] '+str(hywidth))
driver=out/'MeasurementMachineDriver.lean';driver.write_text(header+'\n'.join(rows)+'\n')
env=dict(os.environ,LEAN_PATH=str(out));r=subprocess.run([str(Path(args.lean).resolve()),'--run',str(driver)],capture_output=True,text=True,env=env,timeout=180)
(out/'machine-driver.stdout').write_text(r.stdout);(out/'machine-driver.stderr').write_text(r.stderr);assert r.returncode==0,r.stderr+r.stdout
native=(root/'consumer/development-build/full/measurement-coordinate-output.txt').read_text().splitlines()
expected=[' '.join(line.split()[:8])for line in native];assert r.stdout.splitlines()==expected,(r.stdout,expected)
(out/'MACHINE-RESULT.json').write_text(json.dumps({'cases':len(rows),'input':'unchanged five coordinate fixtures','status':'all eight output fields agree with freshly rebuilt full native baseline','providers':'supplied fixture glyphs/integers/metrics and all-success allocation; no extra native requests or fresh actual font/dictionary admission claimed','native_request_trace_compared':False},indent=2)+'\n')
print('measurement machine',len(rows),'exact output rows')
