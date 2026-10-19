import Std

namespace ScannerTraversal

inductive Event where
  | text (source : Nat)
  | boundary (lineBreaker : Bool) (br : Bool)
  deriving Repr, DecidableEq

inductive Tree where
  | text (source : Nat)
  | ruby
  | inlineBox (principal overflow : List Tree)
  | atomic (br : Bool)
  | placeholder (absolute : Bool) (firstLetter : Option Tree)
  deriving Repr

def meaning : Tree → List Event
  | .text source => [.text source]
  | .ruby => []
  | .inlineBox principal overflow => principal.flatMap meaning ++ overflow.flatMap meaning
  | .atomic br => [.boundary true br, .boundary true br]
  | .placeholder absolute child =>
      (if absolute then [.boundary true false] else []) ++
      match child with
      | none => []
      | some target => [.boundary false false] ++ meaning target ++ [.boundary false false]

def cost : Tree → Nat
  | .text _ => 2
  | .ruby => 1
  | .inlineBox principal overflow =>
      1 + (principal.map cost).sum + (overflow.map cost).sum
  | .atomic _ => 3
  | .placeholder absolute child =>
      1 + (if absolute then 1 else 0) +
      match child with
      | none => 0
      | some target => 2 + cost target

theorem cost_positive (tree : Tree) : 0 < cost tree := by
  cases tree with
  | text _ => simp [cost]
  | ruby => simp [cost]
  | inlineBox principal overflow => simp [cost]; omega
  | atomic br => simp [cost]
  | placeholder absolute child =>
      cases absolute <;> cases child <;> simp [cost] <;> omega

inductive Task where
  | enter (tree : Tree)
  | emit (event : Event)
  deriving Repr

def taskCost : Task → Nat
  | .enter tree => cost tree
  | .emit _ => 1

def workCost (tasks : List Task) : Nat := (tasks.map taskCost).sum

def taskMeaning : Task → List Event
  | .enter tree => meaning tree
  | .emit event => [event]

def output (tasks : List Task) : List Event := tasks.flatMap taskMeaning

def expand : Tree → List Task
  | .text source => [.emit (.text source)]
  | .ruby => []
  | .inlineBox principal overflow =>
      principal.map Task.enter ++ overflow.map Task.enter
  | .atomic br => [.emit (.boundary true br), .emit (.boundary true br)]
  | .placeholder absolute child =>
      (if absolute then [.emit (.boundary true false)] else []) ++
      match child with
      | none => []
      | some target => [.emit (.boundary false false), .enter target, .emit (.boundary false false)]

theorem expansion_cost (tree : Tree) : workCost (expand tree) + 1 = cost tree := by
  cases tree with
  | text source => simp [workCost, expand, cost, taskCost]
  | ruby => simp [workCost, expand, cost]
  | inlineBox principal overflow =>
      simp only [expand, workCost, List.map_append, List.sum_append, List.map_map, cost]
      change (principal.map cost).sum + (overflow.map cost).sum + 1 = 1 + (principal.map cost).sum + (overflow.map cost).sum
      omega
  | atomic br => simp [workCost, expand, cost, taskCost]
  | placeholder absolute child =>
      cases absolute <;> cases child <;> simp [workCost, expand, cost, taskCost] <;> omega

theorem expansion_meaning (tree : Tree) : output (expand tree) = meaning tree := by
  cases tree with
  | text source => simp [output, expand, meaning, taskMeaning]
  | ruby => simp [output, expand, meaning]
  | inlineBox principal overflow =>
      simp [output, expand, meaning, List.flatMap_append, List.flatMap_map, taskMeaning]
  | atomic br => simp [output, expand, meaning, taskMeaning]
  | placeholder absolute child =>
      cases absolute <;> cases child <;> simp [output, expand, meaning, taskMeaning]

def nativeWalk : Nat → List Task → List Event
  | 0, _ => []
  | _ + 1, [] => []
  | fuel + 1, .emit event :: rest => event :: nativeWalk fuel rest
  | fuel + 1, .enter tree :: rest => nativeWalk fuel (expand tree ++ rest)

theorem walk_refinement (fuel : Nat) (tasks : List Task)
    (enough : workCost tasks ≤ fuel) : nativeWalk fuel tasks = output tasks := by
  induction fuel generalizing tasks with
  | zero =>
      cases tasks with
      | nil => rfl
      | cons task rest =>
          cases task with
          | emit event => simp [workCost, taskCost] at enough
          | enter tree =>
              have positive := cost_positive tree
              simp only [workCost, List.map_cons, List.sum_cons, taskCost] at enough
              omega
  | succ fuel ih =>
      cases tasks with
      | nil => rfl
      | cons task rest =>
          cases task with
          | emit event =>
              have bound : workCost rest ≤ fuel := by
                simp [workCost, taskCost] at enough ⊢
                omega
              simp [nativeWalk, ih rest bound, output, taskMeaning]
          | enter tree =>
              have decrease := expansion_cost tree
              have bound : workCost (expand tree ++ rest) ≤ fuel := by
                simp only [workCost, List.map_cons, List.sum_cons, taskCost] at enough
                simp only [workCost, List.map_append, List.sum_append] at decrease ⊢
                omega
              rw [nativeWalk, ih _ bound]
              simp only [output, List.flatMap_append, List.flatMap_cons, taskMeaning]
              exact congrArg (· ++ output rest) (expansion_meaning tree)

def textSources (events : List Event) : List Nat := events.filterMap fun event =>
  match event with
  | .text source => some source
  | .boundary _ _ => none

theorem scanner_source_order (tree : Tree) :
    textSources (nativeWalk (cost tree) [.enter tree]) = textSources (meaning tree) := by
  rw [walk_refinement _ _ (by simp [workCost, taskCost])]
  simp [output, taskMeaning]

theorem ordinary_placeholder_invisible : meaning (.placeholder false none) = [] := by simp [meaning]

theorem absolute_placeholder_flushes :
    meaning (.placeholder true none) = [.boundary true false] := by simp [meaning]

theorem first_letter_shape_boundary (target : Tree) :
    meaning (.placeholder false (some target)) =
      [.boundary false false] ++ meaning target ++ [.boundary false false] := by simp [meaning]

#print axioms expansion_cost
#print axioms expansion_meaning
#print axioms walk_refinement
#print axioms scanner_source_order
#print axioms ordinary_placeholder_invisible
#print axioms absolute_placeholder_flushes
#print axioms first_letter_shape_boundary
end ScannerTraversal
