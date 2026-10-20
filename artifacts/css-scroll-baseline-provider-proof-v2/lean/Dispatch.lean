import Provider
namespace ScrollBaselineDispatch
open ScrollBaselineProvider

structure Input where
  first : Bool
  lineLayout : Bool
  block : Bool
  button : Bool
  contain : Bool
  outer : Int
  inner : Int
  border : Int
  fallback : Int
  child : Option Int
  deriving Repr, DecidableEq

inductive Event where
  | queryBlock | queryButton | fallback | containment | child | inner | border | outer
  deriving Repr, DecidableEq

structure Output where
  value : Option Int
  calls : List Event
  deriving Repr, DecidableEq

def sourceClamp (size value : Int) : Int :=
  let result := if size < value then size else value
  if 0 > result then 0 else result

theorem native_primitive_is_clamp (size value : Int) : sourceClamp size value = clamp size value := by
  unfold sourceClamp clamp
  dsimp
  split <;> split <;> omega

def continuation (i : Input) (prelude : List Event) : Output :=
  if i.contain then ⟨none, prelude ++ [.containment]⟩
  else match i.child with
    | none => ⟨none, prelude ++ [.containment, .child]⟩
    | some d =>
      let fromStart := if i.first then d else i.inner - d
      let baseline := max 0 (min i.outer (i.border + fromStart))
      ⟨some (if i.first then baseline else i.outer - baseline),
        prelude ++ [.containment, .child] ++
          (if i.first then [] else [.inner]) ++ [.border, .outer]⟩

def native (i : Input) : Output :=
  if i.lineLayout && !i.first then
    if i.block then
      if !i.button then ⟨some i.fallback, [.queryBlock, .queryButton, .fallback]⟩
      else continuation i [.queryBlock, .queryButton]
    else continuation i [.queryBlock]
  else continuation i []

inductive Route where
  | synthesized | suppressed | absent | delegated
  deriving Repr, DecidableEq

def legacy (i : Input) : Bool := i.lineLayout && !i.first && i.block && !i.button

def route (i : Input) : Route :=
  if legacy i then .synthesized
  else if i.contain then .suppressed
  else if i.child.isSome then .delegated else .absent

def physicalBaseline (i : Input) (d : Int) : Int :=
  let point := i.border + (if i.first then d else i.inner - d)
  if point < 0 then 0 else if point > i.outer then i.outer else point

def reference (i : Input) : Option Int :=
  match route i with
  | .synthesized => some i.fallback
  | .suppressed | .absent => none
  | .delegated => i.child.map fun d =>
      let point := physicalBaseline i d
      if i.first then point else i.outer - point

def prelude (i : Input) : List Event :=
  if i.lineLayout && !i.first then
    if i.block then [.queryBlock, .queryButton] else [.queryBlock]
  else []

def expectedCalls (i : Input) : List Event :=
  match route i with
  | .synthesized => [.queryBlock, .queryButton, .fallback]
  | .suppressed => prelude i ++ [.containment]
  | .absent => prelude i ++ [.containment, .child]
  | .delegated => prelude i ++ [.containment, .child] ++
      (if i.first then [] else [.inner]) ++ [.border, .outer]

theorem clamp_matches_independent_piecewise (i : Input) (d : Int)
    (size : 0 ≤ i.outer) :
    clamp i.outer (i.border + fromStart i.first i.inner d) = physicalBaseline i d := by
  unfold clamp physicalBaseline fromStart
  dsimp
  split <;> split <;> (try split) <;> omega

theorem continuation_value (i : Input) (p : List Event) :
    (continuation i p).value =
      if i.contain then none else i.child.map (repaired i.first i.outer i.inner i.border) := by
  cases h : i.contain <;> cases f : i.first <;> cases d : i.child <;>
    simp [continuation, h, f, d, repaired, fromStart, clamp]

theorem native_value_split (i : Input) :
    (native i).value = if legacy i then some i.fallback else
      if i.contain then none else i.child.map (repaired i.first i.outer i.inner i.border) := by
  rcases i with ⟨f,l,b,t,c,o,n,s,v,d⟩
  cases f <;> cases l <;> cases b <;> cases t <;> cases c <;> cases d <;> rfl

theorem full_value_refinement (i : Input) (size : 0 ≤ i.outer) :
    (native i).value = reference i := by
  rw [native_value_split]
  unfold reference route
  split
  · rfl
  · split
    · rfl
    · cases h : i.child with
      | none => simp
      | some d =>
        simp only [Option.isSome_some, ↓reduceIte, Option.map_some]
        have same := clamp_matches_independent_piecewise i d size
        unfold repaired
        rw [same]
        rfl

theorem exact_ordered_calls (i : Input) : (native i).calls = expectedCalls i := by
  rcases i with ⟨f,l,b,t,c,o,n,s,v,d⟩
  cases f <;> cases l <;> cases b <;> cases t <;> cases c <;> cases d <;>
    rfl

