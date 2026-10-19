NAMES={'provider-classification','ordinary-sibling-membership','late-guard-start-preservation','self-versus-fallback','signed-extrema-retention'}


def selected(f):
    return f['domain'] in NAMES and f['output']==1


def boolean(x): return 'true' if x else 'false'
def integer(x): return f'({x} : Int)'
def size(x): return 'none' if x==1073741823 else f'(some {x})'


def tree(f,idx=0):
    n=f['nodes'][idx]
    children=[x for x in f['lines'] if x['owner']==idx]
    forest='Forest.nil'
    for line in reversed(children):
        if line['inline']:
            forest=f'(Forest.inline {boolean(line["empty"])} {forest})'
        else:
            forest=f'(Forest.child {tree(f,line["child"])} {forest})'
    dims=f'⟨{size(n["preferred"])}, {size(n["minimum"])}, {n["paddingStart"]}, {n["paddingEnd"]}⟩'
    frame=f'⟨{idx}, {integer(n["start"])}, {integer(n["end"])}, {boolean(n["selfEmpty"])}, {boolean(n["empty"])}, {boolean(n["hidden"])}, {boolean(n["marginRoot"] or not n["block"])}, {dims}⟩'
    return f'(Tree.frame {frame} {forest})'


def render(base,fixtures):
    prelude='''
namespace Collapse
set_option maxRecDepth 100000
set_option maxHeartbeats 0
def resultText (idx : Nat) (revised : Bool) (t : Tree) : String :=
  let r := visitWith revised t
  let s := aggregate r.edges
  let edges := r.edges.map (fun e => match e with
    | .start id _ => "S" ++ toString id
    | .finish id _ => "E" ++ toString id)
  toString idx ++ " " ++ toString revised ++ " " ++ toString (value s) ++ " " ++
    toString s.positive ++ " " ++ toString s.negative ++ " " ++ toString r.through ++ " | " ++ String.intercalate " " edges
'''
    parts=[base,prelude]
    for i,f in enumerate(fixtures):
        if selected(f):
            parts.append(f'#eval IO.println (resultText {i} false {tree(f)})\n#eval IO.println (resultText {i} true {tree(f)})')
    parts.append('end Collapse')
    return '\n'.join(parts)


def expected(fixtures):
    result=[]
    for i,f in enumerate(fixtures):
        if selected(f):
            for revised,key in [(False,'original_expected'),(True,'candidate_expected')]:
                nums,events=f[key].split(' |')
                nums=nums.split()
                edges=[e for e in events.split() if e[0] in 'SE']
                result.append(f'{i} {str(revised).lower()} '+ ' '.join(nums[:3])+ ' '+str(nums[4]=='1').lower()+' | '+' '.join(edges))
    return result
