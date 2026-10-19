import CompositionWitnesses
namespace Wiring

def raw (c : LiveCount.Chain Nat Nat) := c.flatten
def indexed (s : LiveCount.Store Nat Nat) (i : Nat) := LiveCount.getIndex (raw s.chain) s.stored i
def owner (c : LiveCount.Chain Nat Nat) (k : Nat) := LiveCount.owner c k

end Wiring
