import Boundaries
open TypeInvalidation
namespace IndependentMutation

def rootOnly (e : Environment) (s : State) (visited : List Subject) : State :=
  { s with
    cache := fun subject => if s.pending ∧ subject ∈ visited ∧ subject = .root
      then expected e s subject else s.cache subject
    pending := s.pending && !covered e visited }

theorem rootOnly_wrong :
    (rootOnly fixture addAlpha fixture.subjects).cache (.descendant 0) = 17 ∧
    expected fixture (rootOnly fixture addAlpha fixture.subjects) (.descendant 0) = 43 ∧
    (rootOnly fixture addAlpha fixture.subjects).pending = false := by decide +kernel

theorem rootOnly_incoherent : ¬ Coherent fixture (rootOnly fixture addAlpha fixture.subjects) := by
  intro h
  have bad := h (by decide) (.descendant 0) (by simp [fixture])
  obtain ⟨a,b,c⟩ := rootOnly_wrong
  simp only [a,b,c] at bad
  cases bad <;> contradiction

#print axioms IndependentMutation.rootOnly_wrong
#print axioms IndependentMutation.rootOnly_incoherent
end IndependentMutation
