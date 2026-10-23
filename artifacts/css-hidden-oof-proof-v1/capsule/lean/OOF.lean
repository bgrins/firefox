import Subtree

namespace OOF

inductive Timing where
  | original | beforeInput | afterInput
  deriving DecidableEq, Repr

structure Rect where
  x : Int
  y : Int
  w : Int
  h : Int
  deriving DecidableEq, Repr

structure Response where
  tree : Subtree.Tree
  size : Hidden.Size

structure Result where
  tree : Subtree.Tree
  iResize : Bool
  rect : Rect

def prepare (timing : Timing) (hidden : Bool) (t : Subtree.Tree) : Subtree.Tree :=
  if timing == .beforeInput && hidden then Subtree.markRoot t else t

def resizeFlag (t : Subtree.Tree) (differs : Bool) : Bool :=
  !Subtree.dirty t && differs

def callbackTree (timing : Timing) (hidden : Bool) (t : Subtree.Tree) : Subtree.Tree :=
  if timing == .afterInput && hidden then Subtree.markRoot t else t

def didReflow (hidden : Bool) (t : Subtree.Tree) : Subtree.Tree :=
  if hidden then t else
    match t with | .node id _ _ table cs => .node id false false table cs

def execute (timing : Timing) (hidden next differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect)
    (t : Subtree.Tree) : Result :=
  let prepared := prepare timing hidden t
  let resize := resizeFlag prepared differs
  let entered := callbackTree timing hidden prepared
  let response := if hidden && !next then Response.mk entered Hidden.zero else provider resize entered
  ⟨didReflow hidden response.tree, resize, place response.size⟩

def nativeHidden (parentHides ownsAnon anonChild : Bool) : Bool :=
  parentHides && !(ownsAnon && anonChild)

def centered (s : Hidden.Size) : Rect := ⟨600 + (12000 - s.i) / 2, 600, s.i, s.b⟩

def clean : Subtree.Tree := .node 1 false false false []

