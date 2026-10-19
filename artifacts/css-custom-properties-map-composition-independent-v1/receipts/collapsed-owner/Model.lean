import CompositionWitnesses
namespace Wiring

def raw (c : LiveCount.Chain Nat Nat) := MapIterator.drain (MapIterator.start c)
def indexed (s : LiveCount.Store Nat Nat) (i : Nat) := LiveCount.getIndex (raw s.chain) s.stored i
def owner (c : LiveCount.Chain Nat Nat) (k : Nat) := (LiveCount.lookup c k).map some

end Wiring
