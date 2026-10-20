from pathlib import Path
import json,re,subprocess

def decode(text):
    def unique(items):
        d={}
        for k,v in items:
            if k in d:raise RuntimeError('duplicate field')
            d[k]=v
        return d
    return json.loads(text,object_pairs_hook=unique)

def payload_valid(value):
    return value is None or (type(value) is list and len(value)==7 and all(type(x) is int for x in value))

def model_rows(text,records):
    rows=[decode(x) for x in text.splitlines()]
    if len(rows)!=len(records):raise RuntimeError('model count')
    for c,r in zip(records,rows):
        if type(r) is not dict or set(r)!={'id','safe','core','shift','machine','reference','complete_pair_equal'}:raise RuntimeError('model fields')
        if type(r['id']) is not int or r['id']!=c['id']:raise RuntimeError('model id')
        if any(type(r[k]) is not bool for k in ['safe','core','shift','complete_pair_equal']):raise RuntimeError('model bool')
        if not payload_valid(r['machine']) or not payload_valid(r['reference']):raise RuntimeError('model payload')
    return rows

def expected_trace(c):
    g=c['guard']
    return [] if g in [1,2] else [907,907] if g==3 else [907,407] if g in [4,5] else [907,407,407,207,1170,1121,1172,700,302]

def native_row(text,c,reference):
    actual=decode(text)
    if type(actual) is not dict or set(actual)!={'value','trace'} or not payload_valid(actual['value']):raise RuntimeError('native fields')
    if type(actual['trace']) is not list or any(type(x) is not int for x in actual['trace']):raise RuntimeError('native trace type')
    if actual['value']!=reference or actual['trace']!=expected_trace(c):raise RuntimeError('native observable mismatch')
    return actual

def cases():
    return [{"id":i,"hazard":h,"guard":g,"horizontal":a} for i,(h,g,a) in
      enumerate((h,g,a) for h in range(4) for g in range(6) for a in [False,True])]

def lean_source():
    return r"""import Lean
import StickyFullChallenges
open Lean StickyNumeric StickyConsumers StickyEndpoints StickyFullEndpoint StickyFullChallenges RootCrossAxis

def frameFor (h : Nat) : Frame2 :=
  if h == 0 then ordinary else if h == 1 then shiftFrame else if h == 2 then coreFrame else boundedFrame

def scenario (h g : Nat) (axis : Bool) : Bool × List Frame2 :=
  let f := if axis then frameFor h else swapFrame (frameFor h)
  let frames := if g == 2 then [{f with sticky := false}] else if g == 3 then [f,f]
    else if g == 4 then [{f with hasOffsets := false}]
    else if g == 5 then [if axis then {f with x := {f.x with insets := ⟨none,none⟩}}
                        else {f with y := {f.y with insets := ⟨none,none⟩}}]
    else [f]
  (g != 1,frames)

def payload (early late : Int) (d : Option Displacement) : Json :=
  match d with
  | none => Json.null
  | some v => toJson ([v.shift,v.near.atScroll,v.near.maxOffset,v.far.atScroll,v.far.maxOffset,early,late] : List Int)

def main : IO Unit := do
  let mut id := 0
  for h in [0:4] do
    for g in [0:6] do
      for axis in [false,true] do
        let (container,frames) := scenario h g axis
        let safe := decide (EntrySafe2 container axis frames)
        let m := machineEntry container axis frames
        let r := mathEntry container axis frames
        let early := machineEvaluate (fullCaller2 container axis true 50 frames)
        let late := machineEvaluate (fullCaller2 container axis false 50 frames)
        let re := expected container axis true 50 frames
        let rl := expected container axis false 50 frames
        IO.println (Json.mkObj [("id",toJson id),("safe",toJson safe),
          ("core",toJson m.core.isSome),("shift",toJson m.shift.isSome),
          ("machine",payload early late m.displacement),("reference",payload re rl r.displacement),
          ("complete_pair_equal",toJson (decide (m=r)))]).compress
        id := id+1
"""

