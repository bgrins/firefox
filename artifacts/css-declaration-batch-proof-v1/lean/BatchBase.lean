import AllOrder
namespace BatchBase
open AllOrder
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]
local notation "E" => Entry ι ν

structure Comparator (ι ν : Type) where
  same : Entry ι ν → Entry ι ν → Bool
  sound : ∀ old new, same old new = true → old = new

def decideFound (cmp : Comparator ι ν) (old new : E) (seen : Bool) (pos : Nat) : Plan :=
  if seen then .move pos else if cmp.same old new then .none else .replace pos

def scan (cmp : Comparator ι ν) (op : ι → ι → Bool) (new : E) : Nat → List E → Search
  | _, [] => .pending false
  | n, old :: tail =>
    match scan cmp op new (n + 1) tail with
    | .found p => .found p
    | .pending seen =>
      if old.id = new.id then .found (decideFound cmp old new seen n)
      else .pending (op new.id old.id || seen)

def planner (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E) : Plan :=
  match scan cmp op new 0 xs with
  | .pending _ => .append
  | .found p => p


theorem scan_absent (cmp : Comparator ι ν) (op : ι → ι → Bool) (new : E) (xs : List E) (h : absent new.id xs)
    (n : Nat) : scan cmp op new n xs = .pending (xs.any (fun e => op new.id e.id)) := by
  induction xs generalizing n with
  | nil => rfl
  | cons old tail ih =>
    have ho := h old (by simp)
    have ht : absent new.id tail := by intro e he; exact h e (by simp [he])
    simp [scan, ih ht, ho]

theorem scan_prepend_found (cmp : Comparator ι ν) (op : ι → ι → Bool) (new : E) (pre tail : List E)
    (n : Nat) (p : Plan) (h : scan cmp op new (n + pre.length) tail = .found p) :
    scan cmp op new n (pre ++ tail) = .found p := by
  induction pre generalizing n with
  | nil => simpa using h
  | cons e pre ih =>
    have h' : scan cmp op new (n + 1 + pre.length) tail = .found p := by
      simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h
    simp [scan, ih (n + 1) h']

theorem scan_split (cmp : Comparator ι ν) (op : ι → ι → Bool) (new old : E) (pre post : List E)
    (h : old.id = new.id) (ha : absent new.id post) :
    scan cmp op new 0 (pre ++ old :: post) =
      .found (decideFound cmp old new (post.any (fun e => op new.id e.id)) pre.length) := by
  apply scan_prepend_found
  simp [scan, scan_absent cmp op new post ha, h]


theorem planner_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : execute xs new (planner cmp op xs new) = reference op xs new := by
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
  · simp [planner, scan_absent cmp op new xs ha, execute, reference_absent op new xs ha]
  · rw [reference_split op new old pre post hp he]
    simp only [planner, scan_split cmp op new old pre post he hs]
    unfold decideFound
    split
    · exact execute_split_move pre post old new
    · split
      · next h => have heq := cmp.sound old new h; subst old; rfl
      · exact execute_split_replace pre post old new



theorem planner_valid (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) : ValidPlan xs new (planner cmp op xs new) := by
  rcases unique_split xs new hu with ha | ⟨pre, old, post, rfl, he, hp, hs⟩
  · simp [planner, scan_absent cmp op new xs ha]; exact .append
  · simp only [planner, scan_split cmp op new old pre post he hs]
    unfold decideFound
    split
    · exact .move pre post old rfl he
    · split
      · exact .none
      · exact .replace pre post old rfl he

theorem planner_index_bounds (cmp : Comparator ι ν) (op : ι → ι → Bool) (xs : List E) (new : E)
    (hu : unique xs) (n : Nat)
    (h : planner cmp op xs new = .replace n ∨ planner cmp op xs new = .move n) : n < xs.length := by
  have hv := planner_valid cmp op xs new hu
  rcases h with h | h <;> rw [h] at hv <;> cases hv <;> simp_all


end BatchBase
