import ProviderSorting
namespace ShadowOrder

theorem exact_map_admitted (table : List RawStyleRule) (maps : PseudoMap)
 (pseudos : List Nat)
 (valid : maps.all (fun entry => entry.2.all (rawRuleAdmission table)) = true) :
 ((pseudoMapLookup maps pseudos).toList.flatten).all (rawRuleAdmission table) = true := by
 induction maps with
 | nil => rfl
 | cons entry rest ih =>
   simp only [List.all_cons,Bool.and_eq_true] at valid
   by_cases found : entry.1 == pseudos
   · simp [pseudoMapLookup,List.find?,found,valid.1]
   · simpa [pseudoMapLookup,List.find?,found] using ih valid.2

theorem data_map_admitted (table : List RawStyleRule) (maps : PseudoMap)
 (pseudos : List Nat) (valid : rawMapValid table maps = true) :
 ((pseudoMapLookup maps pseudos).toList.flatten).all (rawRuleAdmission table) = true := by
 simp only [rawMapValid,Bool.and_eq_true] at valid
 exact exact_map_admitted table maps pseudos valid.2

theorem sorted_exact_map_layer_order (tree : Nat) (data : RawCascadeData)
 (maps : PseudoMap) (pseudos : List Nat) (valid : rawMapValid data.table maps = true) :
 (sortedMapRules tree data (pseudoMapLookup maps pseudos)).Pairwise
   (fun a b => a.layer ≤ b.layer) :=
 raw_local_layer_sorted tree data.table ((pseudoMapLookup maps pseudos).toList.flatten)
   (data_map_admitted data.table maps pseudos valid)

theorem exact_map_numeric_bounds (tree : Nat) (data : RawCascadeData)
 (maps : PseudoMap) (pseudos : List Nat) (valid : rawMapValid data.table maps = true)
 (rule : Rule) (member : rule ∈ mapRules tree data (pseudoMapLookup maps pseudos)) :
 ruleNumericBounds rule :=
 matched_numeric_bounds tree data.table ((pseudoMapLookup maps pseudos).toList.flatten)
   (data_map_admitted data.table maps pseudos valid) rule member

#print axioms exact_map_admitted
#print axioms sorted_exact_map_layer_order
end ShadowOrder