theorem visible_preservation (timing : Timing) (next differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    execute timing false next differs provider place t = execute .original false next differs provider place t := by
  simp [execute, prepare, callbackTree]

theorem hidden_input_dirty (t : Subtree.Tree) :
    Subtree.dirty (prepare .beforeInput true t) = true := by
  simpa [prepare] using Subtree.root_is_dirty t

theorem pre_input_resize_false (t : Subtree.Tree) (differs : Bool) :
    resizeFlag (prepare .beforeInput true t) differs = false := by
  simp [resizeFlag, hidden_input_dirty]

theorem late_input_uses_old_flag (t : Subtree.Tree) (differs : Bool) :
    resizeFlag (prepare .afterInput true t) differs = resizeFlag t differs := by simp [prepare]

theorem timing_counterexample :
    resizeFlag (prepare .beforeInput true clean) true = false ∧
    resizeFlag (prepare .afterInput true clean) true = true ∧
    Subtree.dirty (callbackTree .afterInput true clean) = true := by decide

theorem hidden_didReflow_preserves (t : Subtree.Tree) : didReflow true t = t := rfl

theorem repaired_skipped_tree (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    (execute .beforeInput true false differs provider place t).tree = Subtree.markRoot t := by
  simp [execute, prepare, callbackTree, didReflow]

theorem repaired_skipped_rect (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    (execute .beforeInput true false differs provider place t).rect = place Hidden.zero := by
  simp [execute]

theorem skipped_original_tree (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    (execute .original true false differs provider place t).tree = t := by
  simp [execute, prepare, callbackTree, didReflow]

theorem repaired_root_eligible (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    Subtree.eligible (execute .beforeInput true false differs provider place t).tree = true := by
  rw [repaired_skipped_tree]
  exact Subtree.root_is_eligible t

theorem repaired_leaf_eligible (path : List Nat) (t : Subtree.Tree)
    (differs : Bool) (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect)
    (clear : Subtree.clearRootPath path t = true) :
    Subtree.eligibleAt path (execute .beforeInput true false differs provider place t).tree = true := by
  rw [repaired_skipped_tree]
  exact Subtree.clear_root_path_marks path t clear

theorem repaired_leaf_recovery (path : List Nat) (t target : Subtree.Tree)
    (differs : Bool) (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect)
    (frame : Hidden.Frame) (layout : Hidden.Key → Hidden.Size) (key : Hidden.Key)
    (clear : Subtree.clearRootPath path t = true)
    (found : Subtree.locate path (execute .beforeInput true false differs provider place t).tree = some target) :
    (Hidden.geometryQuery true layout key {frame with dirty := Subtree.eligible target}).geometry = layout key := by
  rw [repaired_skipped_tree] at found
  exact Subtree.selected_query_recovery path t target frame layout key clear found

theorem root_coverage_condition (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) (t : Subtree.Tree) :
    Subtree.allDirty (execute .beforeInput true false differs provider place t).tree = Subtree.rootClosure t := by
  rw [repaired_skipped_tree]
  exact Subtree.root_coverage_exact t

theorem existing_eligible_leaf_preserved (path : List Nat) (t : Subtree.Tree)
    (differs : Bool) (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect)
    (before : Subtree.eligibleAt path t = true) :
    Subtree.eligibleAt path (execute .beforeInput true false differs provider place t).tree = true := by
  rw [repaired_skipped_tree]
  exact Subtree.root_preserves_eligible_path path t before

theorem dirty_barrier_remains (differs : Bool)
    (provider : Bool → Subtree.Tree → Response) (place : Hidden.Size → Rect) :
    Subtree.eligibleAt [0] (execute .beforeInput true false differs provider place Subtree.dirtyBarrier).tree = false := by
  rw [repaired_skipped_tree]
  exact Subtree.already_dirty_root_clean_leaf

theorem old_clean_zero_witness (provider : Bool → Subtree.Tree → Response) :
    Subtree.eligible (execute .original true false true provider centered clean).tree = false ∧
    (execute .original true false true provider centered clean).rect = ⟨6600, 600, 0, 0⟩ := by
  simp [execute, prepare, callbackTree, didReflow, clean, Subtree.eligible, centered, Hidden.zero]

theorem repaired_temporary_zero_witness (provider : Bool → Subtree.Tree → Response) :
    Subtree.eligible (execute .beforeInput true false true provider centered clean).tree = true ∧
    (execute .beforeInput true false true provider centered clean).rect = ⟨6600, 600, 0, 0⟩ := by
  constructor
  · exact repaired_root_eligible true provider centered clean
  · simp [execute, centered, Hidden.zero]

theorem specified_placement_witness : centered ⟨720, 480⟩ = ⟨6240, 600, 720, 480⟩ := by decide

theorem anon_exception_preserved : nativeHidden true true true = false := by decide

theorem placeholder_hidden_witness :
    nativeHidden true false false = true := by rfl

def erasingProvider (_ : Bool) (_ : Subtree.Tree) : Response := ⟨clean, ⟨720, 480⟩⟩

theorem continuation_provider_boundary :
    Subtree.eligible (execute .beforeInput true true true erasingProvider centered clean).tree = false := by decide

def resizeSensitive (flag : Bool) (t : Subtree.Tree) : Response :=
  ⟨t, ⟨if flag then 2 else 1, 1⟩⟩

theorem non_skipping_timing_output_can_differ :
    (execute .beforeInput true true true resizeSensitive centered clean).rect ≠
    (execute .afterInput true true true resizeSensitive centered clean).rect := by decide

theorem clean_query_does_not_fix_original_zero (layout : Hidden.Key → Hidden.Size) (key : Hidden.Key) :
    (Hidden.geometryQuery true layout key ⟨false, Hidden.zero, none⟩).geometry = Hidden.zero := by
  simp [Hidden.geometryQuery]

end OOF
