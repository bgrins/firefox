import Count
namespace LiveCount
structure TrialStore where
  chain : Chain Nat String
  stored : Nat

def trialInsert (s : TrialStore) (k : Nat) (v : Option String) : TrialStore :=
  ⟨insert s.chain k v, if (lookup s.chain k).isSome && !v.isSome then s.stored else updateCount s.stored (lookup s.chain k).isSome v.isSome⟩
end LiveCount
