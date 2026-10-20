import Std
namespace CaptionCache

structure Size where
  inlineSize : Int
  blockSize : Int
  deriving DecidableEq, Repr

structure Input (P : Type) where
  prior : P
  containingBlock : Size
  deriving DecidableEq, Repr

def original [DecidableEq P] (a b : Input P) : Bool := decide (a.prior = b.prior)
def candidate [DecidableEq P] (a b : Input P) : Bool :=
  decide ((a.prior, a.containingBlock) = (b.prior, b.containingBlock))

def IndependentInputsAgree (a b : Input P) : Prop :=
  a.prior = b.prior ∧
  a.containingBlock.inlineSize = b.containingBlock.inlineSize ∧
  a.containingBlock.blockSize = b.containingBlock.blockSize

theorem candidate_iff_independent_components [DecidableEq P] (a b : Input P) :
    candidate a b = true ↔ IndependentInputsAgree a b := by
  rcases a with ⟨p,ai,ab⟩
  rcases b with ⟨q,bi,bb⟩
  simp [candidate,IndependentInputsAgree,Size.mk.injEq]

theorem candidate_conjoins_prior_and_basis [DecidableEq P] (a b : Input P) :
    candidate a b = (original a b && decide (a.containingBlock = b.containingBlock)) := by
  simp [candidate,original]

theorem same_basis_preserves_prior_decision [DecidableEq P] (a b : Input P)
    (same : a.containingBlock = b.containingBlock) : candidate a b = original a b := by
  simp [candidate_conjoins_prior_and_basis,same]

theorem prior_rejection_preserved [DecidableEq P] (a b : Input P)
    (reject : original a b = false) : candidate a b = false := by
  simp [candidate_conjoins_prior_and_basis,reject]

theorem changed_basis_rejected [DecidableEq P] (a b : Input P)
    (changed : a.containingBlock ≠ b.containingBlock) : candidate a b = false := by
  simp [candidate_conjoins_prior_and_basis,changed]

def reuse (present dirty accepted : Bool) : Bool := present && !dirty && accepted

theorem reuse_derives_inputs [DecidableEq P] (present dirty : Bool) (a b : Input P)
    (used : reuse present dirty (candidate a b) = true) :
    present = true ∧ dirty = false ∧ IndependentInputsAgree a b := by
  simp only [reuse,Bool.and_eq_true,Bool.not_eq_true'] at used
  exact ⟨used.1.1,used.1.2,(candidate_iff_independent_components a b).1 used.2⟩

end CaptionCache
