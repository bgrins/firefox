import Std
namespace KeyframePriority

structure Property where
  shorthand : Bool
  logical : Bool
  components : Nat
  idl : Nat
  deriving DecidableEq

def category (a : Property) : Nat :=
  if a.shorthand then 2 else if a.logical then 1 else 0

def nativeLE (a b : Property) : Prop :=
  category a < category b ∨ category a = category b ∧
    (a.shorthand = false ∨
      a.components < b.components ∨ a.components = b.components ∧
        (a.logical = false ∧ b.logical = true ∨ a.logical = b.logical ∧ a.idl ≤ b.idl))

def specLE (a b : Property) : Prop :=
  (a.shorthand = false ∧ b.shorthand = true) ∨
  a.shorthand = b.shorthand ∧
    ((a.shorthand = true ∧ a.components < b.components) ∨
      (a.shorthand = false ∨ a.components = b.components) ∧
        ((a.logical = false ∧ b.logical = true) ∨
          a.logical = b.logical ∧ (a.shorthand = false ∨ a.idl ≤ b.idl)))

instance (a b : Property) : Decidable (nativeLE a b) := inferInstanceAs (Decidable (_ ∨ _))
instance (a b : Property) : Decidable (specLE a b) := inferInstanceAs (Decidable (_ ∨ _))

theorem priority_refinement (a b : Property) : nativeLE a b ↔ specLE a b := by
  cases a with | mk ash al ac ai =>
    cases b with | mk bsh bl bc bi =>
      cases ash <;> cases al <;> cases bsh <;> cases bl <;>
        simp [nativeLE, specLE, category] <;> omega

theorem priority_reflexive (a : Property) : nativeLE a a := by
  simp [nativeLE]

theorem priority_total (a b : Property) : nativeLE a b ∨ nativeLE b a := by
  cases a with | mk ash al ac ai =>
    cases b with | mk bsh bl bc bi =>
      cases ash <;> cases al <;> cases bsh <;> cases bl <;>
        simp [nativeLE, category] <;> omega

theorem priority_transitive (a b c : Property)
    (hab : nativeLE a b) (hbc : nativeLE b c) : nativeLE a c := by
  cases a with | mk ash al ac ai =>
    cases b with | mk bsh bl bc bi =>
      cases c with | mk csh cl cc ci =>
        cases ash <;> cases al <;> cases bsh <;> cases bl <;>
          cases csh <;> cases cl <;>
            simp [nativeLE, category] at * <;> omega

theorem uniform_filter (xs : List α) (isLogical : α → Bool) (logical : Bool)
    (uniform : ∀ x ∈ xs, isLogical x = logical) (keep : α → Bool)
    (nonempty : xs.filter keep ≠ []) :
    (xs.filter keep).all isLogical = logical := by
  cases logical with
  | true =>
    apply List.all_eq_true.mpr
    intro x hx
    exact uniform x (List.mem_filter.mp hx).1
  | false =>
    cases h : xs.filter keep with
    | nil => exact False.elim (nonempty h)
    | cons x tail =>
      have hx : x ∈ xs.filter keep := by simp [h]
      have hf := uniform x (List.mem_filter.mp hx).1
      simp [hf]

theorem count_precedes_mapping (a b : Property)
    (ha : a.shorthand = true) (hb : b.shorthand = true)
    (hc : a.components < b.components) : specLE a b := by
  simp [specLE, ha, hb, hc]

theorem physical_precedes_logical (a b : Property)
    (ha : a.shorthand = b.shorthand) (hc : a.components = b.components)
    (hp : a.logical = false) (hl : b.logical = true) : specLE a b := by
  simp [specLE, ha, hc, hp, hl]

structure Declaration (V : Type) where
  property : Property
  targets : List Nat
  value : V

def firstMatch (target : Nat) : List (Declaration V) → Option (Declaration V)
  | [] => none
  | d :: ds => if target ∈ d.targets then some d else firstMatch target ds

def Wins (target : Nat) (ds : List (Declaration V)) (d : Declaration V) : Prop :=
  d ∈ ds ∧ target ∈ d.targets ∧
  ∀ e ∈ ds, target ∈ e.targets → specLE d.property e.property

