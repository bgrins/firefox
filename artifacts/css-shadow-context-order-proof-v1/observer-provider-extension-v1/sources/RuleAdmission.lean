import Ordering
namespace ShadowOrder
structure RawStyleRule where
 source : Nat
 layer : Nat
 flags : Nat
 declarations : List Declaration
 deriving DecidableEq, Repr

structure RawSelectorResult where
 ordinal : Nat
 specificity : Nat
 proximity : Nat
 matched : Bool
 deriving DecidableEq, Repr

def materialize (tree : Nat) (table : List RawStyleRule) (candidate : RawSelectorResult) : Option Rule := do
 if !candidate.matched then none else
 let source ← table[candidate.ordinal]?
 return ⟨tree,source.source,source.layer,candidate.specificity,candidate.proximity,
   candidate.ordinal,source.flags,source.declarations⟩

def rawRuleAdmission (table : List RawStyleRule) (candidate : RawSelectorResult) : Bool :=
 candidate.ordinal < table.length && candidate.ordinal < 16777216 &&
 candidate.specificity < 4294967296 && candidate.proximity < 65536 &&
 (table[candidate.ordinal]?.map fun source => decide (source.layer < 65536)).getD false

def completeLocalKey (r : Rule) : Nat :=
 r.layer * 4722366482869645213696 + localKey r.specificity (65535-r.proximity) r.sourceOrder

theorem proximity_order (a b : Nat) (ha : a < 65536) (hb : b < 65536) :
 65535-a ≤ 65535-b ↔ b ≤ a := by omega

theorem complete_key_injective_fields (a b : Rule)
 (ha : a.specificity < 4294967296 ∧ a.proximity < 65536 ∧ a.sourceOrder < 16777216)
 (hb : b.specificity < 4294967296 ∧ b.proximity < 65536 ∧ b.sourceOrder < 16777216)
 (h : completeLocalKey a = completeLocalKey b) :
 a.layer = b.layer ∧ a.specificity = b.specificity ∧ a.proximity = b.proximity ∧
 a.sourceOrder = b.sourceOrder := by
 unfold completeLocalKey localKey at h
 omega

theorem materialize_tie (tree : Nat) (table : List RawStyleRule)
 (ca cb : RawSelectorResult) (a b : Rule)
 (haa : rawRuleAdmission table ca = true) (hba : rawRuleAdmission table cb = true)
 (ha : materialize tree table ca = some a) (hb : materialize tree table cb = some b)
 (key : completeLocalKey a = completeLocalKey b) : a = b := by
 simp only [rawRuleAdmission,Bool.and_eq_true,decide_eq_true_eq] at haa hba
 unfold materialize at ha hb
 cases hca : ca.matched <;> simp only [hca,Bool.not_false,Bool.not_true,↓reduceIte] at ha
 · contradiction
 cases hcb : cb.matched <;> simp only [hcb,Bool.not_false,Bool.not_true,↓reduceIte] at hb
 · contradiction
 cases hta : table[ca.ordinal]? with
 | none => simp [hta] at ha
 | some sa =>
   cases htb : table[cb.ordinal]? with
   | none => simp [htb] at hb
   | some sb =>
     simp [hta] at ha
     simp [htb] at hb
     subst a
     subst b
     have fields := complete_key_injective_fields _ _
       ⟨haa.1.1.2,haa.1.2,haa.1.1.1.2⟩
       ⟨hba.1.1.2,hba.1.2,hba.1.1.1.2⟩ key
     have ordinal : ca.ordinal = cb.ordinal := fields.2.2.2
     have source : sa = sb := by rw [ordinal,htb] at hta; exact Option.some.inj hta.symm
     cases ca
     cases cb
     simp_all

theorem unique_sorted_observation (key : α → Nat) (xs ys : List α)
 (permutation : xs.Perm ys)
 (sx : xs.Pairwise (fun a b => key a ≤ key b))
 (sy : ys.Pairwise (fun a b => key a ≤ key b))
 (ties : ∀ a ∈ xs, ∀ b ∈ xs, key a = key b → a = b) : xs = ys := by
 apply List.Perm.eq_of_pairwise _ sx sy permutation
 intro a b ha hb hab hba
 exact ties a ha b (permutation.mem_iff.mpr hb) (Nat.le_antisymm hab hba)

#print axioms materialize_tie
#print axioms unique_sorted_observation
end ShadowOrder
