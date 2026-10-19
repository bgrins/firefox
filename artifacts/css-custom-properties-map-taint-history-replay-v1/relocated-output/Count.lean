import Std
set_option linter.unusedSectionVars false

namespace LiveCount

abbrev Entry (K V : Type) := K × Option V
abbrev Node (K V : Type) := List (Entry K V)
abbrev Chain (K V : Type) := List (Node K V)
variable {K V : Type} [DecidableEq K]

def ownFind : Node K V → K → Option (Option V)
  | [], _ => none
  | (key, value) :: rest, k => if key = k then some value else ownFind rest k

def lookup : Chain K V → K → Option V
  | [], _ => none
  | node :: parents, k => match ownFind node k with
    | some value => value
    | none => lookup parents k

def ownInsert : Node K V → K → Option V → Node K V
  | [], k, v => [(k, v)]
  | (key, value) :: rest, k, v =>
    if key = k then (k, v) :: rest else (key, value) :: ownInsert rest k v

def insert : Chain K V → K → Option V → Chain K V
  | [], k, v => [[(k, v)]]
  | node :: parents, k, v => ownInsert node k v :: parents

def nodeUnique (n : Node K V) : Prop := (n.map Prod.fst).Nodup
def valid (c : Chain K V) : Prop := ∀ n ∈ c, nodeUnique n

theorem own_find_insert (n : Node K V) (k q : K) (v : Option V) :
    ownFind (ownInsert n k v) q = if q = k then some v else ownFind n q := by
  induction n with
  | nil => by_cases h : q = k
           · subst q; simp [ownInsert, ownFind]
           · simp [ownInsert, ownFind, h, Ne.symm h]
  | cons e rest ih =>
    rcases e with ⟨key, value⟩
    by_cases h : key = k
    · subst key; by_cases hq : q = k
      · subst q; simp [ownInsert, ownFind]
      · simp [ownInsert, ownFind, hq, Ne.symm hq]
    · by_cases hq : q = k
      · subst q; simp [ownInsert, ownFind, h, ih]
      · by_cases he : key = q <;> simp [ownInsert, ownFind, h, hq, he, ih]

theorem lookup_insert (c : Chain K V) (k q : K) (v : Option V) :
    lookup (insert c k v) q = if q = k then v else lookup c q := by
  cases c with
  | nil => by_cases h : q = k
           · subst q; simp [insert, lookup, ownFind]
           · simp [insert, lookup, ownFind, h, Ne.symm h]
  | cons n ps =>
    simp only [insert, lookup, own_find_insert]
    by_cases h : q = k <;> simp [h]

theorem tombstone (n : Node K V) (parents : Chain K V) (k : K)
    (h : ownFind n k = some none) : lookup (n :: parents) k = none := by
  simp [lookup, h]

def tally (keys : List K) (f : K → Bool) : Nat :=
  (keys.filter f).length

def count (keys : List K) (c : Chain K V) : Nat :=
  tally keys (fun k => (lookup c k).isSome)

def projection (keys : List K) (c : Chain K V) : List (K × V) :=
  keys.filterMap (fun k => (lookup c k).map (fun v => (k, v)))

def bit (b : Bool) : Nat := if b then 1 else 0

def updateCount (n : Nat) (old new : Bool) : Nat :=
  match old, new with
  | false, true => n + 1
  | true, false => n - 1
  | _, _ => n

theorem tally_cons (k : K) (ks : List K) (f : K → Bool) :
    tally (k :: ks) f = bit (f k) + tally ks f := by
  cases h : f k <;> simp [tally, bit, h, Nat.add_comm]

theorem tally_congr (ks : List K) (f g : K → Bool)
    (h : ∀ k ∈ ks, f k = g k) : tally ks f = tally ks g := by
  unfold tally
  congr 1
  apply List.filter_congr
  exact h

theorem tally_update_balance (ks : List K) (k : K) (f : K → Bool) (b : Bool)
    (unique : ks.Nodup) (present : k ∈ ks) :
    tally ks (fun q => if q = k then b else f q) + bit (f k) =
      tally ks f + bit b := by
  induction ks with
  | nil => simp at present
  | cons a rest ih =>
    have u := List.nodup_cons.mp unique
    by_cases h : a = k
    · subst a
      have tail : tally rest (fun q => if q = k then b else f q) = tally rest f := by
        apply tally_congr
        intro q hq
        have ne : q ≠ k := by intro eq; subst q; exact u.1 hq
        simp [ne]
      rw [tally_cons, tally_cons, tail]
      simp
      omega
    · have hk : k ∈ rest := by simpa [Ne.symm h] using present
      have ihcount := ih u.2 hk
      rw [tally_cons, tally_cons]
      simp only [h, ↓reduceIte]
      omega

theorem tally_positive (ks : List K) (k : K) (f : K → Bool)
    (present : k ∈ ks) (yes : f k = true) : 0 < tally ks f := by
  have hm : k ∈ ks.filter f := by simp [present, yes]
  exact List.length_pos_of_mem hm

theorem count_transition (ks : List K) (c : Chain K V) (k : K) (v : Option V)
    (unique : ks.Nodup) (present : k ∈ ks) :
    count ks (insert c k v) = updateCount (count ks c) (lookup c k).isSome v.isSome := by
  have balance := tally_update_balance ks k (fun q => (lookup c q).isSome) v.isSome unique present
  have f : (fun q => (lookup (insert c k v) q).isSome) =
      (fun q => if q = k then v.isSome else (lookup c q).isSome) := by
    funext q; rw [lookup_insert]; split <;> rfl
  unfold count
  rw [f]
  cases old : (lookup c k).isSome <;> cases new : v.isSome <;>
    simp [updateCount, bit, old, new] at * <;> omega

theorem decrement_headroom (ks : List K) (c : Chain K V) (k : K)
    (present : k ∈ ks) (old : (lookup c k).isSome = true) : 0 < count ks c := by
  exact tally_positive ks k _ present old

theorem projection_length (ks : List K) (c : Chain K V) :
    (projection ks c).length = count ks c := by
  induction ks with
  | nil => simp [projection, count, tally]
  | cons k rest ih =>
    cases h : lookup c k <;> simp_all [projection, count, tally]

theorem empty_initialization (ks : List K) : count ks ([[]] : Chain K V) = 0 := by
  simp [count, tally, lookup, ownFind]

theorem expand_lookup (c : Chain K V) (k : K) : lookup ([] :: c) k = lookup c k := rfl

theorem expand_count (ks : List K) (c : Chain K V) : count ks ([] :: c) = count ks c := rfl

theorem tally_bound (ks : List K) (f : K → Bool) : tally ks f ≤ ks.length := by
  exact List.length_filter_le _ _

theorem tally_missing (ks : List K) (k : K) (f : K → Bool)
    (present : k ∈ ks) (no : f k = false) : tally ks f < ks.length := by
  induction ks with
  | nil => simp at present
  | cons a rest ih =>
    rw [tally_cons, List.length_cons]
    by_cases eq : a = k
    · subst a
      have bound := tally_bound rest f
      simp only [no, bit, Bool.false_eq_true, ↓reduceIte, Nat.zero_add]
      omega
    · have hk : k ∈ rest := by simpa [Ne.symm eq] using present
      have hr := ih hk
      cases f a <;> simp [bit] <;> omega

end LiveCount
