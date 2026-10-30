import RelativeInfinity

namespace WinnerNaN
open RelativeInfinity

def HasNaN {α : Type} (eval : α → Value) (children : List α) : Prop :=
  ∃ leaf ∈ children, eval leaf = .nan

def Guard {α : Type} (hazard : α → Prop) (children : List α) (winner : α) : Prop :=
  ∀ leaf ∈ children, leaf ≠ winner → hazard leaf → leaf = winner

def OtherDiscardedSafe {α : Type} (eval : α → Value) (hazard : α → Prop)
    (children : List α) (winner : α) : Prop :=
  ∀ leaf ∈ children, leaf ≠ winner → ¬ hazard leaf → eval leaf ≠ .nan

theorem equal_leaf_same_context {α : Type} (eval : α → Value) (a b : α)
    (equal : a = b) : eval a = eval b := by
  exact congrArg eval equal

theorem discarded_nan_implies_winner_nan {α : Type} (eval : α → Value)
    (hazard : α → Prop) (children : List α) (winner : α)
    (guard : Guard hazard children winner)
    (safe : OtherDiscardedSafe eval hazard children winner)
    (present : HasNaN eval children) : eval winner = .nan := by
  classical
  obtain ⟨leaf, member, nan⟩ := present
  by_cases equal : leaf = winner
  · simpa [equal] using nan
  by_cases dangerous : hazard leaf
  · exact False.elim (equal (guard leaf member equal dangerous))
  · exact False.elim (safe leaf member equal dangerous nan)

theorem member_winner_nan_implies_child_nan {α : Type} (eval : α → Value)
    (children : List α) (winner : α) (member : winner ∈ children)
    (nan : eval winner = .nan) : HasNaN eval children := by
  exact ⟨winner, member, nan⟩

theorem guarded_nan_equivalence {α : Type} (eval : α → Value)
    (hazard : α → Prop) (children : List α) (winner : α)
    (member : winner ∈ children) (guard : Guard hazard children winner)
    (safe : OtherDiscardedSafe eval hazard children winner) :
    HasNaN eval children ↔ eval winner = .nan := by
  exact ⟨discarded_nan_implies_winner_nan eval hazard children winner guard safe,
    member_winner_nan_implies_child_nan eval children winner member⟩

def identity : Op → Value
  | .min => .posInf
  | .max => .negInf

def aggregate {α : Type} (op : Op) (eval : α → Value) : List α → Value
  | [] => identity op
  | leaf :: rest => semantic op (eval leaf) (aggregate op eval rest)

theorem binary_nan_iff (op : Op) (a b : Value) :
    semantic op a b = .nan ↔ a = .nan ∨ b = .nan := by
  cases op <;> cases a <;> cases b <;> simp [semantic, minimum, maximum]

theorem aggregate_nan_iff {α : Type} (op : Op) (eval : α → Value)
    (children : List α) : aggregate op eval children = .nan ↔ HasNaN eval children := by
  induction children with
  | nil => cases op <;> simp [aggregate, identity, HasNaN]
  | cons leaf rest ih =>
    simp only [aggregate, binary_nan_iff, ih]
    simp [HasNaN]

theorem guarded_nary_nan_preserved {α : Type} (op : Op) (eval : α → Value)
    (hazard : α → Prop) (children : List α) (winner : α)
    (member : winner ∈ children) (guard : Guard hazard children winner)
    (safe : OtherDiscardedSafe eval hazard children winner) :
    aggregate op eval children = .nan ↔ eval winner = .nan := by
  exact (aggregate_nan_iff op eval children).trans
    (guarded_nan_equivalence eval hazard children winner member guard safe)

theorem singleton_nan_preserved {α : Type} (op : Op) (eval : α → Value) (leaf : α) :
    aggregate op eval [leaf] = .nan ↔ eval leaf = .nan := by
  rw [aggregate_nan_iff]
  simp [HasNaN]

theorem duplicate_list_nan_preserved {α : Type} (op : Op) (eval : α → Value)
    (children : List α) (winner : α) (member : winner ∈ children)
    (duplicates : ∀ leaf ∈ children, leaf = winner) :
    aggregate op eval children = .nan ↔ eval winner = .nan := by
  rw [aggregate_nan_iff]
  constructor
  · rintro ⟨leaf, contains, nan⟩
    simpa [duplicates leaf contains] using nan
  · exact member_winner_nan_implies_child_nan eval children winner member

structure Leaf where
  unit : Nat
  coefficient : Value
  deriving DecidableEq, Repr

def evaluate (context : Nat → Basis) (leaf : Leaf) : Value :=
  scale (context leaf.unit) leaf.coefficient

def relativeInfinity (leaf : Leaf) : Prop := isInfinite leaf.coefficient = true

theorem finite_or_nan_exclusion (context : Nat → Basis) (leaf : Leaf)
    (noExplicitNaN : leaf.coefficient ≠ .nan) (noInfinity : ¬ relativeInfinity leaf) :
    evaluate context leaf ≠ .nan := by
  rcases leaf with ⟨unit, coefficient⟩
  cases coefficient <;> cases basis : context unit <;>
    simp_all [evaluate, scale, relativeInfinity, isInfinite]

theorem contextual_guard_sufficient (op : Op) (context : Nat → Basis)
    (children : List Leaf) (winner : Leaf) (member : winner ∈ children)
    (guard : Guard relativeInfinity children winner)
    (noExplicitNaN : ∀ leaf ∈ children, leaf.coefficient ≠ .nan) :
    aggregate op (evaluate context) children = .nan ↔ evaluate context winner = .nan := by
  apply guarded_nary_nan_preserved op (evaluate context) relativeInfinity children winner member guard
  intro leaf contains different noInfinity
  exact finite_or_nan_exclusion context leaf (noExplicitNaN leaf contains) noInfinity

theorem contextual_mutation_nan_preserved (op : Op) (before after : Nat → Basis)
    (children : List Leaf) (winner : Leaf) (member : winner ∈ children)
    (guard : Guard relativeInfinity children winner)
    (noExplicitNaN : ∀ leaf ∈ children, leaf.coefficient ≠ .nan) :
    (aggregate op (evaluate before) children = .nan ↔ evaluate before winner = .nan) ∧
    (aggregate op (evaluate after) children = .nan ↔ evaluate after winner = .nan) := by
  exact ⟨contextual_guard_sufficient op before children winner member guard noExplicitNaN,
    contextual_guard_sufficient op after children winner member guard noExplicitNaN⟩

def splitContext (unit : Nat) : Basis := if unit = 0 then .zero else .positive 0

def retainedFinite : Leaf := ⟨1, .finite (-1)⟩
def discardedInfinity : Leaf := ⟨0, .posInf⟩
def retainedOtherUnitInfinity : Leaf := ⟨1, .posInf⟩
def discardedExplicitNaN : Leaf := ⟨1, .nan⟩

theorem equal_coefficients_do_not_determine_resolution :
    discardedInfinity.coefficient = retainedOtherUnitInfinity.coefficient ∧
    evaluate splitContext discardedInfinity ≠ evaluate splitContext retainedOtherUnitInfinity := by
  decide

end WinnerNaN
