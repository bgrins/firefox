import CursorHistory
import Index

namespace MapComposition
variable {K V : Type} [DecidableEq K]

theorem own_find_entry (n : LiveCount.Node K V) (k : K) :
    MapIterator.ownFind n k = (LiveCount.ownFind n k).map (fun v => (k,v)) := by
  induction n with
  | nil => rfl
  | cons e rest ih =>
    rcases e with ⟨key,value⟩
    by_cases h : key = k
    · subst key; simp [MapIterator.ownFind, LiveCount.ownFind]
    · simpa [MapIterator.ownFind, LiveCount.ownFind, h] using ih

theorem own_find_payload (n : LiveCount.Node K V) (k : K) :
    (MapIterator.ownFind n k).map Prod.snd = LiveCount.ownFind n k := by
  rw [own_find_entry]
  cases LiveCount.ownFind n k <;> rfl

theorem nearest_entry (c : LiveCount.Chain K V) (k : K) :
    MapIterator.nearest c k = (LiveCount.owner c k).map (fun v => (k,v)) := by
  induction c with
  | nil => rfl
  | cons n ps ih =>
    simp only [MapIterator.nearest, own_find_entry, LiveCount.owner]
    cases LiveCount.ownFind n k <;> simp_all

theorem owner_bridge (c : LiveCount.Chain K V) (k : K) :
    MapIterator.lookupOwner c k = LiveCount.owner c k := by
  unfold MapIterator.lookupOwner
  rw [nearest_entry]
  cases LiveCount.owner c k <;> rfl

theorem lookup_bridge (c : LiveCount.Chain K V) (k : K) :
    MapIterator.nativeGet c k = LiveCount.lookup c k := by
  rw [MapIterator.native_get_owner, owner_bridge, LiveCount.owner_lookup]

omit [DecidableEq K] in
theorem valid_bridge (c : LiveCount.Chain K V) :
    MapIterator.Valid c ↔ LiveCount.valid c := by
  simp only [MapIterator.Valid, MapIterator.Unique, LiveCount.valid,
    LiveCount.nodeUnique, List.nodup_iff_pairwise_ne, List.pairwise_map]

theorem emitted_membership (c : LiveCount.Chain K V) (k : K) (v : Option V)
    (valid : LiveCount.valid c) :
    (k,v) ∈ MapIterator.drain (MapIterator.start c) ↔ LiveCount.owner c k = some v := by
  constructor
  · intro he
    have hn := MapIterator.emitted_nearest c (k,v) ((valid_bridge c).mpr valid) he
    rw [nearest_entry] at hn
    cases h : LiveCount.owner c k <;> simp_all
  · intro ho
    have hn : MapIterator.nearest c k = some (k,v) := by rw [nearest_entry, ho]; rfl
    rw [← MapIterator.reference_lookup] at hn
    rw [MapIterator.initialized_enumeration]
    exact List.mem_of_find?_eq_some hn

theorem raw_enumeration (c : LiveCount.Chain K V) (valid : LiveCount.valid c) :
    LiveCount.RawEnumeration c (MapIterator.drain (MapIterator.start c)) := by
  exact ⟨MapIterator.iterator_keys_unique c ((valid_bridge c).mpr valid),
    fun k v => emitted_membership c k v valid⟩

theorem ready_live_count (ks : List K) (s : LiveCount.Store K V)
    (unique : ks.Nodup) (ready : LiveCount.Ready ks s) :
    s.stored = (MapIterator.live (MapIterator.drain (MapIterator.start s.chain))).length := by
  rw [ready.1]
  exact (LiveCount.filtered_count ks s.chain _ unique ready.2.1
    (raw_enumeration s.chain ready.2.2)).symm

theorem ready_reference_count (ks : List K) (s : LiveCount.Store K V)
    (unique : ks.Nodup) (ready : LiveCount.Ready ks s) :
    s.stored = (MapIterator.live (MapIterator.reference s.chain)).length := by
  rw [← MapIterator.live_enumeration]
  exact ready_live_count ks s unique ready

theorem getter_bridge (c : LiveCount.Chain K V) (stored index : Nat) :
    MapIterator.getIndex c stored index =
      LiveCount.getIndex (MapIterator.drain (MapIterator.start c)) stored index := rfl

theorem ready_index_exact (ks : List K) (s : LiveCount.Store K V) (index : Nat)
    (unique : ks.Nodup) (ready : LiveCount.Ready ks s) :
    MapIterator.getIndex s.chain s.stored index = (MapIterator.live (MapIterator.reference s.chain))[index]? :=
  MapIterator.get_index_exact s.chain s.stored index (ready_reference_count ks s unique ready)

theorem ready_index_in_bounds (ks : List K) (s : LiveCount.Store K V) (index : Nat)
    (unique : ks.Nodup) (ready : LiveCount.Ready ks s) (bound : index < s.stored) :
    ∃ e, MapIterator.getIndex s.chain s.stored index = some e :=
  MapIterator.get_index_in_range s.chain s.stored index (ready_reference_count ks s unique ready) bound

theorem ready_live_unique (ks : List K) (s : LiveCount.Store K V)
    (ready : LiveCount.Ready ks s) :
    MapIterator.Unique (MapIterator.live (MapIterator.drain (MapIterator.start s.chain))) :=
  MapIterator.live_unique s.chain ((valid_bridge s.chain).mpr ready.2.2)

theorem index_value (ks : List K) (s : LiveCount.Store K V) (index : Nat)
    (ready : LiveCount.Ready ks s) (k : K) (v : Option V)
    (returned : MapIterator.getIndex s.chain s.stored index = some (k,v)) :
    ∃ value, v = some value ∧ LiveCount.owner s.chain k = some (some value) ∧
      LiveCount.lookup s.chain k = some value := by
  have present := LiveCount.published_value_present _ _ _ _
    ((getter_bridge s.chain s.stored index).symm ▸ returned)
  have member : (k,v) ∈ MapIterator.live (MapIterator.drain (MapIterator.start s.chain)) := by
    unfold MapIterator.getIndex at returned
    split at returned
    · contradiction
    · exact List.mem_of_getElem? returned
  have owner := (emitted_membership s.chain k v ready.2.2).mp (List.mem_filter.mp member).1
  cases hv : v with
  | none => simp [hv] at present
  | some value =>
    simp only [hv] at owner
    refine ⟨value, rfl, owner, ?_⟩
    have hl := LiveCount.owner_lookup s.chain k
    rw [owner] at hl
    exact hl.symm

end MapComposition