def run(root,output,tools,command):
    from generate import generate
    records=cases()
    src=output/'FullEntry.cpp';src.write_text(generate('combined','full_entry_driver.cpp'))
    model=output/'FullEntry.lean';model.write_text(lean_source())
    command([tools['lean'],'--run',str(model)],'full-entry-model')
    raw=model_rows((output/'full-entry-model.log').read_text(),records)
    for c,r in zip(records,raw):
        expected_safe=c['hazard']==0 or c['guard']!=0
        if type(r['safe']) is not bool or r['safe']!=expected_safe:raise RuntimeError('full-entry domain '+str(c))
        if r['safe'] and (r['machine']!=r['reference'] or not r['complete_pair_equal']):raise RuntimeError('full-entry reference '+str(c))
        if c['guard']!=0 and (r['core'] or r['shift'] or r['machine'] is not None):raise RuntimeError('early return '+str(c))
    native=[]
    for name,flag in [('debug','-O0'),('optimized','-O2')]:
        binary=output/('full-entry-'+name)
        command([tools['clang'],'-std=c++20',flag,'-fsanitize=undefined','-fno-sanitize-recover=all',str(src),'-o',str(binary)],'full-entry-'+name+'-compile')
        for c,r in zip(records,raw):
            stem='full-entry-'+name+'-'+str(c['id'])
            rc=command([str(binary),str(c['hazard']),str(c['guard']),str(int(c['horizontal']))],stem,expected=None)
            text=(output/(stem+'.log')).read_text()
            if r['safe']:
                if rc!=0:raise RuntimeError('admitted native failed '+stem)
                actual=native_row(text,c,r['reference'])
                core_entered=207 in actual['trace']
                if core_entered!=r['core']:raise RuntimeError('core entry trace mismatch '+stem)
            else:
                if rc==0 or 'signed integer overflow' not in text:raise RuntimeError('missing overflow witness '+stem)
            native.append({'case':c,'mode':name,'exit':rc,'safe':r['safe'],'raw':text})
    (output/'FULL-ENTRY-NATIVE.json').write_text(json.dumps(native,indent=2)+'\n')
    mutations=[('stripped-positive','StickyFullEndpoint',None,None),('omit-y-core','StickyFullEndpoint','StickyMachineGeometry.ArithmeticSafe (coreCodes f).2','True'),
      ('omit-y-shift','StickyFullEndpoint','Admitted (shiftCodes f).2','True'),
      ('eager-core-domain','StickyFullEndpoint','entersCore xAxis f = true →','True →')]
    results=[]
    base=(root/'lean/StickyFullEndpoint.lean').read_text()
    base=re.sub(r'^theorem [\s\S]*?(?=^theorem |^def |^instance |^structure |^end )','',base,flags=re.M)
    driver=lean_source().replace('import StickyFullChallenges','import StickyFullChallenges\nimport FullEntryMutant')
    for name,module,before,after in mutations:
        if before is not None and base.count(before)!=1:raise RuntimeError('mutation site '+name)
        mutated=(base if before is None else base.replace(before,after)).replace('namespace StickyFullEndpoint','namespace FullEntryMutant').replace('end StickyFullEndpoint','end FullEntryMutant')
        target=output/'FullEntryMutant.lean';target.write_text(mutated)
        command([tools['lean'],'-o',str(output/'lean/FullEntryMutant.olean'),str(target)],'full-entry-mutant-'+name+'-compile')
        text=driver.replace('EntrySafe2 container axis frames','FullEntryMutant.EntrySafe2 container axis frames')
        test=output/'FullEntryMutantDriver.lean';test.write_text(text)
        command([tools['lean'],'--run',str(test)],'full-entry-mutant-'+name)
        actual=model_rows((output/('full-entry-mutant-'+name+'.log')).read_text(),records)
        diff=[a['id'] for a,b in zip(actual,raw) if a['safe']!=b['safe']]
        if bool(diff)!=(before is not None):raise RuntimeError('domain mutation discrimination '+name)
        (output/('FullEntryMutant-'+name+'.lean')).write_text(mutated)
        results.append({'name':name,'changed_domain_rows':diff,'compile_success':True})
    result={'cases':len(records),'admitted':sum(r['safe'] for r in raw),'rejected':sum(not r['safe'] for r in raw),'native_runs':len(native),'domain_mutation_records':results,'scope':'Actual full selected caller, both-axis UB witnesses, branch-sensitive domain and complete model pair refinement; no browser reachability inferred.'}
    (output/'FULL-ENTRY-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
