import Accounting

namespace DrainProgressContract
open AnimationObligations

def key (generation : Nat) : Key := { animationKey with generation := generation }

def sameNativeIdentity (a b : Key) : Prop :=
  a.lifetime = b.lifetime ∧ a.pseudoType = b.pseudoType ∧
  a.pseudoArgument = b.pseudoArgument ∧ a.level = b.level

instance (a b : Key) : Decidable (sameNativeIdentity a b) :=
  inferInstanceAs (Decidable (a.lifetime = b.lifetime ∧ a.pseudoType = b.pseudoType ∧
    a.pseudoArgument = b.pseudoArgument ∧ a.level = b.level))

def completedKeys (count : Nat) : Bits := fun k =>
  decide (sameNativeIdentity k animationKey ∧ k.generation < count)

def completed (count : Nat) : State :=
  ⟨completedKeys count, AnimationObligations.none, AnimationObligations.none, AnimationObligations.none, completedKeys count, AnimationObligations.none⟩

def round (s : State) (k : Key) : State :=
  install (beginTraversal (select (request s k) all) all) all

theorem key_identity (a b : Nat) : sameNativeIdentity (key a) (key b) := by
  simp [sameNativeIdentity, key]

theorem key_generation (n : Nat) : (key n).generation = n := rfl

theorem key_injective {a b : Nat} (h : key a = key b) : a = b := by
  exact congrArg Key.generation h

theorem completedKeys_next (n : Nat) (k : Key) :
    completedKeys (n + 1) k = (k == key n || completedKeys n k) := by
  apply Bool.eq_iff_iff.mpr
  simp only [Bool.or_eq_true, beq_iff_eq]
  cases k with
  | mk lifetime pseudoType pseudoArgument level generation =>
    cases level <;>
      simp [completedKeys, sameNativeIdentity, key, animationKey, Key.mk.injEq] <;>
      omega

theorem completed_conserved (n : Nat) : Conserved (completed n) := by
  intro k required
  simpa [covered, completed, AnimationObligations.none] using required

theorem completed_ready (n : Nat) : Ready (completed n) := by
  intro k required
  simpa [settled, completed, AnimationObligations.none] using required

theorem completed_drained (n : Nat) (k : Key) :
    (completed n).queued k = false ∧ (completed n).hinted k = false ∧
    (completed n).flight k = false := by
  simp [completed, AnimationObligations.none]

theorem next_is_fresh (n : Nat) : Fresh (completed n) (key n) := by
  simp [Fresh, completed, completedKeys, key, sameNativeIdentity, animationKey, AnimationObligations.none]

theorem completed_round (n : Nat) : round (completed n) (key n) = completed (n + 1) := by
  simp only [round, completed, request, select, beginTraversal, install]
  congr 1 <;>
    funext k <;>
    simp [all, AnimationObligations.none, completedKeys_next, Bool.or_comm]

theorem round_history (n : Nat) : History (completed n) (completed (n + 1)) := by
  have requestStep := Step.request (completed n) (key n) (next_is_fresh n)
  have selected := Step.select (request (completed n) (key n)) all
  have begun := Step.beginTraversal (select (request (completed n) (key n)) all) all
  have installed := Step.install (beginTraversal (select (request (completed n) (key n)) all) all) all
  have history := History.tail (History.tail (History.tail (History.tail
    (History.refl (completed n)) requestStep) selected) begun) installed
  change History (completed n) (round (completed n) (key n)) at history
  simpa only [completed_round] using history

theorem no_round_rank (rank : State → Nat)
    (decreasing : ∀ n, rank (completed (n + 1)) < rank (completed n)) : False := by
  have bound : ∀ n, rank (completed n) + n ≤ rank (completed 0) := by
    intro n
    induction n with
    | zero => omega
    | succ n ih => have := decreasing n; omega
  have := bound (rank (completed 0) + 1)
  omega

theorem repeated_ready_renewal (n : Nat) :
    Conserved (completed n) ∧ Ready (completed n) ∧
    Fresh (completed n) (key n) ∧
    History (completed n) (completed (n + 1)) :=
  ⟨completed_conserved n, completed_ready n, next_is_fresh n, round_history n⟩

theorem same_rank_renewal (rank : Key → Nat)
    (identity_only : ∀ a b, sameNativeIdentity a b → rank a = rank b) (n : Nat) :
    rank (key (n + 1)) = rank (key n) :=
  identity_only _ _ (key_identity _ _)

theorem one_round_installs : (round (completed 0) (key 0)).installed (key 0) = true := by
  decide

theorem next_generation_unsettled :
    settled (request (completed 1) (key 1)) (key 1) = false := by decide

end DrainProgressContract
