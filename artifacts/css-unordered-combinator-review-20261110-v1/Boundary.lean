import JsonV2

namespace ReviewUnordered
open CssGrammar CssUnordered

def k (s : String) : Grammar := .keyword s

theorem three_equal_occurrences : [] ∈ CssUnordered.run [k "a", k "a", k "a"] ["a", "a", "a"] := by decide
theorem four_equal_tokens_refused : [] ∉ CssUnordered.run [k "a", k "a", k "a"] ["a", "a", "a", "a"] := by decide
theorem left_nested_interleaving_refused : [] ∉ CssUnordered.run [(lower [k "a", k "b"]).getD (k "invalid"), k "c"] ["a", "c", "b"] := by decide
theorem complete_left_chunk : [] ∈ CssUnordered.run [(lower [k "a", k "b"]).getD (k "invalid"), k "c"] ["b", "a", "c"] := by decide
theorem repeated_suffix_preserved : ["a", "a"] ∈ CssUnordered.run [k "a", k "b"] ["b", "a", "a", "a"] := by decide
theorem nullable_alternative_refused : lower [.alt (k "a") (.optional (k "b")), k "c"] = none := by decide
theorem invalid_inner_optional_not_rescued : decode [.legacy (.keyword "a"), .legacy .optional, .legacy (.keyword "b"), .unordered 2, .legacy .optional] = none := by decide
theorem stack_suffix_preserved : step (.unordered 2) [k "b", k "a", k "sentinel"] = (lower [k "a", k "b"]).map (fun g => [g, k "sentinel"]) := by decide
theorem semantic_relation_not_admission : UnorderedMatches [.optional (k "a"), k "b"] [] [] := by
  refine ⟨[⟨0, by decide⟩], by decide, by decide, ?_⟩
  exact ⟨[], .absent, rfl⟩

end ReviewUnordered
