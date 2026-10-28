import Defaults

namespace FallbackCycleWitness
open ProviderDefaults

structure ScopedState where
  names : List Nat := []
  cycle : Bool := false
  deriving DecidableEq, Repr

structure ScopedResult where
  outcome : Outcome
  state : ScopedState
  deriving DecidableEq, Repr

def environment : Environment :=
  ⟨fun n => if n = 0 then 3 else 7,
   fun n => if n = 0 then .ref 1 (.ref 2 .missing)
     else if n = 1 then .ref 0 .missing else .missing⟩

def scopedEvaluate (defaultFailures : Bool) : Nat → Expr → ScopedState → ScopedResult
  | 0, _, s => ⟨.pending, s⟩
  | fuel + 1, expr, s =>
    match expr with
    | .literal n => ⟨.value n, s⟩
    | .missing => ⟨.missing, s⟩
    | .reject => ⟨.rejected, s⟩
    | .plusOne e =>
      let r := scopedEvaluate defaultFailures fuel e s
      match r.outcome with
      | .value n => { r with outcome := .value (n + 1) }
      | _ => r
    | .ref name otherwise =>
      let primary : ScopedResult :=
        if name ∈ s.names then
          ⟨.missing, { s with cycle := true }⟩
        else
          let r := scopedEvaluate defaultFailures fuel (environment.body name)
            { names := s.names ++ [name], cycle := false }
          let output := if r.state.cycle then r.outcome else
            match r.outcome with
            | .missing | .rejected =>
              if defaultFailures then .value (environment.initial name) else r.outcome
            | _ => r.outcome
          ⟨output, { names := s.names, cycle := r.state.cycle || s.cycle }⟩
      match primary.outcome with
      | .missing => scopedEvaluate defaultFailures fuel otherwise primary.state
      | _ => primary

def consumer : Expr := .ref 0 (.literal 11)
def oldResult := scopedEvaluate false 16 consumer {}
def scopedResult := scopedEvaluate true 16 consumer {}
def participantResult := evaluate true environment 16 consumer {}

theorem baseline_consumer_fallback : oldResult.outcome = .value 11 := by decide +kernel

theorem scoped_bit_leaks_c_default :
    scopedResult.outcome = .value 7 ∧ scopedResult.state.cycle = true := by decide +kernel

theorem participant_marks_select_a_default :
    participantResult.outcome = .value 3 := by decide +kernel

theorem exact_participants_exclude_c :
    participantResult.state.poisoned = [.property 1, .property 0] := by decide +kernel

theorem scoped_bit_does_not_preserve_baseline :
    scopedResult.outcome ≠ oldResult.outcome := by decide +kernel

theorem scoped_bit_does_not_implement_participants :
    scopedResult.outcome ≠ participantResult.outcome := by decide +kernel

theorem missing_provider_alone_defaults :
    (scopedEvaluate true 16 (.ref 2 (.literal 11)) {}).outcome = .value 7 ∧
    (scopedEvaluate true 16 (.ref 2 (.literal 11)) {}).state.cycle = false := by decide +kernel

end FallbackCycleWitness
