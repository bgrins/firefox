import SpacingValues
import SpacingRunAdmission
import TabSpacingAdmission

namespace HyphenSpacingPhases

open HyphenSpacingValues

structure Pair (Value : Type) where
  before : Value
  after : Value

structure Tab (Value : Type) where
  offset : Nat
  width : Value

def tabEntries (first finish : Nat) : List (Tab Value) → List (Write Value)
  | [] => []
  | tab::rest => if tab.offset < finish then
      ⟨tab.offset-first,.after,tab.width⟩ :: tabEntries first finish rest else []

def justificationEntries (queryStart queryEnd arrayStart : Nat) (spacings : List (Pair Value)) : List (Write Value) :=
  (List.range' queryStart (min queryEnd (arrayStart+spacings.length)-queryStart)).flatMap fun index =>
    match spacings[index-arrayStart]? with
    | some spacing => [⟨index-queryStart,.before,spacing.before⟩,⟨index-queryStart,.after,spacing.after⟩]
    | none => []

structure Input (Value : Type) where
  config : Config Value
  queryStart : Nat
  queryEnd : Nat
  textCombined : Bool
  ordinaryEnabled : Bool
  initial : Control
  units : List HyphenSpacingValues.Unit
  ignoreTabs : Bool
  tabWidthPositive : Bool
  tabCache : Option (List (Tab Value))
  tabFirst : Nat
  justificationStart : Nat
  justification : List (Pair Value)

structure Result (Value : Type) where
  store : Store Value
  present : Bool

def ordinary (input : Input Value) : NativeState Value :=
  let initial : NativeState Value := ⟨input.initial,fun _ _ => input.config.arithmetic.zero⟩
  if input.ordinaryEnabled then nativeLoop input.config initial input.units else initial

def tabWrites (input : Input Value) : List (Write Value) :=
  if !input.ignoreTabs && input.tabWidthPositive then
    match input.tabCache with
    | none => []
    | some tabs => tabEntries input.tabFirst (input.tabFirst+(input.queryEnd-input.queryStart)) tabs
  else []

def hasTabPhase (input : Input Value) : Bool :=
  !input.ignoreTabs && input.tabWidthPositive && input.tabCache.isSome

def native (input : Input Value) : Result Value :=
  if input.textCombined then ⟨fun _ _ => input.config.arithmetic.zero,false⟩ else
  let base := ordinary input
  let tabs := execute input.config.arithmetic base.store (tabWrites input)
  let final := execute input.config.arithmetic tabs
    (justificationEntries input.queryStart input.queryEnd input.justificationStart input.justification)
  ⟨final,base.control.present || hasTabPhase input || !input.justification.isEmpty⟩

def trace (input : Input Value) : List (Write Value) :=
  if input.textCombined then [] else
    (if input.ordinaryEnabled then referenceTrace input.config input.initial input.units else []) ++
      tabWrites input ++ justificationEntries input.queryStart input.queryEnd input.justificationStart input.justification

theorem complete_pointwise (input : Input Value) (index : Nat) (side : Side) :
    (native input).store index side =
      (valuesAt (trace input) index side).foldl input.config.arithmetic.add input.config.arithmetic.zero := by
  unfold native trace
  split
  next combined => rfl
  next normal =>
    rw [← ordered_values input.config.arithmetic (fun _ _ => input.config.arithmetic.zero)]
    simp only [execute_append]
    unfold ordinary
    split
    next ordinaryOn => rw [whole_loop_reference]
    next ordinaryOff => rfl

theorem output_length (input : Input Value) :
    ((List.range (input.queryEnd-input.queryStart)).map fun index =>
      Pair.mk ((native input).store index .before) ((native input).store index .after)).length =
      input.queryEnd-input.queryStart := by simp

theorem tab_bounds (first finish : Nat) (tabs : List (Tab Value))
    (lower : ∀ tab ∈ tabs, first ≤ tab.offset) :
    Bounded (finish-first) (tabEntries first finish tabs) := by
  induction tabs with
  | nil => simp [tabEntries,Bounded]
  | cons tab rest ih =>
    rw [tabEntries]
    split
    next below =>
      intro entry member
      rcases List.mem_cons.mp member with head | tail
      · subst entry
        have bound := lower tab (by simp)
        dsimp only
        omega
      · exact ih (by intro t ht; exact lower t (by simp [ht])) entry tail
    next done => simp [Bounded]

theorem justification_bounds (queryStart queryEnd arrayStart : Nat) (spacings : List (Pair Value)) :
    Bounded (queryEnd-queryStart) (justificationEntries queryStart queryEnd arrayStart spacings) := by
  intro entry member
  simp only [justificationEntries,List.mem_flatMap] at member
  obtain ⟨index,indexMem,writeMem⟩ := member
  have indexBound := List.mem_range'.mp indexMem
  split at writeMem
  next found spacing equal =>
    simp only [List.mem_cons,List.not_mem_nil,or_false] at writeMem
    rcases writeMem with same | same <;> subst entry <;> dsimp only <;> omega
  next absent => simp at writeMem

theorem selected_justification_exists (queryStart queryEnd arrayStart index : Nat)
    (spacings : List (Pair Value)) (arrayBefore : arrayStart ≤ queryStart)
    (selected : index ∈ List.range' queryStart (min queryEnd (arrayStart+spacings.length)-queryStart)) :
    ∃ spacing, spacings[index-arrayStart]? = some spacing := by
  have bounds := List.mem_range'.mp selected
  have inside : index-arrayStart < spacings.length := by omega
  exact ⟨spacings[index-arrayStart],List.getElem?_eq_getElem inside⟩

theorem full_trace_bounds (input : Input Value)
    (unitBounds : ∀ unit ∈ input.units, unit.index < input.queryEnd-input.queryStart ∧
      unit.wordTarget < input.queryEnd-input.queryStart)
    (tabBounds : Bounded (input.queryEnd-input.queryStart) (tabWrites input)) :
    Bounded (input.queryEnd-input.queryStart) (trace input) := by
  unfold trace
  split
  next combined => simp [Bounded]
  next normal =>
    rw [bounded_append,bounded_append]
    refine ⟨⟨?_,tabBounds⟩,justification_bounds _ _ _ _⟩
    split
    next enabled => exact trace_bounds _ _ _ _ unitBounds
    next disabled => simp [Bounded]

theorem combined_zero (input : Input Value) (combined : input.textCombined = true) :
    (native input).present = false ∧ (∀ index side, (native input).store index side = input.config.arithmetic.zero) := by
  simp [native,combined]

def orderWitness : List (Write (List Nat)) := [⟨0,.after,[1]⟩,⟨0,.after,[2]⟩,⟨0,.after,[3]⟩]

theorem addition_order_retained :
    execute ⟨[],List.append⟩ (fun _ _ => []) orderWitness 0 .after = [1,2,3] ∧
    execute ⟨[],List.append⟩ (fun _ _ => []) orderWitness.reverse 0 .after = [3,2,1] := by decide

end HyphenSpacingPhases
