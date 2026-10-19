import Iterator

namespace MapIterator

variable {K V : Type} [DecidableEq K]

def ownFind (n : Node K V) (k : K) : Option (Entry K V) := n.find? (fun e => e.1 == k)

def nearest : Chain K V → K → Option (Entry K V)
  | [], _ => none
  | n :: ps, k => match ownFind n k with
    | some e => some e
    | none => nearest ps k

def lookupOwner (c : Chain K V) (k : K) : Option (Option V) :=
  (nearest c k).map Prod.snd

def nativeGet : Chain K V → K → Option V
  | [], _ => none
  | n :: ps, k => match ownFind n k with
    | some e => e.2
    | none => nativeGet ps k

def Unique (n : Node K V) : Prop := n.Pairwise (fun a b => a.1 ≠ b.1)
def Valid (c : Chain K V) : Prop := ∀ n ∈ c, Unique n

theorem ownFind_none (n : Node K V) (k : K) :
    ownFind n k = none ↔ owns n k = false := by
  simp [ownFind, owns, List.find?_eq_none, List.any_eq_false]

theorem filter_find (n xs : Node K V) (k : K) (h : owns n k = false) :
    ownFind (xs.filter (fun e => !owns n e.1)) k = ownFind xs k := by
  unfold ownFind
  rw [List.find?_filter]
  congr 1
  funext e
  by_cases he : e.1 = k <;> simp [he, h]

theorem reference_lookup (c : Chain K V) (k : K) :
    ownFind (reference c) k = nearest c k := by
  induction c with
  | nil => rfl
  | cons n ps ih =>
    unfold reference
    simp only [ownFind, List.find?_append]
    change (ownFind n k).or (ownFind ((reference ps).filter (fun e => !owns n e.1)) k) = nearest (n :: ps) k
    cases h : ownFind n k with
    | none =>
      simp only [nearest, h]
      rw [filter_find n _ k ((ownFind_none n k).mp h), ih]
      rfl
    | some e => simp [nearest, h]

theorem native_get_owner (c : Chain K V) (k : K) :
    nativeGet c k = (lookupOwner c k).join := by
  induction c with
  | nil => rfl
  | cons n ps ih => cases h : ownFind n k <;> simp_all [nativeGet, lookupOwner, nearest]

theorem contains_owns (e : Entry K V) (n : Node K V) (h : e ∈ n) : owns n e.1 = true := by
  simp only [owns, List.any_eq_true]
  exact ⟨e, h, by simp⟩

theorem reference_unique (c : Chain K V) (h : Valid c) : Unique (reference c) := by
  induction c with
  | nil => exact List.Pairwise.nil
  | cons n ps ih =>
    have hn : Unique n := h n (by simp)
    have hp : Valid ps := fun p hp => h p (by simp [hp])
    unfold reference Unique
    apply List.pairwise_append.mpr
    refine ⟨hn, (ih hp).filter _, ?_⟩
    intro a ha b hb he
    have hb' := (List.mem_filter.mp hb).2
    have ha' := contains_owns a n ha
    rw [he] at ha'
    simp_all

theorem iterator_keys_unique (c : Chain K V) (h : Valid c) :
    ((drain (start c)).map Prod.fst).Nodup := by
  rw [initialized_enumeration, List.nodup_iff_pairwise_ne, List.pairwise_map]
  exact reference_unique c h

theorem iterator_exact_owner (c : Chain K V) (k : K) :
    (ownFind (drain (start c)) k).map Prod.snd = lookupOwner c k := by
  rw [initialized_enumeration, reference_lookup]
  rfl

theorem iterator_exact_get (c : Chain K V) (k : K) :
    ((ownFind (drain (start c)) k).map Prod.snd).join = nativeGet c k := by
  rw [iterator_exact_owner, native_get_owner]

theorem unique_find_of_mem (n : Node K V) (e : Entry K V)
    (hu : Unique n) (he : e ∈ n) : ownFind n e.1 = some e := by
  induction n with
  | nil => simp at he
  | cons a rest ih =>
    have hp := List.pairwise_cons.mp hu
    rcases List.mem_cons.mp he with h | h
    · subst e; simp [ownFind]
    · have ne := hp.1 e h
      simpa [ownFind, ne] using ih hp.2 h

theorem emitted_nearest (c : Chain K V) (e : Entry K V)
    (hv : Valid c) (he : e ∈ drain (start c)) : nearest c e.1 = some e := by
  rw [initialized_enumeration] at he
  rw [← reference_lookup]
  exact unique_find_of_mem _ _ (reference_unique c hv) he

theorem tombstone_stops (n : Node K V) (ps : Chain K V) (k : K)
    (h : ownFind n k = some (k, none)) :
    lookupOwner (n :: ps) k = some none ∧ nativeGet (n :: ps) k = none := by
  simp [lookupOwner, nearest, nativeGet, h]

def getIndexRaw (c : Chain K V) (stored index : Nat) : Option (Entry K V) :=
  if index ≥ stored then none else (drain (start c))[index]?

theorem get_index_raw_exact (c : Chain K V) (stored index : Nat)
    (length_ready : stored = (reference c).length) :
    getIndexRaw c stored index = (reference c)[index]? := by
  unfold getIndexRaw
  rw [initialized_enumeration]
  split
  · symm; apply List.getElem?_eq_none; omega
  · rfl

theorem get_index_raw_out_of_range (c : Chain K V) (stored index : Nat)
    (h : stored ≤ index) : getIndexRaw c stored index = none := by
  simp [getIndexRaw, h]

theorem get_index_raw_in_range (c : Chain K V) (stored index : Nat)
    (length_ready : stored = (reference c).length) (h : index < stored) :
    ∃ e, getIndexRaw c stored index = some e := by
  rw [get_index_raw_exact c stored index length_ready]
  exact ⟨(reference c)[index]'(by omega), List.getElem?_eq_getElem (by omega)⟩

def live (n : Node K V) : Node K V := n.filter (fun e => e.2.isSome)

def getIndex (c : Chain K V) (stored index : Nat) : Option (Entry K V) :=
  if index ≥ stored then none else (live (drain (start c)))[index]?

theorem live_enumeration (c : Chain K V) :
    live (drain (start c)) = live (reference c) := by
  rw [initialized_enumeration]

theorem live_unique (c : Chain K V) (h : Valid c) :
    Unique (live (drain (start c))) := by
  rw [live_enumeration]
  exact (reference_unique c h).filter _

omit [DecidableEq K] in
theorem live_has_value (e : Entry K V) (n : Node K V) (h : e ∈ live n) :
    ∃ v, e.2 = some v := by
  have hv := (List.mem_filter.mp h).2
  cases he : e.2 with
  | none => simp [he] at hv
  | some v => exact ⟨v, rfl⟩

theorem get_index_exact (c : Chain K V) (stored index : Nat)
    (live_count_ready : stored = (live (reference c)).length) :
    getIndex c stored index = (live (reference c))[index]? := by
  unfold getIndex
  rw [live_enumeration]
  split
  · symm; apply List.getElem?_eq_none; omega
  · rfl

theorem get_index_in_range (c : Chain K V) (stored index : Nat)
    (live_count_ready : stored = (live (reference c)).length) (h : index < stored) :
    ∃ e, getIndex c stored index = some e := by
  rw [get_index_exact c stored index live_count_ready]
  exact ⟨(live (reference c))[index]'(by omega), List.getElem?_eq_getElem (by omega)⟩

theorem get_index_out_of_range (c : Chain K V) (stored index : Nat)
    (h : stored ≤ index) : getIndex c stored index = none := by
  simp [getIndex, h]

end MapIterator
