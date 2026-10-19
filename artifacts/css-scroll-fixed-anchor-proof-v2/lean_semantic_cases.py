import lean_cases
import semantic


DIRECT = r'''
def printDirect (id : Nat) (o : Obs) : IO Unit := do
  let old := decisionCode (classify false o)
  let new := decisionCode (classify true o)
  IO.println s!"{id} {old} {old} {new} {new} D2:{old} D2:{old} D2:{new} D2:{new}"
'''

GRAPH = r'''
def printGraph (id : Nat) (nodes : Array Node) (gates : Gates) (ranks : Array Nat) : IO Unit := do
  let g : Graph := fun i => nodes[i]!
  let childBound := fun parent slot =>
    !Traversal.eligible g slot || decide (ranks[Traversal.resolved g slot]! < ranks[parent]!)
  let valid := (List.range nodes.size).all fun parent =>
    ((g parent).lists.all fun item => !ordinary item.1 || item.2.all (childBound parent)) &&
    (absolutePass (g parent).lists).all (childBound parent)
  unless valid && decide (ranks[1]! < nodes.size) do
    throw (IO.userError "invalid supplied rank")
  let os := Traversal.specificationPublic false g gates nodes.size 1
  let on := Traversal.nativePublic false g gates nodes.size 1
  let ns := Traversal.specificationPublic true g gates nodes.size 1
  let nn := Traversal.nativePublic true g gates nodes.size 1
  IO.println s!"{id} {Traversal.resultCode os} {Traversal.resultCode on} {Traversal.resultCode ns} {Traversal.resultCode nn} {Traversal.traceCode os.trace} {Traversal.traceCode on.trace} {Traversal.traceCode ns.trace} {Traversal.traceCode nn.trace}"
'''


def generate(cases):
    source = lean_cases.generate(cases)
    before = source.index('def printDirect ')
    after = source.index('\n#eval ', before)
    source = source[:before] + DIRECT + GRAPH + source[after:]
    rows = []
    by_id = {c['id']: c for c in cases}
    for row in source.splitlines():
        if row.startswith('#eval printGraph '):
            case = by_id[int(row.split()[2])]
            row += ' #[' + ','.join(map(str, semantic.validate(case))) + ']'
        rows.append(row)
    return '\n'.join(rows).replace('import Anchor', 'import Traversal', 1) + '\n' 
