import Unordered
import SelectionLaws

namespace CssUnordered
open CssGrammar

theorem nullable_spec (grammar : Grammar) : nullable grammar = true ↔ Matches grammar [] [] :=
  accepts_iff grammar []

theorem valid_spec (children : List Grammar) : valid children = true ↔ Admissible children := by
  simp [valid, Admissible, Bool.and_eq_true, List.all_eq_true, ← nullable_spec]

theorem sequence_matches (first : Grammar) (tail : List Grammar) (input rest : List String) :
    Matches (sequence first tail) input rest ↔ MatchList (first :: tail) input rest := by
  induction tail generalizing first input rest with
  | nil => simp [sequence, MatchList]
  | cons head tail ih => simp [sequence, MatchList, seq_iff, ih]

theorem sequence_spec (children : List Grammar) (input rest : List String) :
    (∃ grammar, sequence? children = some grammar ∧ Matches grammar input rest) ↔
      children ≠ [] ∧ MatchList children input rest := by
  cases children <;> simp [sequence?, sequence_matches]

theorem alternatives_matches (first : Grammar) (tail : List Grammar) (input rest : List String) :
    Matches (alternatives first tail) input rest ↔ ∃ grammar ∈ first :: tail, Matches grammar input rest := by
  induction tail generalizing first with
  | nil => simp [alternatives]
  | cons head tail ih => simp [alternatives, alt_iff, ih]

theorem alternatives_spec (children : List Grammar) (input rest : List String) :
    (∃ grammar, alternatives? children = some grammar ∧ Matches grammar input rest) ↔
      ∃ grammar ∈ children, Matches grammar input rest := by
  cases children <;> simp [alternatives?, alternatives_matches]

theorem plans_spec (children : List Grammar) (input rest : List String) :
    (∃ grammar ∈ plans children, Matches grammar input rest) ↔ UnorderedMatches children input rest := by
  constructor
  · rintro ⟨grammar, member, derivation⟩
    obtain ⟨indices, order, plan⟩ := List.mem_filterMap.mp member
    obtain ⟨nonempty, sequenceMatch⟩ := (sequence_spec _ input rest).mp ⟨grammar, plan, derivation⟩
    exact ⟨indices, by simpa using nonempty, (index_orders_spec _).mp order, sequenceMatch⟩
  · rintro ⟨indices, nonempty, unique, derivation⟩
    obtain ⟨grammar, plan, grammarMatch⟩ := (sequence_spec _ input rest).mpr ⟨by simpa using nonempty, derivation⟩
    exact ⟨grammar, List.mem_filterMap.mpr ⟨indices, (index_orders_spec _).mpr unique, plan⟩, grammarMatch⟩

theorem lowering_spec (children : List Grammar) (input rest : List String) :
    (∃ grammar, lower children = some grammar ∧ Matches grammar input rest) ↔
      Admissible children ∧ UnorderedMatches children input rest := by
  by_cases accepted : valid children = true
  · simp [lower, accepted, alternatives_spec, plans_spec, ← valid_spec]
  · simp [lower, accepted, ← valid_spec]

theorem run_spec (children : List Grammar) (input rest : List String) :
    rest ∈ run children input ↔ Admissible children ∧ UnorderedMatches children input rest := by
  have contract := lowering_spec children input rest
  cases result : lower children with
  | none => simpa [run, result] using contract
  | some grammar => simpa [run, result, CssGrammar.run_iff] using contract

theorem lower_matching (children : List Grammar) (grammar : Grammar)
    (result : lower children = some grammar) (input rest : List String) :
    Matches grammar input rest ↔ Admissible children ∧ UnorderedMatches children input rest := by
  simpa [result] using lowering_spec children input rest

theorem nullable_operand_refused (children : List Grammar) (child : Grammar)
    (member : child ∈ children) (empty : Matches child [] []) : lower children = none := by
  have rejected : valid children ≠ true := by
    intro accepted
    exact (valid_spec children).mp accepted |>.2 child member empty
  simp [lower, rejected]

theorem short_arity_refused (children : List Grammar) (short : children.length < 2) : lower children = none := by
  have rejected : valid children ≠ true := by
    intro accepted
    have enough := (valid_spec children).mp accepted |>.1
    omega
  simp [lower, rejected]

theorem exact_remainder (children : List Grammar) (input rest : List String)
    (member : rest ∈ run children input) : ∃ consumed, input = consumed ++ rest := by
  cases result : lower children with
  | none => simp [run, result] at member
  | some grammar =>
    exact remainder_suffix ((CssGrammar.run_iff grammar input rest).mp (by simpa [run, result] using member))

theorem append_remainder (children : List Grammar) (input rest suffix : List String)
    (member : rest ∈ run children input) : (rest ++ suffix) ∈ run children (input ++ suffix) := by
  cases result : lower children with
  | none => simp [run, result] at member
  | some grammar =>
    have derivation := (CssGrammar.run_iff grammar input rest).mp (by simpa [run, result] using member)
    simpa [run, result, CssGrammar.run_iff] using matches_append derivation suffix

end CssUnordered
