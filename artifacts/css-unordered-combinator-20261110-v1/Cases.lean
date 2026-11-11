import TextLaws

namespace CssUnordered
open CssGrammar

def a : Grammar := .keyword "a"
def b : Grammar := .keyword "b"
def c : Grammar := .keyword "c"
def nested : Grammar := (lower [b, c]).getD a

theorem duplicate_text_single : [] ∈ run [a, a] ["a"] := by decide
theorem duplicate_text_twice : [] ∈ run [a, a] ["a", "a"] := by decide
theorem duplicate_text_thrice_rejected : [] ∉ run [a, a] ["a", "a", "a"] := by decide
theorem flat_permutation : [] ∈ run [a, b, c] ["b", "a", "c"] := by decide
theorem nested_not_flat : [] ∉ run [a, nested] ["b", "a", "c"] := by decide
theorem grouping_changes_language : run [a, b, c] ["b", "a", "c"] ≠ run [a, nested] ["b", "a", "c"] := by decide
theorem nested_contiguous : [] ∈ run [a, nested] ["b", "c", "a"] := by decide
theorem optional_nullable_refused : lower [.optional a, b] = none := by decide
theorem all_optional_refused : lower [.optional a, .optional b] = none := by decide
theorem optional_required_allowed : [] ∈ run [.seq (.optional a) b, c] ["c", "b"] := by decide
theorem optional_required_present : [] ∈ run [.seq (.optional a) b, c] ["c", "a", "b"] := by decide
theorem nested_nullable_refused : decode [.legacy (.keyword "a"), .legacy .optional,
    .legacy (.keyword "b"), .unordered 2, .legacy (.keyword "c"), .legacy .seq,
    .legacy (.keyword "d"), .unordered 2] = none := by decide
theorem arity_zero_refused : decode [.unordered 0] = none := by decide
theorem arity_one_refused : decode [.legacy (.keyword "a"), .unordered 1] = none := by decide
theorem underflow_refused : decode [.legacy (.keyword "a"), .unordered 2] = none := by decide
theorem trailing_stack_refused : decode [.legacy (.keyword "a"), .legacy (.keyword "b")] = none := by decide
theorem trailing_suffix : ["tail"] ∈ run [a, b] ["b", "a", "tail"] := by decide
theorem suffix_not_swallowed : [] ∉ run [a, b] ["b", "a", "tail"] := by decide
theorem empty_refused : [] ∉ run [a, b] [] := by decide
theorem single_allowed : [] ∈ run [a, b] ["b"] := by decide
theorem text_none_isolated : accepts textGrammar ["none", "full-width"] = false := by decide
theorem text_case_exclusive : accepts textGrammar ["uppercase", "lowercase"] = false := by decide
theorem text_reverse : accepts textGrammar ["full-size-kana", "full-width", "uppercase"] = true := by decide
theorem text_full_suffix : ["tail"] ∈ CssGrammar.run textGrammar ["full-width", "uppercase", "tail"] := by decide

end CssUnordered
