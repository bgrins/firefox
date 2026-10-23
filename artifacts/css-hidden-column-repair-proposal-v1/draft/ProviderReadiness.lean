import Std

namespace ColumnReadinessDraft

inductive Kind where
  | column | group | table | other
  deriving DecidableEq, BEq, Repr

structure Frame where
  kind : Kind
  dirty : Bool
  parent : Option Nat
  inFlowParent : Option Nat
  hidden : Bool
  deriving DecidableEq, Repr

abbrev World := Nat → Option Frame

def groupOwner (w : World) (group : Nat) : Option Nat := do
  let g ← w group
  if g.kind != .group then none else do
    let table ← g.parent
    let t ← w table
    if t.kind == .table then some table else none

def provider (w : World) (target : Nat) : Option Nat := do
  let f ← w target
  match f.kind with
  | .column => do
      let group ← f.parent
      groupOwner w group
  | .group => groupOwner w target
  | _ => none

def oldGate (w : World) (target : Nat) : Bool :=
  match w target with
  | none => false
  | some f => f.dirty

def newGate (w : World) (target : Nat) : Bool :=
  if oldGate w target then true else
    match provider w target with
    | none => false
    | some table => oldGate w table

theorem gate_extends (w : World) (target : Nat)
    (h : oldGate w target = true) : newGate w target = true := by
  simp [newGate, h]

theorem clean_without_provider (w : World) (target : Nat)
    (h : oldGate w target = false) (hp : provider w target = none) :
    newGate w target = false := by
  simp [newGate, h, hp]

theorem clean_provider_stays_closed (w : World) (target table : Nat)
    (h : oldGate w target = false) (hp : provider w target = some table)
    (ht : oldGate w table = false) : newGate w target = false := by
  simp [newGate, h, hp, ht]

theorem dirty_provider_admits (w : World) (target table : Nat)
    (h : oldGate w target = false) (hp : provider w target = some table)
    (ht : oldGate w table = true) : newGate w target = true := by
  simp [newGate, h, hp, ht]

theorem normal_clean_unchanged (w : World) (target : Nat) (p ip : Option Nat)
    (hidden : Bool)
    (hf : w target = some ⟨.other, false, p, ip, hidden⟩) :
    oldGate w target = false ∧ newGate w target = false := by
  simp [oldGate, newGate, provider, hf]

theorem clean_group_dirty_table (w : World) (group table : Nat)
    (gi ti tp : Option Nat) (gh th : Bool)
    (hg : w group = some ⟨.group, false, some table, gi, gh⟩)
    (ht : w table = some ⟨.table, true, tp, ti, th⟩) :
    newGate w group = true := by
  simp [newGate, oldGate, provider, groupOwner, hg, ht]

theorem clean_column_dirty_table (w : World) (column group table : Nat)
    (ci gi ti tp : Option Nat) (ch gh th gd : Bool)
    (hc : w column = some ⟨.column, false, some group, ci, ch⟩)
    (hg : w group = some ⟨.group, gd, some table, gi, gh⟩)
    (ht : w table = some ⟨.table, true, tp, ti, th⟩) :
    newGate w column = true := by
  simp [newGate, oldGate, provider, groupOwner, hc, hg, ht]

def ancestors (w : World) : Nat → Nat → List Nat
  | 0, _ => []
  | fuel + 1, target =>
      match w target with
      | none => []
      | some f => match f.inFlowParent with
        | none => []
        | some parent => match w parent with
          | none => []
          | some p =>
              (if p.hidden then [parent] else []) ++ ancestors w fuel parent

def oldSelection (w : World) (fuel target : Nat) : List Nat :=
  if oldGate w target then ancestors w fuel target else []

def newSelection (w : World) (fuel target : Nat) : List Nat :=
  if newGate w target then ancestors w fuel target else []

theorem dirty_selection_unchanged (w : World) (fuel target : Nat)
    (h : oldGate w target = true) :
    newSelection w fuel target = oldSelection w fuel target := by
  simp [newSelection, oldSelection, gate_extends w target h, h]

theorem admitted_selection_uses_original_target (w : World) (fuel target : Nat)
    (h : newGate w target = true) :
    newSelection w fuel target = ancestors w fuel target := by
  simp [newSelection, h]

def cleanProviderDirtyAncestor : World
  | 0 => some ⟨.column, false, some 1, some 1, false⟩
  | 1 => some ⟨.group, false, some 2, some 2, false⟩
  | 2 => some ⟨.table, false, some 3, some 3, false⟩
  | 3 => some ⟨.other, true, none, none, true⟩
  | _ => none

example : provider cleanProviderDirtyAncestor 0 = some 2 ∧
    oldGate cleanProviderDirtyAncestor 3 = true ∧
    ancestors cleanProviderDirtyAncestor 4 0 = [3] ∧
    newGate cleanProviderDirtyAncestor 0 = false := by decide

def hiddenDirtyProvider : World
  | 0 => some ⟨.column, false, some 1, some 1, false⟩
  | 1 => some ⟨.group, false, some 2, some 2, false⟩
  | 2 => some ⟨.table, true, none, none, true⟩
  | _ => none

example : newSelection hiddenDirtyProvider 3 0 = [2] ∧
    ancestors hiddenDirtyProvider 3 2 = [] := by decide

end ColumnReadinessDraft
