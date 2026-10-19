import Std

namespace LanguageBreak

inductive BreakKind where
  | none | normal | hyphen | emergency
  deriving DecidableEq, Repr

def BreakKind.available : BreakKind → Bool
  | .none => false
  | _ => true

structure Coordinate where
  owner : Nat
  offset : Nat
  deriving DecidableEq, Repr

structure Glyph where
  kind : BreakKind
  clusterStart : Bool
  precedingSpace : Bool
  deriving DecidableEq, Repr

def filterKind (g : Glyph) (incoming : BreakKind) : BreakKind :=
  if incoming.available && !g.clusterStart && !g.precedingSpace then .none
  else incoming

def merge (g : Glyph) (incoming : BreakKind) : Glyph :=
  match filterKind g incoming with
  | .none => g
  | value => { g with kind := value }

theorem zero_preserves (g : Glyph) : merge g .none = g := by
  simp [merge,filterKind,BreakKind.available]

theorem cluster_filter_preserves (g : Glyph) (incoming : BreakKind)
    (cluster : g.clusterStart = false) (space : g.precedingSpace = false) :
    merge g incoming = g := by
  cases incoming <;> simp [merge,filterKind,cluster,space,BreakKind.available]

theorem nonzero_replaces (g : Glyph) (incoming : BreakKind)
    (nonzero : incoming.available = true)
    (allowed : g.clusterStart = true ∨ g.precedingSpace = true) :
    (merge g incoming).kind = incoming := by
  cases incoming <;> simp_all [merge,filterKind,BreakKind.available]
  all_goals cases allowed <;> simp_all

theorem availability_preserved (g : Glyph) (incoming : BreakKind)
    (old : g.kind.available = true) : (merge g incoming).kind.available = true := by
  unfold merge
  split <;> simp_all [BreakKind.available]

def applyWrites (g : Glyph) (writes : List BreakKind) : Glyph := writes.foldl merge g

theorem finite_availability_preserved (g : Glyph) (writes : List BreakKind)
    (old : g.kind.available = true) : (applyWrites g writes).kind.available = true := by
  induction writes generalizing g with
  | nil => exact old
  | cons w ws ih => exact ih (merge g w) (availability_preserved g w old)

def applyAt (storage : Coordinate → Glyph) (address : Coordinate) (kind : BreakKind) : Coordinate → Glyph :=
  fun query => if query = address then merge (storage query) kind else storage query

theorem different_owner_preserved (storage : Coordinate → Glyph) (address query : Coordinate)
    (different : query.owner ≠ address.owner) (kind : BreakKind) :
    applyAt storage address kind query = storage query := by
  simp only [applyAt]
  split
  next same => exact False.elim (different (congrArg Coordinate.owner same))
  next _ => rfl

theorem different_offset_preserved (storage : Coordinate → Glyph) (address query : Coordinate)
    (different : query.offset ≠ address.offset) (kind : BreakKind) :
    applyAt storage address kind query = storage query := by
  simp only [applyAt]
  split
  next same => exact False.elim (different (congrArg Coordinate.offset same))
  next _ => rfl

structure Contribution where
  sourceOwner : Nat
  sinkOwner : Option Nat
  sinkOffset : Nat
  length : Nat
  deriving DecidableEq, Repr

def Contribution.coordinates (c : Contribution) : List Coordinate :=
  match c.sinkOwner with
  | none => []
  | some owner => (List.range c.length).map fun i => ⟨owner,c.sinkOffset+i⟩

theorem coordinates_in_range (c : Contribution) (q : Coordinate)
    (member : q ∈ c.coordinates) :
    c.sinkOwner = some q.owner ∧ c.sinkOffset ≤ q.offset ∧ q.offset < c.sinkOffset+c.length := by
  unfold Contribution.coordinates at member
  split at member
  next missing => simp at member
  next owner found =>
    simp only [List.mem_map,List.mem_range] at member
    obtain ⟨i,bound,rfl⟩ := member
    exact ⟨found,by change c.sinkOffset ≤ c.sinkOffset+i; omega,by change c.sinkOffset+i < c.sinkOffset+c.length; omega⟩

theorem coordinates_no_duplicates (c : Contribution) : c.coordinates.Nodup := by
  unfold Contribution.coordinates
  split
  next _ => exact List.nodup_nil
  next owner _ =>
    change List.Pairwise (· ≠ ·) _
    rw [List.pairwise_map]
    apply List.Pairwise.imp (R := fun x y : Nat => x ≠ y)
    · intro x y different equal
      apply different
      have h := congrArg Coordinate.offset equal
      change c.sinkOffset+x = c.sinkOffset+y at h
      omega
    · exact List.nodup_range

example : merge ⟨.emergency,true,false⟩ .normal = ⟨.normal,true,false⟩ := rfl
example : merge ⟨.emergency,true,false⟩ .none = ⟨.emergency,true,false⟩ := rfl

end LanguageBreak
