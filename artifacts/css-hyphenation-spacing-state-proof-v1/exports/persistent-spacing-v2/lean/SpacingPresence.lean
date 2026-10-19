import SpacingAssociation

namespace SpacingPresence
open HyphenSpacingValues HyphenSpacingPhases HyphenTabValues SpacingAssociation

def noSpacing : Config Nat :=
  ⟨⟨0,Nat.add⟩,0,0,0,0,false,false,false,false,⟨fun _ => false,fun _ => true,fun _ _ => false,0⟩⟩

def input (first finish : Nat) : Input Nat :=
  ⟨noSpacing,first,finish,false,false,⟨false,none,false⟩,[],false,true,none,first,0,[]⟩

def environment : Environment Nat :=
  ⟨PersistentTabs.exampleNumeric,fun i => input i (i+1),PersistentTabs.exampleProviders,0,true,true⟩

def fresh : PropertySession.Session Nat := PropertySession.construct 3 7 0 0 none

def later : PropertySession.Session Nat := (query environment (input 0 2) fresh).1

theorem presence_depends_on_history :
    (query environment (input 0 1) fresh).2.present = false ∧
    (query environment (input 0 1) later).2.present = true := by decide +kernel

theorem zero_values_despite_presence_difference (index : Nat) (side : Side) :
    (query environment (input 0 1) fresh).2.store index side = 0 ∧
    (query environment (input 0 1) later).2.store index side = 0 := by
  have firstEmpty : (trace (applied environment (input 0 1) fresh)).length = 0 := by decide +kernel
  have laterEmpty : (trace (applied environment (input 0 1) later)).length = 0 := by decide +kernel
  constructor
  · rw [exact_ordered_values, List.length_eq_zero_iff.mp firstEmpty]
    rfl
  · rw [exact_ordered_values, List.length_eq_zero_iff.mp laterEmpty]
    rfl

def adjustedWidth (base : Nat) (spacing : Result Nat) (index : Nat) (side : Side) : Nat :=
  if spacing.present then base + spacing.store index side else base

theorem zero_width_observation (base index : Nat) (side : Side) :
    adjustedWidth base (query environment (input 0 1) fresh).2 index side =
      adjustedWidth base (query environment (input 0 1) later).2 index side := by
  have zeros := zero_values_despite_presence_difference index side
  have flags := presence_depends_on_history
  simp [adjustedWidth,flags.1,flags.2,zeros.2]

end SpacingPresence