theorem synthesis_precedes_containment (i : Input) (yes : legacy i = true) :
    native i = ⟨some i.fallback, [.queryBlock, .queryButton, .fallback]⟩ := by
  have value := native_value_split i
  have calls := exact_ordered_calls i
  simp only [yes, ↓reduceIte] at value
  simp [expectedCalls, route, yes] at calls
  cases h : native i
  simp_all

theorem containment_without_legacy (i : Input) (no : legacy i = false)
    (yes : i.contain = true) : (native i).value = none := by
  simp [native_value_split, no, yes]

theorem absence_preserved (i : Input) (no : legacy i = false)
    (missing : i.child = none) : (native i).value = none := by
  simp [native_value_split, no, missing]

theorem delegated_zero_is_present (i : Input) (no : legacy i = false)
    (clear : i.contain = false) (child : i.child = some 0) :
    (native i).value = some (repaired i.first i.outer i.inner i.border 0) := by
  simp [native_value_split, no, clear, child]

theorem first_does_not_query_inner (i : Input) (first : i.first = true) :
    Event.inner ∉ (native i).calls := by
  rw [exact_ordered_calls]
  rcases i with ⟨f,l,b,t,c,o,n,s,v,d⟩
  cases f <;> cases l <;> cases b <;> cases t <;> cases c <;> cases d <;>
    simp_all [expectedCalls,route,legacy,prelude]

theorem signed_border_intermediates_fit (inner border distance : Int)
    (hi : 0 ≤ inner ∧ inner ≤ 2147483647)
    (hb : -2147483648 ≤ border ∧ border ≤ 2147483647)
    (hd : -2147483648 ≤ distance ∧ distance ≤ 2147483647) :
    -9223372036854775808 ≤ inner - distance ∧
    inner - distance ≤ 9223372036854775807 ∧
    -9223372036854775808 ≤ border + inner - distance ∧
    border + inner - distance ≤ 9223372036854775807 ∧
    -9223372036854775808 ≤ border + distance ∧
    border + distance ≤ 9223372036854775807 := by omega

theorem all_candidate_operations_fit (i : Input) (d : Int)
    (outer : 0 ≤ i.outer ∧ i.outer ≤ 2147483647)
    (inner : 0 ≤ i.inner ∧ i.inner ≤ 2147483647)
    (border : -2147483648 ≤ i.border ∧ i.border ≤ 2147483647)
    (distance : -2147483648 ≤ d ∧ d ≤ 2147483647) :
    -9223372036854775808 ≤ fromStart i.first i.inner d ∧
    fromStart i.first i.inner d ≤ 9223372036854775807 ∧
    -9223372036854775808 ≤ i.border + fromStart i.first i.inner d ∧
    i.border + fromStart i.first i.inner d ≤ 9223372036854775807 ∧
    0 ≤ clamp i.outer (i.border + fromStart i.first i.inner d) ∧
    clamp i.outer (i.border + fromStart i.first i.inner d) ≤ 2147483647 ∧
    0 ≤ repaired i.first i.outer i.inner i.border d ∧
    repaired i.first i.outer i.inner i.border d ≤ 2147483647 := by
  have wide := signed_border_intermediates_fit i.inner i.border d inner border distance
  have narrow := narrowing_and_final_subtraction_fit i.first i.outer i.inner i.border d outer
  cases h : i.first <;> simp_all [fromStart] <;> omega

def originalNative (i : Input) : Output :=
  if legacy i then ⟨some i.fallback,[.queryBlock,.queryButton,.fallback]⟩
  else if i.contain then ⟨none,prelude i ++ [.containment]⟩
  else match i.child with
    | none => ⟨none,prelude i ++ [.containment,.child]⟩
    | some d => ⟨some (original i.outer i.border d),prelude i ++ [.containment,.child,.border,.outer]⟩

theorem first_group_complete_output_preserved (i : Input) (first : i.first = true) :
    native i = originalNative i := by
  rcases i with ⟨f,l,b,t,c,o,n,s,v,d⟩
  cases f <;> cases l <;> cases b <;> cases t <;> cases c <;> cases d <;>
    simp_all [native,originalNative,legacy,prelude,continuation,original,clamp]

theorem no_metadata_queries_when_absent (i : Input) (missing : i.child = none)
    (no : legacy i = false) :
    (native i).calls = prelude i ++ (if i.contain then [.containment] else [.containment,.child]) := by
  rw [exact_ordered_calls]
  cases h : i.contain <;> simp [expectedCalls,route,no,missing,h]

theorem none_iff_no_selected_provider (i : Input) :
    (native i).value = none ↔ legacy i = false ∧ (i.contain = true ∨ i.child = none) := by
  rw [native_value_split]
  cases h : legacy i <;> cases c : i.contain <;> cases d : i.child <;> simp

theorem outputs_agree_outside_delegation (i : Input)
    (outside : route i ≠ .delegated) : native i = originalNative i := by
  rcases i with ⟨f,l,b,t,c,o,n,s,v,d⟩
  cases f <;> cases l <;> cases b <;> cases t <;> cases c <;> cases d <;>
    simp_all [route,native,originalNative,legacy,prelude,continuation]

end ScrollBaselineDispatch
