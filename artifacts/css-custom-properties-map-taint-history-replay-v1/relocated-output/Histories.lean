import Composition
namespace MapComposition
variable {K V : Type} [DecidableEq K]

theorem index_keys_unique (c : LiveCount.Chain K V) (stored i j : Nat)
    (e f : LiveCount.Entry K V) (valid : LiveCount.valid c)
    (a : MapIterator.getIndex c stored i = some e)
    (b : MapIterator.getIndex c stored j = some f) (same : e.1 = f.1) : i = j := by
  have nodup : ((MapIterator.live (MapIterator.drain (MapIterator.start c))).map Prod.fst).Nodup := by
    rw [List.nodup_iff_pairwise_ne, List.pairwise_map]
    exact MapIterator.live_unique c ((valid_bridge c).mpr valid)
  have ai : (MapIterator.live (MapIterator.drain (MapIterator.start c)))[i]? = some e := by
    unfold MapIterator.getIndex at a; split at a
    · contradiction
    · exact a
  have bj : (MapIterator.live (MapIterator.drain (MapIterator.start c)))[j]? = some f := by
    unfold MapIterator.getIndex at b; split at b
    · contradiction
    · exact b
  have ki : ((MapIterator.live (MapIterator.drain (MapIterator.start c))).map Prod.fst)[i]? = some e.1 := by
    rw [List.getElem?_map, ai]; rfl
  have kj : ((MapIterator.live (MapIterator.drain (MapIterator.start c))).map Prod.fst)[j]? = some f.1 := by
    rw [List.getElem?_map, bj]; rfl
  obtain ⟨hi, _⟩ := List.getElem?_eq_some_iff.mp ki
  apply (List.Nodup.getElem?_inj hi nodup).mp
  rw [ki, kj, same]

theorem history_raw_enumeration (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) :
    let s := LiveCount.run compare LiveCount.initial ops
    LiveCount.RawEnumeration s.chain (MapIterator.drain (MapIterator.start s.chain)) :=
  raw_enumeration _ (LiveCount.finite_history ops compare).2.2

theorem history_live_count (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) :
    let s := LiveCount.run compare LiveCount.initial ops
    s.stored = (MapIterator.live (MapIterator.drain (MapIterator.start s.chain))).length :=
  ready_live_count _ _ (LiveCount.dedup_unique _) (LiveCount.finite_history ops compare)

theorem history_index_exact (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (index : Nat) :
    let s := LiveCount.run compare LiveCount.initial ops
    MapIterator.getIndex s.chain s.stored index = (MapIterator.live (MapIterator.reference s.chain))[index]? :=
  ready_index_exact _ _ _ (LiveCount.dedup_unique _) (LiveCount.finite_history ops compare)

theorem history_index_in_bounds (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (index : Nat)
    (bound : index < (LiveCount.run compare LiveCount.initial ops).stored) :
    let s := LiveCount.run compare LiveCount.initial ops
    ∃ e, MapIterator.getIndex s.chain s.stored index = some e :=
  ready_index_in_bounds _ _ _ (LiveCount.dedup_unique _) (LiveCount.finite_history ops compare) bound

theorem history_index_out_of_bounds (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (index : Nat)
    (bound : (LiveCount.run compare LiveCount.initial ops).stored ≤ index) :
    let s := LiveCount.run compare LiveCount.initial ops
    MapIterator.getIndex s.chain s.stored index = none :=
  MapIterator.get_index_out_of_range _ _ _ bound

theorem history_index_owner (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (index : Nat) (k : K) (v : Option V)
    (returned : let s := LiveCount.run compare LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored index = some (k,v)) :
    let s := LiveCount.run compare LiveCount.initial ops
    ∃ value, v = some value ∧ LiveCount.owner s.chain k = some (some value) ∧
      LiveCount.lookup s.chain k = some value :=
  index_value _ _ _ (LiveCount.finite_history ops compare) _ _ returned

theorem history_index_keys_unique (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (i j : Nat) (e f : LiveCount.Entry K V)
    (a : let s := LiveCount.run compare LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored i = some e)
    (b : let s := LiveCount.run compare LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored j = some f) (same : e.1 = f.1) : i = j :=
  index_keys_unique _ _ _ _ _ _ (LiveCount.finite_history ops compare).2.2 a b same

theorem history_value_reference (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (sound : LiveCount.CompareSound compare)
    (index : Nat) (k : K) (v : V)
    (returned : let s := LiveCount.run compare LiveCount.initial ops
      MapIterator.getIndex s.chain s.stored index = some (k,some v)) :
    LiveCount.referenceRun (fun _ => none) ops k = some v := by
  obtain ⟨value, eq, _, lookup⟩ := history_index_owner ops compare index k (some v) returned
  have same : v = value := Option.some.inj eq
  subst value
  rw [LiveCount.history_lookup ops LiveCount.initial compare sound k] at lookup
  simpa [LiveCount.initial, LiveCount.lookup, LiveCount.ownFind] using lookup

theorem every_prefix_count (ops : List (LiveCount.Op K V))
    (compare : Option V → Option V → Bool) (n : Nat) :
    let s := LiveCount.run compare LiveCount.initial (ops.take n)
    s.stored = (MapIterator.live (MapIterator.drain (MapIterator.start s.chain))).length :=
  history_live_count (ops.take n) compare

end MapComposition
