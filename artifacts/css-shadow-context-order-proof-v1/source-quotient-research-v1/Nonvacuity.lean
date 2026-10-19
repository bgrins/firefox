import TwoPhaseQuotient
namespace ShadowOrder

def witnessKey (occurrence : Nat) := occurrence / 2

def witnessImportant (key : Nat) : List (AliasDecision Nat) :=
 if key = 0 then [.rule] else []

def witnessNormal (key : Nat) : List (AliasDecision Nat) :=
 if key = 0 then [.effect 5,.effect 13] else [.effect 37]

def witnessEligible (state : Option Nat) (_ : Nat) := state.isNone

def witnessApply (_ : Option Nat) (_ : Nat) (value : Nat) := some value

theorem nonvacuous_mixed_two_phase_admission :
 (∀ state key value, witnessEligible (witnessApply state key value) key = false) ∧
 (∀ state key value other, witnessEligible state other = false →
   witnessEligible (witnessApply state key value) other = false) ∧
 (∀ occurrence ∈ ([0,1,2] : List Nat),
   AliasDecision.rule ∈ witnessImportant (witnessKey occurrence) →
   occurrence ∈ ([0,1] : List Nat)) := by
 refine ⟨by intros; rfl,by intros; rfl,?_⟩
 intro occurrence member rule
 simp only [List.mem_cons,List.not_mem_nil,or_false] at member
 rcases member with rfl | rfl | rfl
 · simp
 · simp
 · simp [witnessImportant,witnessKey] at rule

theorem nonvacuous_important_rule_blocks_mixed_normal_aliases :
 twoPhaseExecution witnessKey witnessImportant witnessNormal witnessEligible witnessApply
   [0,1] [0,1,2] none = some 37 ∧
 twoPhaseExecution (fun x => x) witnessImportant witnessNormal witnessEligible witnessApply
   [0,0] [0,0,1] none = some 37 := by
 decide

#print axioms nonvacuous_mixed_two_phase_admission
#print axioms nonvacuous_important_rule_blocks_mixed_normal_aliases
end ShadowOrder
