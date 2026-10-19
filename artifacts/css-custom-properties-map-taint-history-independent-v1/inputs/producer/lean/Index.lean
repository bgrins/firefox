import Cow
namespace LiveCount
variable {K V : Type} [DecidableEq K]

def owner : Chain K V → K → Option (Option V)
  | [], _ => none
  | node :: parents, k => match ownFind node k with
    | some value => some value
    | none => owner parents k

theorem owner_lookup (c : Chain K V) (k : K) : (owner c k).join = lookup c k := by
  induction c with
  | nil => rfl
  | cons n ps ih => cases h : ownFind n k <;> simp_all [owner, lookup]

def RawEnumeration (c : Chain K V) (raw : Node K V) : Prop :=
  (raw.map Prod.fst).Nodup ∧ ∀ k v, (k, v) ∈ raw ↔ owner c k = some v

def liveRows (raw : Node K V) : Node K V := raw.filter (fun e => e.2.isSome)

theorem live_keys_member (c : Chain K V) (raw : Node K V) (k : K)
    (h : RawEnumeration c raw) :
    k ∈ (liveRows raw).map Prod.fst ↔ (lookup c k).isSome = true := by
  constructor
  · intro hm
    rcases List.mem_map.mp hm with ⟨⟨key,v⟩, he, eq⟩
    simp only at eq; subst key
    have hf := List.mem_filter.mp he
    have ho := (h.2 k v).mp hf.1
    have hl := owner_lookup c k
    rw [ho] at hl
    simp only [Option.join_some] at hl
    simpa [hl] using hf.2
  · intro yes
    cases ho : owner c k with
    | none =>
      have hl := owner_lookup c k
      rw [ho] at hl
      rw [← hl] at yes
      contradiction
    | some v =>
      have hl := owner_lookup c k
      rw [ho] at hl
      simp only [Option.join_some] at hl
      apply List.mem_map.mpr
      refine ⟨(k,v), List.mem_filter.mpr ⟨(h.2 k v).mpr ho, ?_⟩, rfl⟩
      simpa [hl] using yes

theorem filtered_count (ks : List K) (c : Chain K V) (raw : Node K V)
    (unique : ks.Nodup) (cover : covers ks c) (h : RawEnumeration c raw) :
    (liveRows raw).length = count ks c := by
  have rawUnique : ((liveRows raw).map Prod.fst).Nodup :=
    (List.filter_sublist.map Prod.fst).nodup h.1
  have refUnique : ((projection ks c).map Prod.fst).Nodup := projection_unique ks c unique
  have perm : ((liveRows raw).map Prod.fst).Perm ((projection ks c).map Prod.fst) := by
    apply (List.perm_ext_iff_of_nodup rawUnique refUnique).mpr
    intro k
    rw [live_keys_member c raw k h, projection_keys, List.mem_filter]
    constructor
    · intro yes
      cases val : lookup c k with
      | none => simp [val] at yes
      | some v => exact ⟨cover k (lookup_key c k v val), rfl⟩
    · exact fun pair => pair.2
  have lengths := perm.length_eq
  simp only [List.length_map] at lengths
  rw [projection_length] at lengths
  exact lengths

def getIndex (raw : Node K V) (stored index : Nat) : Option (Entry K V) :=
  if stored ≤ index then none else (liveRows raw)[index]?

theorem filtered_index_exact (ks : List K) (s : Store K V) (raw : Node K V) (index : Nat)
    (unique : ks.Nodup) (ready : Ready ks s) (h : RawEnumeration s.chain raw) :
    getIndex raw s.stored index = (liveRows raw)[index]? := by
  unfold getIndex
  split
  · symm; apply List.getElem?_eq_none
    rw [filtered_count ks s.chain raw unique ready.2.1 h, ← ready.1]
    assumption
  · rfl

theorem filtered_index_in_bounds (ks : List K) (s : Store K V) (raw : Node K V) (index : Nat)
    (unique : ks.Nodup) (ready : Ready ks s) (h : RawEnumeration s.chain raw)
    (bound : index < s.stored) : ∃ e, getIndex raw s.stored index = some e := by
  rw [filtered_index_exact ks s raw index unique ready h]
  have hi : index < (liveRows raw).length := by
    rw [filtered_count ks s.chain raw unique ready.2.1 h, ← ready.1]; exact bound
  exact ⟨(liveRows raw)[index]'hi, List.getElem?_eq_getElem hi⟩

omit [DecidableEq K] in
theorem index_out_of_bounds (raw : Node K V) (stored index : Nat) (h : stored ≤ index) :
    getIndex raw stored index = none := by simp [getIndex, h]

omit [DecidableEq K] in
theorem published_value_present (raw : Node K V) (stored index : Nat) (e : Entry K V)
    (h : getIndex raw stored index = some e) : e.2.isSome = true := by
  unfold getIndex at h
  split at h
  · contradiction
  · have he : e ∈ liveRows raw := List.mem_of_getElem? h
    exact (List.mem_filter.mp he).2

end LiveCount
