import AttributeObservers
namespace PostGuardObservers

def nameOnlyAttributeLookup (attributes : Nat → Option String) (query : AttributeQuery) :=
 attributes query.1

theorem namespace_erasure_aliases_every_pair (attributes : Nat → Option String)
 (name leftNamespace rightNamespace : Nat) :
 nameOnlyAttributeLookup attributes (name,leftNamespace) =
 nameOnlyAttributeLookup attributes (name,rightNamespace) := rfl

theorem namespace_distinguishing_provider_cannot_be_encoded
 (provider : Nat → Nat → Option String) (name leftNamespace rightNamespace : Nat)
 (distinct : provider name leftNamespace ≠ provider name rightNamespace) :
 ¬ ∃ attributes : Nat → Option String,
   nameOnlyAttributeLookup attributes (name,leftNamespace) = provider name leftNamespace ∧
   nameOnlyAttributeLookup attributes (name,rightNamespace) = provider name rightNamespace := by
 rintro ⟨attributes,left,right⟩
 exact distinct (left.symm.trans right)

theorem distinct_literal_lengths_cannot_share_one_lookup (attributes : Nat → Option String)
 (name leftNamespace rightNamespace : Nat) :
 ¬ (nameOnlyAttributeLookup attributes (name,leftNamespace) = some "13px" ∧
    nameOnlyAttributeLookup attributes (name,rightNamespace) = some "37px") := by
 intro both
 have impossible : (some "13px" : Option String) = some "37px" := both.1.symm.trans both.2
 contradiction

#print axioms namespace_distinguishing_provider_cannot_be_encoded
#print axioms distinct_literal_lengths_cannot_share_one_lookup
end PostGuardObservers
