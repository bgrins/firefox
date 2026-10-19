import CompositionWitnesses
namespace Wiring

def raw (c : LiveCount.Chain Nat Nat) := MapIterator.drain (MapIterator.start c)
def indexed (s : LiveCount.Store Nat Nat) (i : Nat) := if s.stored ≤ i then none else (raw s.chain)[i]?
def owner (c : LiveCount.Chain Nat Nat) (k : Nat) := LiveCount.owner c k

end Wiring
