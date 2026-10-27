import Subtree

namespace LineReady
open Subtree

structure Line where
  dirty : Bool
  children : List Tree

def oldSkip (line : Line) : Line := { line with dirty := false }
def newSkip (line : Line) : Line :=
  { dirty := false, children := line.children.map markRoot }
def firstOnly (line : Line) : Line :=
  { dirty := false, children := match line.children with
      | [] => []
      | t :: ts => markRoot t :: ts }
def selectedBranch (hidden ownsAnonymous : Bool) (line : Line) : Option Line :=
  if hidden && !ownsAnonymous then some (newSkip line) else none

def closures (ts : List Tree) : Bool :=
  match ts with
  | [] => true
  | t :: rest => rootClosure t && closures rest

def lineEligible (n : Nat) (path : List Nat) (line : Line) : Bool :=
  (line.children[n]?).any (eligibleAt path)

theorem skipped_flag_cleared (line : Line) : (newSkip line).dirty = false := rfl

theorem old_skip_keeps_frames (line : Line) : (oldSkip line).children = line.children := rfl

theorem root_count_preserved (line : Line) :
    (newSkip line).children.length = line.children.length := by simp [newSkip]

theorem exact_all_root_coverage (ts : List Tree) :
    allDirtyList (ts.map markRoot) = closures ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => simp [allDirtyList, closures, root_coverage_exact, ih]

theorem all_roots_under_closure (line : Line) (h : closures line.children = true) :
    allDirtyList (newSkip line).children = true := by
  simpa [newSkip, exact_all_root_coverage] using h

theorem allDirtyList_get (ts : List Tree) (n : Nat) (t : Tree)
    (all : allDirtyList ts = true) (found : ts[n]? = some t) : allDirty t = true := by
  induction ts generalizing n with
  | nil => simp at found
  | cons x xs ih =>
    have both : allDirty x = true ∧ allDirtyList xs = true := by simpa [allDirtyList] using all
    cases n with
    | zero => simp at found; subst t; exact both.1
    | succ n => exact ih n both.2 (by simpa using found)

theorem allDirty_locate (path : List Nat) (t target : Tree)
    (all : allDirty t = true) (found : locate path t = some target) :
    eligible target = true := by
  induction path generalizing t with
  | nil => simp [locate] at found; subst target
           cases t with
           | node id d h table cs => simp_all [allDirty, eligible]
  | cons n path ih =>
    cases t with
    | node id d h table cs =>
      have both : d = true ∧ allDirtyList cs = true := by simpa [allDirty] using all
      have children : allDirtyList cs = true := both.2
      cases childEq : cs[n]? with
      | none => simp [locate, childEq] at found
      | some child =>
        exact ih child (allDirtyList_get cs n child children childEq)
          (by simpa [locate, childEq] using found)

theorem selected_descendant_ready (line : Line) (n : Nat) (path : List Nat)
    (root target : Tree) (closure : closures line.children = true)
    (child : (newSkip line).children[n]? = some root)
    (found : locate path root = some target) : eligible target = true :=
  allDirty_locate path root target
    (allDirtyList_get _ n root (all_roots_under_closure line closure) child) found

theorem each_root_ready_without_closure (line : Line) (n : Nat) (root : Tree)
    (child : line.children[n]? = some root) :
    lineEligible n [] (newSkip line) = true := by
  simp [lineEligible, newSkip, List.getElem?_map, child, eligibleAt, locate, root_is_eligible]

theorem existing_eligibility_preserved (line : Line) (n : Nat) (path : List Nat)
    (root : Tree) (child : line.children[n]? = some root)
    (ready : eligibleAt path root = true) : lineEligible n path (newSkip line) = true := by
  simpa [lineEligible, newSkip, List.getElem?_map, child] using
    root_preserves_eligible_path path root ready

theorem actual_provider_recovery (line : Line) (n : Nat) (path : List Nat)
    (root target : Tree) (frame : Hidden.Frame) (layout : Hidden.Key → Hidden.Size)
    (key : Hidden.Key) (closure : closures line.children = true)
    (child : (newSkip line).children[n]? = some root)
    (found : locate path root = some target) :
    (Hidden.geometryQuery true layout key {frame with dirty := eligible target}).geometry = layout key :=
  Hidden.dirty_query_uses_actual_provider layout key _
    (selected_descendant_ready line n path root target closure child found)

theorem line_flag_not_query_bit (line : Line) (flag : Bool) (n : Nat) (path : List Nat) :
    lineEligible n path {line with dirty := flag} = lineEligible n path line := rfl

theorem anonymous_owner_excluded (hidden : Bool) (line : Line) :
    selectedBranch hidden true line = none := by simp [selectedBranch]

theorem visible_branch_excluded (owns : Bool) (line : Line) :
    selectedBranch false owns line = none := by simp [selectedBranch]

theorem hidden_selected (line : Line) :
    selectedBranch true false line = some (newSkip line) := rfl

def clean (id : Nat) : Tree := .node id false false false []
def inlineLine : Line := ⟨true, [clean 1, clean 2]⟩

theorem later_inline_first_only_fails : lineEligible 1 [] (firstOnly inlineLine) = false := by
  simp [lineEligible, firstOnly, inlineLine, clean, eligibleAt, locate, eligible]

theorem later_inline_all_roots_recovers : lineEligible 1 [] (newSkip inlineLine) = true := by
  simp [lineEligible, newSkip, inlineLine, clean, markRoot, eligibleAt, locate, eligible]

theorem dirty_line_only_fails : lineEligible 1 [] inlineLine = false := by
  simp [lineEligible, inlineLine, clean, eligibleAt, locate, eligible]

theorem old_clean_skip_fails : lineEligible 1 [] (oldSkip inlineLine) = false := by
  simp [lineEligible, oldSkip, inlineLine, clean, eligibleAt, locate, eligible]

theorem dirty_barrier_counterexample :
    lineEligible 0 [0] (newSkip ⟨true, [dirtyBarrier]⟩) = false := by
  simpa [lineEligible, newSkip] using already_dirty_root_clean_leaf

theorem absent_hidden_ancestor_no_force (target : Tree) : needsForce false target = false :=
  no_hidden_ancestor_no_forcing target

end LineReady
