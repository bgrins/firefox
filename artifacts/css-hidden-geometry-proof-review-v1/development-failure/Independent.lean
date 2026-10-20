import Hidden

namespace Independent
open Hidden

def oldKey : Key := { key 32 with computed := ⟨100, 32⟩ }
def narrowKey : Key := { oldKey with computed := ⟨50, 32⟩ }
def prior : Frame := ⟨false, ⟨100, 32⟩, some ⟨oldKey, 32⟩⟩

theorem original_field_miss :
    narrowKey.containingBlock = oldKey.containingBlock ∧
    narrowKey.borderBStart = oldKey.borderBStart ∧
    canReuse narrowKey prior = false := by decide

theorem original_field_zero_stable :
    let damaged := (measure false true fixedBlock narrowKey prior).frame
    damaged.geometry = zero ∧ damaged.dirty = false ∧
    geometryQuery true fixedBlock narrowKey damaged = damaged := by decide

theorem original_field_direct_recovery :
    let damaged := (measure true true fixedBlock narrowKey prior).frame
    damaged.geometry = zero ∧ damaged.dirty = true ∧
    (geometryQuery true fixedBlock narrowKey damaged).geometry = ⟨50, 32⟩ := by decide

theorem output_not_desired_geometry :
    let damaged := (measure true true (fun _ => zero) narrowKey prior).frame
    (geometryQuery true (fun _ => zero) narrowKey damaged).geometry = zero ∧
    (geometryQuery true (fun _ => zero) narrowKey damaged).geometry ≠ fixedBlock narrowKey := by decide

theorem dirty_without_hidden_ancestor_stays_unrecovered :
    let damaged := (measure true true fixedBlock narrowKey prior).frame
    geometryQuery false fixedBlock narrowKey damaged = damaged ∧
    damaged.geometry = zero := by decide

theorem clean_descendant_retains_old_width (flush : TwoFrames → TwoFrames) :
    let state : TwoFrames := ⟨(measure true true fixedBlock narrowKey prior).frame, prior⟩
    state.measured.dirty = true ∧
    (descendantQuery flush state).descendant.geometry = ⟨100, 32⟩ := by
  simp [descendantQuery, measure, canReuse, prior, oldKey, narrowKey, key]

theorem same_key_invalid_geometry_is_not_repaired :
    let stale : Frame := { prior with geometry := zero }
    (measure true true fixedBlock oldKey stale).reused = true ∧
    (measure true true fixedBlock oldKey stale).frame = stale ∧
    geometryQuery true fixedBlock oldKey stale = stale := by decide

theorem changed_provider_clean_query_retains_previous_output :
    let damaged := (measure true true fixedBlock narrowKey prior).frame
    let recovered := geometryQuery true fixedBlock narrowKey damaged
    (geometryQuery true (fun _ => ⟨80, 99⟩) narrowKey recovered).geometry = ⟨50, 32⟩ := by decide

theorem arbitrary_provider_and_forced_key (layout : Key → Size)
    (next : Key) :
    (geometryQuery true layout next
      (measure true true layout narrowKey prior).frame).geometry = layout next := by
  apply repaired_hidden_miss_recovers
  decide

end Independent

#print axioms Independent.original_field_miss
#print axioms Independent.original_field_zero_stable
#print axioms Independent.original_field_direct_recovery
#print axioms Independent.output_not_desired_geometry
#print axioms Independent.dirty_without_hidden_ancestor_stays_unrecovered
#print axioms Independent.clean_descendant_retains_old_width
#print axioms Independent.same_key_invalid_geometry_is_not_repaired
#print axioms Independent.changed_provider_clean_query_retains_previous_output
#print axioms Independent.arbitrary_provider_and_forced_key
