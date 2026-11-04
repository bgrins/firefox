import RawCounterexample
namespace ShadowOrder

def repairedAllows (cut candidate : Priority) (kind : RevertKind) : Bool :=
 if kind == .layer && cut.important && cut.layer == 65535 && candidate.origin == 3 then
   candidate.layer != 65535
 else nativeAllows cut candidate kind

def repairedAccepted (state : OneState) (d : EvaluatedDeclaration) : Bool :=
 !state.seen && d.included &&
 (state.cutoff.map fun c => repairedAllows c.1 d.priority c.2).getD true

def repairedActionStep (state : OneState) (d : EvaluatedDeclaration) : OneState :=
 match d.action with
 | .revertRule => state
 | action => actionStep state {d with action := action}

def repairedDeclarationStep (state : OneState) (d : EvaluatedDeclaration) : OneState :=
 if repairedAccepted state d then repairedActionStep state d else state

theorem repaired_rule_preserves_cutoff (state : OneState) (d : EvaluatedDeclaration)
 (h : d.action = .revertRule) :
 (repairedDeclarationStep state d).cutoff = state.cutoff := by
 simp [repairedDeclarationStep,repairedActionStep,h]

theorem repaired_allows_self (p : Priority) :
 repairedAllows p p .origin = false ∧ repairedAllows p p .layer = false := by
 simp [repairedAllows,nativeAllows]
 intro _ h _
 exact h

theorem repaired_step_idempotent (state : OneState) (d : EvaluatedDeclaration) :
 repairedDeclarationStep (repairedDeclarationStep state d) d = repairedDeclarationStep state d := by
 by_cases h : repairedAccepted state d = true
 · simp only [repairedDeclarationStep,h,↓reduceIte]
   cases ha : d.action <;>
     simp [repairedActionStep,actionStep,ha,repairedAccepted,repaired_allows_self]
 · simp [repairedDeclarationStep,h]

def repairedWitnessResult (raw : RawInput) : Option Action :=
 (runActions repairedDeclarationStep (witnessNativeTrace raw) ⟨false,none,none⟩).selected

theorem corrected_raw_witness_family (outer intervening animated : Bool) :
 repairedWitnessResult (rawWitness outer intervening animated) =
 witnessReferenceResult (rawWitness outer intervening animated) := by
 cases outer <;> cases intervening <;> cases animated <;> decide

#print axioms repaired_rule_preserves_cutoff
#print axioms repaired_step_idempotent
#print axioms corrected_raw_witness_family
end ShadowOrder
