import SkipRunTraversal

namespace HyphenationProviderWrites

open HyphenSkipRanges HyphenSkipRunTraversal

inductive Kind where
  | none | soft | explicit | automatic
  deriving DecidableEq, Repr

structure Inputs where
  softAtOriginal : Nat → Bool
  explicitAtTransformed : Nat → Bool
  automaticBefore : Nat → Bool
  startOfLine : Bool
  providerStart : Nat
  automatic : Bool

def softWrites (inputs : Inputs) (allowSoft : Bool) : List Run → List (Nat × Kind)
  | [] => []
  | run::rest =>
    if run.skipped then
      softWrites inputs (inputs.softAtOriginal (run.original+run.length-1)) rest
    else
      ((List.range' run.transformed run.length).map fun position =>
        (position,if position = run.transformed ∧ allowSoft ∧
          (!inputs.startOfLine || decide (run.transformed > inputs.providerStart)) then .soft else .none)) ++
        softWrites inputs false rest

theorem soft_write_coordinates (inputs : Inputs) (allowSoft : Bool) (runs : List Run) :
    (softWrites inputs allowSoft runs).map Prod.fst = runs.flatMap contribution := by
  induction runs generalizing allowSoft with
  | nil => rfl
  | cons run rest ih =>
    simp only [softWrites,List.flatMap_cons,contribution]
    split
    next skipped => simpa using ih (inputs.softAtOriginal (run.original+run.length-1))
    next kept => simp [List.map_append,List.map_map,Function.comp_def,ih]

theorem full_soft_initialization (inputs : Inputs) (allowSoft : Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    (softWrites inputs allowSoft (traverse ranges count valid offset remaining)).map Prod.fst =
      List.range' (lookupOriginal ranges offset) remaining := by
  rw [soft_write_coordinates,initialized_coordinates ranges count valid offset remaining bounded available]

theorem full_soft_length (inputs : Inputs) (allowSoft : Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    (softWrites inputs allowSoft (traverse ranges count valid offset remaining)).length = remaining := by
  have coordinates := congrArg List.length
    (full_soft_initialization inputs allowSoft ranges count valid offset remaining bounded available)
  simpa using coordinates

def autoLoop (inputs : Inputs) (start : Nat) (index : Nat) (values : List Kind) : List Kind :=
  if active : index < values.length then
    if inputs.explicitAtTransformed (start+index) then
      let next := if index+1 < values.length then values.set (index+1) .explicit else values
      autoLoop inputs start (index+1) next
    else
      let next := if inputs.automaticBefore (start+index) && decide (values[index]?.getD .none = .none)
        then values.set index .automatic else values
      autoLoop inputs start (index+1) next
  else values
termination_by values.length-index
decreasing_by all_goals split <;> simp_all <;> omega

theorem auto_length (inputs : Inputs) (start index : Nat) (values : List Kind) :
    (autoLoop inputs start index values).length = values.length := by
  rw [autoLoop]
  split
  next active =>
    split
    next explicit =>
      rw [auto_length]
      split <;> simp
    next ordinary =>
      rw [auto_length]
      split <;> simp
  next finished => rfl
termination_by values.length-index
decreasing_by all_goals split <;> simp_all <;> omega

def provide (inputs : Inputs) (wrap enabled allowSoft : Bool)
    (queryLength queryStart : Nat) (runs : List Run) : List Kind :=
  if !wrap || !enabled then List.replicate queryLength .none
  else
    let initial := (softWrites inputs allowSoft runs).map Prod.snd
    if inputs.automatic then autoLoop inputs queryStart 0 initial else initial

theorem full_provider_length (inputs : Inputs) (wrap enabled allowSoft : Bool)
    (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    (provide inputs wrap enabled allowSoft remaining (lookupOriginal ranges offset)
      (traverse ranges count valid offset remaining)).length = remaining := by
  unfold provide
  split
  next disabled => simp
  next enabled =>
    split
    next automatic =>
      rw [auto_length,List.length_map]
      exact full_soft_length inputs allowSoft ranges count valid offset remaining bounded available
    next manual =>
      rw [List.length_map]
      exact full_soft_length inputs allowSoft ranges count valid offset remaining bounded available

end HyphenationProviderWrites
