import TabSpacingAdmission

namespace HyphenTabCacheConstruction

open HyphenTabSpacingAdmission

def collect (isTab : Nat → Bool) (first finish : Nat) : List Nat :=
  if active : first < finish then
    if isTab first then first::collect isTab (first+1) finish
    else collect isTab (first+1) finish
  else []
termination_by finish-first

theorem collected_bounds (isTab : Nat → Bool) (first finish : Nat) :
    ∀ offset ∈ collect isTab first finish, first ≤ offset ∧ offset < finish := by
  rw [collect]
  split
  next active =>
    have tailBounds := collected_bounds isTab (first+1) finish
    split
    next tab =>
      intro offset member
      rcases List.mem_cons.mp member with same | later
      · subst offset; omega
      · have old := tailBounds offset later; omega
    next ordinary =>
      intro offset member
      have old := tailBounds offset member
      omega
  next stopped => simp
termination_by finish-first

theorem collected_order (isTab : Nat → Bool) (first finish : Nat) :
    (collect isTab first finish).Pairwise (· < ·) := by
  rw [collect]
  split
  next active =>
    have tailOrder := collected_order isTab (first+1) finish
    split
    next tab =>
      apply List.pairwise_cons.mpr
      exact ⟨by intro offset member; have bound := collected_bounds isTab (first+1) finish offset member; omega,tailOrder⟩
    next ordinary => exact tailOrder
  next stopped => exact List.Pairwise.nil
termination_by finish-first

structure Cache where
  offsets : List Nat
  limit : Nat
  deriving DecidableEq, Repr

def Ready (cache : Cache) : Prop :=
  cache.offsets.Pairwise (· < ·) ∧ ∀ offset ∈ cache.offsets, offset < cache.limit

def extend (isTab : Nat → Bool) (cache : Cache) (finish : Nat) : Cache :=
  if cache.limit < finish then
    ⟨cache.offsets++collect isTab cache.limit finish,finish⟩
  else cache

theorem empty_ready : Ready ⟨[],0⟩ := by simp [Ready]

theorem extended_ready (isTab : Nat → Bool) (cache : Cache) (finish : Nat) (ready : Ready cache) :
    Ready (extend isTab cache finish) := by
  unfold extend
  split
  next active =>
    refine ⟨List.pairwise_append.mpr ⟨ready.1,collected_order isTab cache.limit finish,?_⟩,?_⟩
    · intro old oldMember new newMember
      have oldBound := ready.2 old oldMember
      have newBound := collected_bounds isTab cache.limit finish new newMember
      omega
    · intro offset member
      change offset < finish
      rcases List.mem_append.mp member with old | new
      · have bound := ready.2 offset old; omega
      · exact (collected_bounds isTab cache.limit finish offset new).2
  next unchanged => exact ready

def rebuilds (isTab : Nat → Bool) (cache : Cache) : List Nat → Cache
  | [] => cache
  | finish::rest => rebuilds isTab (extend isTab cache finish) rest

theorem arbitrary_extensions_ready (isTab : Nat → Bool) (cache : Cache) (ends : List Nat)
    (ready : Ready cache) : Ready (rebuilds isTab cache ends) := by
  induction ends generalizing cache with
  | nil => exact ready
  | cons finish rest ih => exact ih (extend isTab cache finish) (extended_ready isTab cache finish ready)

theorem ready_strict (cache : Cache) (ready : Ready cache) :
    Strict (fun index => cache.offsets[index]?.getD 0) cache.offsets.length := by
  intro first second order bound
  have firstBound : first < cache.offsets.length := by omega
  have values := List.pairwise_iff_getElem.mp ready.1 first second firstBound bound order
  simpa [List.getElem?_eq_getElem firstBound,List.getElem?_eq_getElem bound] using values

theorem ready_sorted (cache : Cache) (ready : Ready cache) : cache.offsets.Pairwise (· ≤ ·) :=
  ready.1.imp (by intro a b smaller; omega)

theorem constructed_tab_write_bounds (isTab : Nat → Bool) (ends : List Nat) (offset length : Nat) :
    let cache := rebuilds isTab ⟨[],0⟩ ends
    let first := if offset = 0 then 0 else
      binarySearch (fun i => cache.offsets[i]?.getD 0) offset 0 cache.offsets.length
    ∀ index ∈ applyOffsets offset length (cache.offsets.drop first), index < length := by
  dsimp only
  have ready := arbitrary_extensions_ready isTab ⟨[],0⟩ ends empty_ready
  exact native_tab_write_bounds _ offset length (ready_sorted _ ready) (ready_strict _ ready)

end HyphenTabCacheConstruction
