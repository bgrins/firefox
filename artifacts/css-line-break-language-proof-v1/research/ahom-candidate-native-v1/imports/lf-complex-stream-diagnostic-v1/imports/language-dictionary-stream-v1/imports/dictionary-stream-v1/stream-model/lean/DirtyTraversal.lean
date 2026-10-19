import Std

namespace DirtyTraversal

structure Frame where
  identity : Nat
  text : Bool
  inflated : Option Nat
  uninflated : Option Nat
  deriving DecidableEq, Repr

inductive Tree where
  | node (frame : Frame) (children : List Tree)
  deriving Repr

def preorder : Tree → List Frame
  | .node f children => f :: children.flatMap preorder

def frontier (trees : List Tree) : List Frame := trees.flatMap preorder

def nativeWalk : Nat → List Tree → List Frame
  | 0, _ => []
  | _ + 1, [] => []
  | fuel + 1, .node f children :: rest =>
      f :: nativeWalk fuel (children ++ rest)

theorem worklist_refinement (fuel : Nat) (trees : List Tree)
    (enough : (frontier trees).length ≤ fuel) : nativeWalk fuel trees = frontier trees := by
  induction fuel generalizing trees with
  | zero =>
    have h : frontier trees = [] := by
      cases hf : frontier trees with
      | nil => rfl
      | cons f rest => simp [hf] at enough
    simp [nativeWalk, h]
  | succ fuel ih =>
    cases trees with
    | nil => rfl
    | cons tree rest =>
      cases tree with
      | node f children =>
        have hl : (frontier (children ++ rest)).length ≤ fuel := by
          simp [frontier, preorder, List.flatMap_append, List.length_append] at *
          omega
        simp only [nativeWalk, ih (children ++ rest) hl]
        simp [frontier, preorder, List.flatMap_append]

theorem visits_every_descendant (trees : List Tree) (f : Frame)
    (member : f ∈ frontier trees) :
    f ∈ nativeWalk (frontier trees).length trees := by
  rw [worklist_refinement _ _ (by omega)]
  exact member

def referencedTargets (f : Frame) : List Nat :=
  if f.text then f.inflated.toList ++ f.uninflated.toList else []

def clearTargets (targets : List Nat) (f : Frame) : Frame :=
  {f with
    inflated := f.inflated.filter fun r => !(targets.contains r)
    uninflated := f.uninflated.filter fun r => !(targets.contains r)}

def dirty (visited world : List Frame) : List Frame :=
  world.map (clearTargets (visited.flatMap referencedTargets))

theorem target_clears_both_slots (targets : List Nat) (f : Frame) (target : Nat)
    (inside : target ∈ targets) :
    (clearTargets targets f).inflated ≠ some target ∧
      (clearTargets targets f).uninflated ≠ some target := by
  simp only [clearTargets]
  constructor <;> cases h : f.inflated <;> cases h' : f.uninflated <;>
    simp_all [Option.filter]
  all_goals
    intro absent equal
    apply absent
    simpa [equal] using inside

theorem native_dirty_refines (trees : List Tree) (world : List Frame) :
    dirty (nativeWalk (frontier trees).length trees) world = dirty (frontier trees) world := by
  rw [worklist_refinement _ _ (by omega)]

theorem changed_text_target_is_marked (trees : List Tree) (f : Frame) (r : Nat)
    (inside : f ∈ frontier trees) (text : f.text = true)
    (old : f.inflated = some r) :
    r ∈ (nativeWalk (frontier trees).length trees).flatMap referencedTargets := by
  apply List.mem_flatMap.mpr
  refine ⟨f, visits_every_descendant trees f inside, ?_⟩
  simp [referencedTargets, text, old]

#print axioms worklist_refinement
#print axioms visits_every_descendant
#print axioms target_clears_both_slots
#print axioms native_dirty_refines
#print axioms changed_text_target_is_marked
end DirtyTraversal
