import Rules
namespace Fragmentation

structure Decoration where
  startExtent : Nat
  endExtent : Nat
  cloned : Bool
  deriving DecidableEq, Repr
structure Input where
  types : BreakTypes
  content : List Atom
  opportunities : List Opportunity
  decorations : List Decoration := []
  capacity : Nat
  deriving DecidableEq, Repr

def decorationExtent (s : Stage) (d : Decoration) : Nat :=
  if d.cloned then match s with
    | .endClone => d.startExtent
    | .bothClone => 0
    | _ => d.startExtent + d.endExtent
  else d.startExtent + d.endExtent

def extent (s : Stage) (i : Input) (cut : Nat) : Nat :=
  ((i.content.take cut).map Atom.extent).sum + (i.decorations.map (decorationExtent s)).sum

def zeroBox (a : Atom) : Bool :=
  match a.kind with | .box _ => a.extent == 0 | _ => false

def nextZeroBox (i : Input) (cut : Nat) : Bool :=
  (i.content.drop cut).head?.any zeroBox

def finishFits (s : Stage) (i : Input) : Bool :=
  i.content.isEmpty || decide (extent s i i.content.length ≤ i.capacity)

def fits (s : Stage) (i : Input) (p : Opportunity) : Bool :=
  decide (0 < p.cut) && decide (p.cut < i.content.length) &&
  decide (extent s i p.cut ≤ i.capacity) && !nextZeroBox i p.cut

def candidate (s : Stage) (i : Input) (p : Opportunity) : Bool :=
  ordinary s i.types i.content p && fits s i p

def GridPlacement (s : Stage) (i : Input) (p : Opportunity) : Prop :=
  Ordinary s i.types i.content p ∧ 0 < p.cut ∧ p.cut < i.content.length ∧
  ((i.content.take p.cut).map Atom.extent).sum +
    (i.decorations.map (decorationExtent s)).sum ≤ i.capacity ∧
  nextZeroBox i p.cut = false

def GridFeasible (s : Stage) (i : Input) : Prop :=
  (i.content = [] ∨ extent s i i.content.length ≤ i.capacity) ∨
  ∃ p ∈ i.opportunities, GridPlacement s i p

inductive Choice where
  | finish | cut (p : Opportunity)
  deriving DecidableEq, Repr

def evaluate (s : Stage) (i : Input) : Option Choice :=
  if finishFits s i then some .finish
  else (i.opportunities.find? (candidate s i)).map Choice.cut

def ValidChoice (s : Stage) (i : Input) : Choice → Prop
  | .finish => i.content = [] ∨ extent s i i.content.length ≤ i.capacity
  | .cut p => p ∈ i.opportunities ∧ GridPlacement s i p

theorem ordinary_decorations_retained (s : Stage) (d : Decoration) (h : d.cloned = false) :
    decorationExtent s d = d.startExtent + d.endExtent := by simp [decorationExtent, h]

theorem candidate_refinement (s : Stage) (i : Input) (p : Opportunity) :
    candidate s i p = true ↔ GridPlacement s i p := by
  simp [candidate, fits, GridPlacement, ordinary_refinement, extent, and_assoc]

theorem finish_refinement (s : Stage) (i : Input) :
    finishFits s i = true ↔ i.content = [] ∨ extent s i i.content.length ≤ i.capacity := by
  simp [finishFits]

theorem grid_evaluator_iff (s : Stage) (i : Input) :
    (evaluate s i).isSome = true ↔ GridFeasible s i := by
  unfold evaluate
  split
  · rename_i h
    have hf := (finish_refinement s i).mp h
    simp [GridFeasible, hf]
  · rename_i h
    have hf : ¬ (i.content = [] ∨ extent s i i.content.length ≤ i.capacity) := by
      intro hf; exact h ((finish_refinement s i).mpr hf)
    simp [GridFeasible, hf, List.find?_isSome, candidate_refinement]

theorem selected_sound (s : Stage) (i : Input) (c : Choice)
    (h : evaluate s i = some c) : ValidChoice s i c := by
  unfold evaluate at h
  split at h
  · rename_i hf
    cases h
    exact (finish_refinement s i).mp hf
  · cases found : i.opportunities.find? (candidate s i) with
    | none => simp [found] at h
    | some p =>
      simp [found] at h
      subst c
      have hm := List.mem_of_find?_eq_some found
      have hp := List.find?_some found
      exact ⟨hm, (candidate_refinement s i p).mp hp⟩

theorem evaluator_none_iff (s : Stage) (i : Input) :
    evaluate s i = none ↔ ¬ GridFeasible s i := by
  rw [← grid_evaluator_iff]
  cases evaluate s i <;> simp

theorem selected_cut_progress (s : Stage) (i : Input) (p : Opportunity)
    (h : evaluate s i = some (.cut p)) :
    0 < p.cut ∧ (i.content.drop p.cut).length < i.content.length := by
  have hp := (selected_sound s i (.cut p) h).2
  simp only [GridPlacement] at hp
  simp only [List.length_drop]
  omega

theorem zero_box_not_left_behind (s : Stage) (i : Input) (p : Opportunity)
    (h : evaluate s i = some (.cut p)) : nextZeroBox i p.cut = false :=
  (selected_sound s i (.cut p) h).2.2.2.2.2

end Fragmentation
