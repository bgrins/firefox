import Counters

namespace CounterDelivery.Examples

open CounterDelivery

def initial : Table := fun name =>
  if name = 0 then [([], [⟨10, 1⟩])] else [([], [⟨90, 7⟩])]

def mark : Name → Bool := fun name => name == 0

def appended (change : Change) : Edit :=
  ⟨0, [], ⟨some 0, .use⟩, ⟨some 0, change⟩⟩

def children : List Edit :=
  [⟨0, [0], ⟨some 0, .use⟩, ⟨some 1, .use⟩⟩,
   ⟨0, [0, 0, 0], ⟨some 1, .use⟩, ⟨some 2, .use⟩⟩,
   ⟨1, [1], ⟨some 0, .use⟩, ⟨some 0, .use⟩⟩]

def updated (change : Change) : Table :=
  push initial (appended change) (calculate (appended change).newRecipe (initial 0))

def repaired (change : Change) : List Stack :=
  deliver mark (updated change) children (full false initial children)

def stale (change : Change) : List Stack :=
  deliver (fun _ => false) (updated change) children (full false initial children)

def cases : List Change := [.reset 11 1 3, .set 99 3, .increment 99 2]

def orderedB (current : Bool) (table : Table) : List Edit → Bool
  | [] => true
  | edit :: rest =>
    let recipe := if current then edit.newRecipe else edit.oldRecipe
    let valid := match recipe.source with
      | none => true
      | some i => match (table edit.name)[i]? with
        | none => false
        | some (owner, _) => owner.isPrefixOf edit.owner
    valid && orderedB current (push table edit (calculate recipe (table edit.name))) rest

theorem orderedB_sound (current : Bool) (table : Table) (edits : List Edit)
    (valid : orderedB current table edits = true) : Ordered current table edits := by
  induction edits generalizing table with
  | nil => trivial
  | cons edit rest ih =>
    simp only [orderedB, Bool.and_eq_true] at valid
    constructor
    · unfold ValidSource
      cases hs : (if current then edit.newRecipe else edit.oldRecipe).source with
      | none => trivial
      | some i =>
        rw [hs] at valid
        cases hr : (table edit.name)[i]? with
        | none => simp [hr] at valid
        | some row =>
          obtain ⟨owner, stack⟩ := row
          refine ⟨owner, stack, hr, ?_⟩
          simp only [hr] at valid
          exact valid.1
    · exact ih _ valid.2

example : cases.map (fun change => (repaired change).map counter) =
    [[3, 3, 7], [3, 3, 7], [3, 3, 7]] := by decide +kernel

example : cases.map (fun change => (stale change).map counter) =
    [[1, 1, 7], [1, 1, 7], [1, 1, 7]] := by decide +kernel

example : (full true initial children).map counter = [0, 0, 7] := by decide +kernel

example : cases.map (fun change => orderedB true (updated change) children) = [true, true, true] := by
  decide +kernel

example : orderedB false initial children = true := by decide +kernel

example : UnchangedClean mark children := by
  intro edit member clean
  simp [children] at member
  rcases member with first | second | last
  · subst edit; simp [mark] at clean
  · subst edit; simp [mark] at clean
  · subst edit; rfl

example : counter [⟨20, 5⟩, ⟨10, 1⟩] = counter [⟨20, 5⟩, ⟨10, 3⟩] ∧
    counters [⟨20, 5⟩, ⟨10, 1⟩] ≠ counters [⟨20, 5⟩, ⟨10, 3⟩] := by decide +kernel

example : apply (.increment 30 2) [] = [⟨30, 2⟩] ∧
    apply (.increment 30 2) [⟨10, 1⟩] = [⟨10, 3⟩] := by decide +kernel

example : counters (apply (.reset 20 0 5) [⟨10, 3⟩]) = [3, 5] ∧
    counters (apply (.reset 20 1 5) [⟨10, 3⟩]) = [5] := by decide +kernel

example : orderedB true initial children = false := by decide +kernel

def staleSources : List Edit := children.map (fun edit => { edit with newRecipe := edit.oldRecipe })

example : (deliver mark (updated (.set 99 3)) staleSources (full false initial children)).map counter =
    [1, 3, 7] := by decide +kernel

example : apply (.reset 11 1 1) [⟨10, 1⟩] ≠ [⟨10, 1⟩] ∧
    counter (apply (.reset 11 1 1) [⟨10, 1⟩]) = 1 := by decide +kernel

end CounterDelivery.Examples
