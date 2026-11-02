import Std

namespace DeclarationCapacity

structure Declaration where
  property : Nat
  value : Nat
deriving DecidableEq, Repr

structure Builder where
  vector : List Declaration
  chain : List Nat
deriving DecidableEq, Repr

def empty : Builder := ⟨[], []⟩

def note (sentinel target : Nat) (s : Builder) (d : Declaration) : Builder :=
  ⟨s.vector ++ [d], s.chain ++
    (if d.property = target ∧ s.vector.length < sentinel then [s.vector.length] else [])⟩

def build (sentinel target : Nat) (s : Builder) (ds : List Declaration) : Builder :=
  ds.foldl (note sentinel target) s

def fullProjection (target offset : Nat) : List Declaration → List Nat
  | [] => []
  | d :: ds => (if d.property = target then [offset] else []) ++
      fullProjection target (offset + 1) ds

def admitted (sentinel target offset : Nat) : List Declaration → List Nat
  | [] => []
  | d :: ds => (if d.property = target ∧ offset < sentinel then [offset] else []) ++
      admitted sentinel target (offset + 1) ds

theorem build_vector (sentinel target : Nat) (s : Builder) (ds : List Declaration) :
    (build sentinel target s ds).vector = s.vector ++ ds := by
  induction ds generalizing s with
  | nil => simp [build]
  | cons d ds ih =>
      simpa [build, note, List.append_assoc] using ih (note sentinel target s d)

theorem build_chain (sentinel target : Nat) (s : Builder) (ds : List Declaration) :
    (build sentinel target s ds).chain =
      s.chain ++ admitted sentinel target s.vector.length ds := by
  induction ds generalizing s with
  | nil => simp [build, admitted]
  | cons d ds ih =>
      simpa [build, note, admitted, List.append_assoc] using ih (note sentinel target s d)

theorem admitted_complete (sentinel target offset : Nat) (ds : List Declaration)
    (bounded : offset + ds.length ≤ sentinel) :
    admitted sentinel target offset ds = fullProjection target offset ds := by
  induction ds generalizing offset with
  | nil => rfl
  | cons d ds ih =>
      have here : offset < sentinel := by simp only [List.length_cons] at bounded; omega
      have rest : offset + 1 + ds.length ≤ sentinel := by
        simp only [List.length_cons] at bounded; omega
      simp only [admitted, fullProjection, here, and_true, ih (offset + 1) rest]

theorem fresh_builder_complete (sentinel target : Nat) (ds : List Declaration)
    (bounded : ds.length ≤ sentinel) :
    (build sentinel target empty ds).chain = fullProjection target 0 ds := by
  rw [build_chain]
  simpa [empty] using admitted_complete sentinel target 0 ds (by simpa using bounded)

theorem unrelated_projection (target offset n : Nat) (d : Declaration)
    (unrelated : d.property ≠ target) :
    fullProjection target offset (List.replicate n d) = [] := by
  induction n generalizing offset with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ, fullProjection, unrelated, ih]

theorem unrelated_admission (sentinel target offset n : Nat) (d : Declaration)
    (unrelated : d.property ≠ target) :
    admitted sentinel target offset (List.replicate n d) = [] := by
  induction n generalizing offset with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ, admitted, unrelated, ih]

theorem projection_append (target offset : Nat) (xs ys : List Declaration) :
    fullProjection target offset (xs ++ ys) =
      fullProjection target offset xs ++ fullProjection target (offset + xs.length) ys := by
  induction xs generalizing offset with
  | nil => simp [fullProjection]
  | cons d xs ih =>
      simp [fullProjection, ih, List.append_assoc, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem admitted_append (sentinel target offset : Nat) (xs ys : List Declaration) :
    admitted sentinel target offset (xs ++ ys) =
      admitted sentinel target offset xs ++ admitted sentinel target (offset + xs.length) ys := by
  induction xs generalizing offset with
  | nil => simp [admitted]
  | cons d xs ih =>
      simp [admitted, ih, List.append_assoc, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem sole_target_projection (target n : Nat) (other wanted : Declaration)
    (different : other.property ≠ target) (same : wanted.property = target) :
    fullProjection target 0 (List.replicate n other ++ [wanted]) = [n] := by
  simp [projection_append, unrelated_projection target 0 n other different,
    fullProjection, same]

theorem sole_target_admission (sentinel target n : Nat) (other wanted : Declaration)
    (different : other.property ≠ target) (same : wanted.property = target) :
    (build sentinel target empty (List.replicate n other ++ [wanted])).chain =
      if n < sentinel then [n] else [] := by
  simp [build_chain, empty, admitted_append,
    unrelated_admission sentinel target 0 n other different, admitted, same]

theorem sole_target_lost (sentinel target n : Nat) (other wanted : Declaration)
    (different : other.property ≠ target) (same : wanted.property = target)
    (full : sentinel ≤ n) :
    (build sentinel target empty (List.replicate n other ++ [wanted])).chain ≠
      fullProjection target 0 (List.replicate n other ++ [wanted]) := by
  rw [sole_target_admission sentinel target n other wanted different same,
    sole_target_projection target n other wanted different same]
  simp [show ¬n < sentinel by omega]

theorem early_target_preserved (sentinel target n : Nat) (other wanted : Declaration)
    (different : other.property ≠ target) (same : wanted.property = target)
    (nonzero : 0 < sentinel) :
    (build sentinel target empty (wanted :: List.replicate n other)).chain = [0] := by
  simp [build_chain, empty, admitted, same, nonzero,
    unrelated_admission sentinel target 1 n other different]

def font : Declaration := ⟨0, 37⟩
def color : Declaration := ⟨1, 0⟩
def u16Sentinel : Nat := 65535
def u32Sentinel : Nat := 4294967295

theorem widened_bound_repairs_old_boundary :
    (build u16Sentinel 0 empty (List.replicate u16Sentinel color ++ [font])).chain = [] ∧
    (build u32Sentinel 0 empty (List.replicate u16Sentinel color ++ [font])).chain = [u16Sentinel] := by
  rw [sole_target_admission u16Sentinel 0 u16Sentinel color font (by decide) rfl,
    sole_target_admission u32Sentinel 0 u16Sentinel color font (by decide) rfl]
  decide

theorem widened_bound_still_finite :
    (build u32Sentinel 0 empty (List.replicate u32Sentinel color ++ [font])).chain ≠
      fullProjection 0 0 (List.replicate u32Sentinel color ++ [font]) := by
  exact sole_target_lost u32Sentinel 0 u32Sentinel color font (by decide) rfl (by omega)

def headIndex (sentinel : Nat) (chain : List Nat) : Nat := chain.headD sentinel

def linkedEdges : List Nat → List (Nat × Nat)
  | [] => []
  | i :: rest => (i, rest.headD 0) :: linkedEdges rest

theorem zero_first_index_is_representable (sentinel : Nat) (nonzero : 0 < sentinel) :
    headIndex sentinel [0] ≠ sentinel ∧ linkedEdges [0] = [(0, 0)] := by
  simp [headIndex, linkedEdges]; omega

theorem fresh_link_not_end_marker (lastIndex newIndex : Nat) (later : lastIndex < newIndex) :
    newIndex ≠ 0 := by omega

end DeclarationCapacity
