import Subtree
import ProviderReadiness
import LineReady

namespace ProviderPath
open Subtree

theorem selected_provider_ready (tree target : Tree) (path : List Nat)
    (clear : clearRootPath path tree = true)
    (found : locate path (markRoot tree) = some target) : eligible target = true := by
  simpa [eligibleAt, found] using clear_root_path_marks path tree clear

theorem clean_query_path_provider_admitted (tree target : Tree) (path : List Nat)
    (w : ColumnReadiness.World) (queried table : Nat)
    (clear : clearRootPath path tree = true)
    (found : locate path (markRoot tree) = some target)
    (identity : ColumnReadiness.oldGate w table = eligible target)
    (cleanQuery : ColumnReadiness.oldGate w queried = false)
    (provider : ColumnReadiness.provider w queried = some table) :
    ColumnReadiness.newGate w queried = true := by
  apply ColumnReadiness.dirty_provider_admits w queried table cleanQuery provider
  rw [identity]
  exact selected_provider_ready tree target path clear found

theorem admitted_walk_keeps_original_target (tree target : Tree) (path : List Nat)
    (w : ColumnReadiness.World) (queried table fuel : Nat)
    (clear : clearRootPath path tree = true)
    (found : locate path (markRoot tree) = some target)
    (identity : ColumnReadiness.oldGate w table = eligible target)
    (cleanQuery : ColumnReadiness.oldGate w queried = false)
    (provider : ColumnReadiness.provider w queried = some table) :
    ColumnReadiness.newSelection w fuel queried = ColumnReadiness.ancestors w fuel queried :=
  ColumnReadiness.admitted_selection_uses_original_target w fuel queried
    (clean_query_path_provider_admitted tree target path w queried table clear found identity cleanQuery provider)

theorem selected_line_root_marked (line : LineReady.Line) (n : Nat) (root : Tree)
    (selected : line.children[n]? = some root) :
    (LineReady.newSkip line).children[n]? = some (markRoot root) := by
  simp [LineReady.newSkip, List.getElem?_map, selected]

theorem selected_line_path_admitted (line : LineReady.Line) (n : Nat)
    (tree target : Tree) (path : List Nat) (w : ColumnReadiness.World)
    (queried table : Nat) (selected : line.children[n]? = some tree)
    (clear : clearRootPath path tree = true)
    (found : locate path (markRoot tree) = some target)
    (identity : ColumnReadiness.oldGate w table = eligible target)
    (cleanQuery : ColumnReadiness.oldGate w queried = false)
    (provider : ColumnReadiness.provider w queried = some table) :
    (LineReady.newSkip line).children[n]? = some (markRoot tree) ∧
    ColumnReadiness.newGate w queried = true :=
  ⟨selected_line_root_marked line n tree selected,
   clean_query_path_provider_admitted tree target path w queried table clear found identity cleanQuery provider⟩

def tableTree (rootDirty : Bool) : Tree :=
  .node 0 rootDirty false false [
    .node 1 false false false [
      .node 2 false false true [.node 3 false false false []]]]

def projectedWorld (tree : Tree) : ColumnReadiness.World
  | 0 => some ⟨.other, eligibleAt [] tree, none, none, true⟩
  | 1 => some ⟨.table, eligibleAt [0] tree, some 0, some 0, false⟩
  | 2 => some ⟨.group, eligibleAt [0,0] tree, some 1, some 1, false⟩
  | 3 => some ⟨.column, eligibleAt [0,0,0] tree, some 2, some 2, false⟩
  | _ => none

def markedWorld (dirty : Bool) := projectedWorld (markRoot (tableTree dirty))

theorem table_path_is_clear : clearRootPath [0] (tableTree false) = true := by
  simp [clearRootPath, clearPath, tableTree]

theorem whole_tree_closure_is_false : rootClosure (tableTree false) = false := by
  simp [rootClosure, tableTree, barrierClosures, barrierClosure, allDirty, allDirtyList]

theorem marked_provider_ready_columns_clean :
    eligibleAt [0] (markRoot (tableTree false)) = true ∧
    eligibleAt [0,0] (markRoot (tableTree false)) = false ∧
    eligibleAt [0,0,0] (markRoot (tableTree false)) = false := by
  simp [eligibleAt, locate, markRoot, markDesc, tableTree, eligible]

theorem marked_tree_still_not_all_dirty : allDirty (markRoot (tableTree false)) = false := by
  simp [markRoot, markDesc, tableTree, allDirty, allDirtyList]

theorem concrete_provider_chains :
    ColumnReadiness.provider (markedWorld false) 3 = some 1 ∧
    ColumnReadiness.provider (markedWorld false) 2 = some 1 := by
  simp [ColumnReadiness.provider, ColumnReadiness.groupOwner, markedWorld, projectedWorld]

theorem clean_column_old_closed_new_open :
    ColumnReadiness.oldGate (markedWorld false) 3 = false ∧
    ColumnReadiness.newGate (markedWorld false) 3 = true := by
  simp [ColumnReadiness.oldGate, ColumnReadiness.newGate, ColumnReadiness.provider,
    ColumnReadiness.groupOwner, markedWorld, projectedWorld, eligibleAt, locate,
    markRoot, markDesc, tableTree, eligible]

theorem clean_group_old_closed_new_open :
    ColumnReadiness.oldGate (markedWorld false) 2 = false ∧
    ColumnReadiness.newGate (markedWorld false) 2 = true := by
  simp [ColumnReadiness.oldGate, ColumnReadiness.newGate, ColumnReadiness.provider,
    ColumnReadiness.groupOwner, markedWorld, projectedWorld, eligibleAt, locate,
    markRoot, markDesc, tableTree, eligible]

theorem concrete_hidden_ancestor_selected :
    ColumnReadiness.newSelection (markedWorld false) 4 3 = [0] := by
  rw [ColumnReadiness.admitted_selection_uses_original_target _ _ _ clean_column_old_closed_new_open.2]
  simp [ColumnReadiness.ancestors, markedWorld, projectedWorld]

theorem dirty_ancestor_barrier_keeps_provider_clean :
    eligibleAt [0] (markRoot (tableTree true)) = false ∧
    clearRootPath [0] (tableTree true) = false := by
  simp [eligibleAt, locate, markRoot, tableTree, eligible, clearRootPath]

theorem dirty_ancestor_countermodel :
    ColumnReadiness.oldGate (markedWorld true) 0 = true ∧
    ColumnReadiness.provider (markedWorld true) 3 = some 1 ∧
    ColumnReadiness.ancestors (markedWorld true) 4 3 = [0] ∧
    ColumnReadiness.newGate (markedWorld true) 3 = false := by
  simp [ColumnReadiness.oldGate, ColumnReadiness.newGate, ColumnReadiness.provider,
    ColumnReadiness.groupOwner, ColumnReadiness.ancestors, markedWorld, projectedWorld,
    eligibleAt, locate, markRoot, tableTree, eligible]

end ProviderPath
