import RawAdmission
namespace ShadowOrder

def rawMatchedRules (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) : List Rule :=
 candidates.filterMap (materialize tree table)

theorem matched_rule_admission (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) (valid : candidates.all (rawRuleAdmission table) = true)
 (rule : Rule) (member : rule ∈ rawMatchedRules tree table candidates) :
 ∃ candidate ∈ candidates,
   rawRuleAdmission table candidate = true ∧ materialize tree table candidate = some rule := by
 rcases List.mem_filterMap.mp member with ⟨candidate,hc,hr⟩
 exact ⟨candidate,hc,List.all_eq_true.mp valid candidate hc,hr⟩

theorem matched_rule_ties (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) (valid : candidates.all (rawRuleAdmission table) = true)
 (a b : Rule) (ha : a ∈ rawMatchedRules tree table candidates)
 (hb : b ∈ rawMatchedRules tree table candidates)
 (keys : completeLocalKey a = completeLocalKey b) : a = b := by
 rcases matched_rule_admission tree table candidates valid a ha with ⟨ca,hca,hva,hma⟩
 rcases matched_rule_admission tree table candidates valid b hb with ⟨cb,hcb,hvb,hmb⟩
 exact materialize_tie tree table ca cb a b hva hvb hma hmb keys

theorem arbitrary_native_local_sort (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) (valid : candidates.all (rawRuleAdmission table) = true)
 (nativeSorted : List Rule)
 (permutation : nativeSorted.Perm (rawMatchedRules tree table candidates))
 (sorted : nativeSorted.Pairwise (fun a b => completeLocalKey a ≤ completeLocalKey b)) :
 nativeSorted = localSort completeLocalKey (rawMatchedRules tree table candidates) := by
 apply unique_sorted_observation completeLocalKey nativeSorted _
   (permutation.trans (sort_perm _ _).symm) sorted (sort_sorted _ _)
 intro a ha b hb keys
 exact matched_rule_ties tree table candidates valid a b
   (permutation.mem_iff.mp ha) (permutation.mem_iff.mp hb) keys

theorem local_layer_order (a b : Rule)
 (ha : a.specificity < 4294967296 ∧ a.proximity < 65536 ∧ a.sourceOrder < 16777216)
 (hb : b.specificity < 4294967296 ∧ b.proximity < 65536 ∧ b.sourceOrder < 16777216)
 (ordered : completeLocalKey a ≤ completeLocalKey b) : a.layer ≤ b.layer := by
 have ap : 65535-a.proximity < 65536 := by omega
 have bp : 65535-b.proximity < 65536 := by omega
 have ab := local_key_bound a.specificity (65535-a.proximity) a.sourceOrder ha.1 ap ha.2.2
 have bb := local_key_bound b.specificity (65535-b.proximity) b.sourceOrder hb.1 bp hb.2.2
 unfold completeLocalKey at ordered
 omega


def ruleNumericBounds (rule : Rule) : Prop :=
 rule.layer < 65536 ∧ rule.specificity < 4294967296 ∧ rule.proximity < 65536 ∧
 rule.sourceOrder < 16777216

theorem materialized_numeric_bounds (tree : Nat) (table : List RawStyleRule)
 (candidate : RawSelectorResult) (rule : Rule)
 (valid : rawRuleAdmission table candidate = true)
 (made : materialize tree table candidate = some rule) : ruleNumericBounds rule := by
 simp only [rawRuleAdmission,Bool.and_eq_true,decide_eq_true_eq] at valid
 unfold materialize at made
 cases matched : candidate.matched <;> simp only [matched,Bool.not_false,Bool.not_true,↓reduceIte] at made
 · contradiction
 cases lookup : table[candidate.ordinal]? with
 | none => simp [lookup] at made
 | some block =>
   simp [lookup] at made
   subst rule
   have layer := valid.2
   simp [lookup] at layer
   exact ⟨layer,valid.1.1.2,valid.1.2,valid.1.1.1.2⟩

theorem matched_numeric_bounds (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) (valid : candidates.all (rawRuleAdmission table) = true)
 (rule : Rule) (member : rule ∈ rawMatchedRules tree table candidates) : ruleNumericBounds rule := by
 rcases matched_rule_admission tree table candidates valid rule member with ⟨c,hc,hv,hm⟩
 exact materialized_numeric_bounds tree table c rule hv hm

theorem raw_local_layer_sorted (tree : Nat) (table : List RawStyleRule)
 (candidates : List RawSelectorResult) (valid : candidates.all (rawRuleAdmission table) = true) :
 (localSort completeLocalKey (rawMatchedRules tree table candidates)).Pairwise
   (fun a b => a.layer ≤ b.layer) := by
 apply List.Pairwise.imp_of_mem _ (sort_sorted completeLocalKey (rawMatchedRules tree table candidates))
 intro a b ha hb keys
 have ba := matched_numeric_bounds tree table candidates valid a ((sort_perm _ _).mem_iff.mp ha)
 have bb := matched_numeric_bounds tree table candidates valid b ((sort_perm _ _).mem_iff.mp hb)
 exact local_layer_order a b ba.2 bb.2 keys

#print axioms arbitrary_native_local_sort
#print axioms local_layer_order
end ShadowOrder
