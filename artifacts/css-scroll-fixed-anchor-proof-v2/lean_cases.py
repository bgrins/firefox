PRELUDE = r'''
import Anchor
open Anchor
set_option maxRecDepth 4096
set_option maxHeartbeats 10000000

def gatesRaw (enabled : Bool) (bits : Nat) (disabled : Bool) (x y : Int) : Gates :=
  ⟨enabled, disabled, bits.testBit 13, decide ((if bits.testBit 11 then x else y) = 0), bits.testBit 10⟩

def obsRaw (enabled : Bool) (pos bits : Nat) (previous nested disabled : Bool)
    (lx ly x y w h : Int) : Obs :=
  let visible := decide (max x 0 < min (x+w) 100 ∧ max y 0 < min (y+h) 100)
  ⟨decide (pos = 3), bits.testBit 1, bits.testBit 0 && !bits.testBit 12,
   previous, bits.testBit 13, bits.testBit 2, bits.testBit 3 && !bits.testBit 12,
   bits.testBit 4, bits.testBit 5, bits.testBit 6, bits.testBit 7,
   bits.testBit 8 && (nested || maintain (gatesRaw enabled bits disabled lx ly)),
   visible, visible && decide (0 ≤ x ∧ 0 ≤ y ∧ x+w ≤ 100 ∧ y+h ≤ 100)⟩

def decisionCode : Decision → Nat
  | .exclude => 0 | .pass => 1 | .traverse => 2 | .accept => 3

def pickCode (p : Option Pick) : Int := (p.map (fun x => (x.id : Int))).getD (-1)
def idString (ids : List Nat) : String := String.intercalate "," (ids.map toString)

def printDirect (id : Nat) (o : Obs) : IO Unit :=
  IO.println s!"{id} {decisionCode (classify false o)} {decisionCode (classify true o)} 2 2"

def printGraph (id : Nat) (nodes : Array Node) (gates : Gates) : IO Unit := do
  let g : Graph := fun i => nodes[i]!
  let tree := unfoldGraph g nodes.size (successors g 1)
  let old := publicSelect gates false tree
  let new := publicSelect gates true tree
  let oldVisits := if maintain gates then visits false tree else []
  let newVisits := if maintain gates then visits true tree else []
  IO.println s!"{id} {pickCode old} {pickCode new} {idString oldVisits} {idString newVisits}"
'''


def boolean(v):
    return 'true' if v else 'false'


def number(v):
    return f'({v})' if v < 0 else str(v)


def observation(c, f):
    values = [boolean(c['enabled']), str(f['pos']), str(f['bits']), boolean(f['previous'] >= 0),
              boolean(f['nested'] >= 0), boolean(f['disabled']),
              *map(number, f['logical']), *map(number, f['rect'])]
    return '(obsRaw ' + ' '.join(values) + ')'


def generate(cases):
    rows = [PRELUDE]
    for c in cases:
        if c['mode'] == 1:
            rows.append(f'#eval printDirect {c["id"]} {observation(c,c["frames"][2])}')
            continue
        nodes = []
        for i, f in enumerate(c['frames']):
            p = f['parent']; within = False
            while p >= 0:
                within |= p == 0; p = c['frames'][p]['parent']
            kinds = ['principal', 'absolute', 'float', 'overflowFloats', 'fixed', 'other']
            lists = '[' + ','.join('(.%s,[%s])' % (kinds[k], ','.join(map(str, ids)))
                                  for k, ids in f['lists']) + ']'
            target = f'(some {f["target"]})' if f['target'] >= 0 else 'none'
            nodes.append('⟨%s,%s,%s,%s⟩' % (observation(c, f), lists, target, boolean(within)))
        f = c['frames'][0]
        gates = '(gatesRaw %s %s %s %s %s)' % (boolean(c['enabled']), f['bits'],
                  boolean(f['disabled']), *map(number, f['logical']))
        rows.append('#eval printGraph %s #[%s] %s' % (c['id'], ','.join(nodes), gates))
    return '\n'.join(rows) + '\n'
