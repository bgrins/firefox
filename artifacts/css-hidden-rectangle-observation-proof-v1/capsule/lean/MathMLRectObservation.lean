import CssSemantics.ProviderObservation
import Subtree

namespace MathMLRectObservation
open CssSemantics.ProviderObservation

structure Rect where
  x : Int
  y : Int
  width : Int
  height : Int
  deriving DecidableEq, Repr

def horizontalSize (rect : Rect) : Hidden.Size := ⟨rect.width, rect.height⟩

inductive Target where
  | leaf
  | unrelated
  deriving DecidableEq, Repr

structure World where
  localRect : Rect
  ancestorX : Int
  ancestorY : Int
  eligible : Bool
  hiddenAncestor : Bool
  live : Bool
  deriving DecidableEq, Repr

def observe (world : World) (target : Target) : Option Rect :=
  if world.live && decide (target = .leaf) then
    some {world.localRect with x := world.ancestorX + world.localRect.x,
                               y := world.ancestorY + world.localRect.y}
  else none

def admitted (world : World) (target : Target) : Bool :=
  world.live && decide (target = .leaf) && world.eligible && world.hiddenAncestor

def stale : World := ⟨⟨0, 0, 40, 16⟩, 70, 25, false, true, true⟩
def reference : World := {stale with ancestorX := 30, ancestorY := 10}
def observedTree : Subtree.Tree :=
  .node 1 false false false [.node 2 false false false []]
def marked : World :=
  {stale with eligible := Subtree.eligibleAt [0] (Subtree.markRoot observedTree)}

theorem marked_eq : marked = {stale with eligible := true} := by
  unfold marked
  rw [Subtree.clear_root_path_marks [0] observedTree
    (by simp [Subtree.clearRootPath, Subtree.clearPath, observedTree])]

def wholeProvider (world : World) (_ : Target) : Option World :=
  some {world with ancestorX := 30, ancestorY := 10, eligible := false}

def sizeOnlyProvider (world : World) (_ : Target) : Option World :=
  let leafRect := world.localRect
  let resized := {leafRect with width := 40, height := 16}
  some {world with localRect := resized, eligible := false}

def deleteProvider (world : World) (_ : Target) : Option World :=
  some {world with live := false, eligible := false}

def observeBefore (world : World) (target : Target) : Option (World × Rect) := do
  let value ← observe world target
  let after ← if admitted world target then wholeProvider world target else some world
  pure (after, value)

def unchanged (world : World) (_ : Unit) : Option World := some world
def firstRepeat : List (Event Unit Target) := [.query .leaf, .query .leaf]
def initial : Session World Target Rect := ⟨marked, []⟩
def actualRect : Rect := ⟨70, 25, 40, 16⟩
def expectedRect : Rect := ⟨30, 10, 40, 16⟩

theorem equal_sizes_different_positions :
    observe stale .leaf = some actualRect ∧
    observe reference .leaf = some expectedRect ∧
    horizontalSize actualRect = horizontalSize expectedRect ∧
    actualRect ≠ expectedRect := by decide

theorem whole_provider_first_repeat :
    admitted marked .leaf = true ∧
    CssSemantics.TransitionMachine.run (advance unchanged admitted wholeProvider observe)
      initial firstRepeat = some ⟨reference, [(.leaf, expectedRect), (.leaf, expectedRect)]⟩ := by
  simp only [initial, marked_eq]
  decide

theorem size_only_clears_readiness_but_keeps_wrong_position :
    CssSemantics.TransitionMachine.run (advance unchanged admitted sizeOnlyProvider observe)
      initial firstRepeat = some ⟨stale, [(.leaf, actualRect), (.leaf, actualRect)]⟩ := by
  simp only [initial, marked_eq]
  decide

theorem pre_force_read_has_updated_world_but_old_observation :
    observeBefore marked .leaf = some (reference, actualRect) := by
  simp only [marked_eq]
  decide

theorem deleted_target_has_no_successful_history :
    query admitted deleteProvider observe marked .leaf = none ∧
    CssSemantics.TransitionMachine.run (advance unchanged admitted deleteProvider observe)
      initial [.query .leaf, .mutate ()] = none := by
  simp only [initial, marked_eq]
  decide

end MathMLRectObservation