theorem first_member (target : Nat) (ds : List (Declaration V)) (d : Declaration V)
    (h : firstMatch target ds = some d) : d ∈ ds ∧ target ∈ d.targets := by
  induction ds with
  | nil => simp [firstMatch] at h
  | cons x xs ih =>
    by_cases hx : target ∈ x.targets
    · simp [firstMatch, hx] at h
      subst d
      simp [hx]
    · simp [firstMatch, hx] at h
      exact ⟨List.mem_cons_of_mem x (ih h).1, (ih h).2⟩

theorem first_none (target : Nat) (ds : List (Declaration V)) :
    firstMatch target ds = none ↔ ∀ d ∈ ds, target ∉ d.targets := by
  induction ds with
  | nil => simp [firstMatch]
  | cons x xs ih =>
    by_cases hx : target ∈ x.targets <;> simp [firstMatch, hx, ih]

theorem sorted_first_wins (target : Nat) (ds : List (Declaration V))
    (sorted : ds.Pairwise (fun a b => nativeLE a.property b.property))
    (d : Declaration V) (h : firstMatch target ds = some d) : Wins target ds d := by
  induction ds with
  | nil => simp [firstMatch] at h
  | cons x xs ih =>
    obtain ⟨hx, hs⟩ := List.pairwise_cons.mp sorted
    by_cases hit : target ∈ x.targets
    · simp [firstMatch, hit] at h
      subst d
      refine ⟨by simp, hit, ?_⟩
      intro e he _
      rcases List.mem_cons.mp he with rfl | he
      · exact (priority_refinement e.property e.property).mp (priority_reflexive _)
      · exact (priority_refinement x.property e.property).mp (hx e he)
    · simp [firstMatch, hit] at h
      obtain ⟨hd, ht, hw⟩ := ih hs h
      refine ⟨List.mem_cons_of_mem x hd, ht, ?_⟩
      intro e he et
      rcases List.mem_cons.mp he with rfl | he
      · exact False.elim (hit et)
      · exact hw e he et

theorem permutation_refinement (target : Nat)
    (original ordered : List (Declaration V)) (permutation : original.Perm ordered)
    (sorted : ordered.Pairwise (fun a b => nativeLE a.property b.property))
    (d : Declaration V) (h : firstMatch target ordered = some d) : Wins target original d := by
  obtain ⟨hd, ht, hw⟩ := sorted_first_wins target ordered sorted d h
  refine ⟨permutation.mem_iff.mpr hd, ht, ?_⟩
  intro e he et
  exact hw e (permutation.mem_iff.mp he) et

theorem value_refinement (target : Nat)
    (original ordered : List (Declaration V)) (permutation : original.Perm ordered)
    (sorted : ordered.Pairwise (fun a b => nativeLE a.property b.property))
    (d winner : Declaration V) (h : firstMatch target ordered = some d)
    (unique : ∀ e, Wins target original e → e.value = winner.value) :
    d.value = winner.value := by
  exact unique d (permutation_refinement target original ordered permutation sorted d h)

def physical : Property := ⟨true, false, 3, 7⟩
def logical : Property := ⟨true, true, 3, 2⟩
def oldLE (a b : Property) : Prop :=
  category a < category b ∨ category a = category b ∧
    (a.shorthand = false ∨ a.components < b.components ∨
      a.components = b.components ∧ a.idl ≤ b.idl)

instance (a b : Property) : Decidable (oldLE a b) := inferInstanceAs (Decidable (_ ∨ _))

theorem old_counterexample : oldLE logical physical ∧ ¬ specLE logical physical := by
  decide

theorem fixed_counterexample : specLE physical logical ∧ ¬ specLE logical physical := by
  decide

#print axioms priority_refinement
#print axioms priority_reflexive
#print axioms priority_total
#print axioms priority_transitive
#print axioms uniform_filter
#print axioms count_precedes_mapping
#print axioms physical_precedes_logical
#print axioms first_member
#print axioms first_none
#print axioms sorted_first_wins
#print axioms permutation_refinement
#print axioms value_refinement
#print axioms old_counterexample
#print axioms fixed_counterexample
end KeyframePriority
