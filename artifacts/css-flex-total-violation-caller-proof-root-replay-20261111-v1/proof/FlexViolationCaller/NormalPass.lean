import FlexViolationCaller.Mapping

namespace FlexViolationCaller

def normalizedPass (iteration : Nat) (line : Line) (values : List Int) : Pass :=
  let xs := suppliedItems line.items values
  let clamped := xs.map clampOne
  let total := FlexViolation.total ((active xs).map asItem)
  let finish := finishOne (FlexViolation.kind total) (iteration + 1 == line.items.length)
  let helper : Walk := ⟨clamped.map finish, 0, newCount finish clamped, 0,
    clamped.any (fellBack (FlexViolation.kind total) (iteration + 1 == line.items.length))⟩
  ⟨⟨xs,line.frozenCount⟩, ⟨clamped,0,0,total,false⟩, helper,
    ⟨helper.items,line.frozenCount + helper.newlyFrozen⟩⟩

theorem prepared_active_length (line : Line) (values : List Int)
    (hv : ProviderValid line values) :
    (active (suppliedItems line.items values)).length = (active line.items).length := by
  have hf := supplied_frame line.items values hv.1
  have hn := aligned_length hf
  have hc := frame_count hf
  have h1 := count_partition line.items
  have h2 := count_partition (suppliedItems line.items values)
  omega

theorem normalized_exact (iteration : Nat) (line : Line) (values : List Int)
    (hc : CountAgrees line) (hv : ProviderValid line values) :
    runPass iteration line values = some (normalizedPass iteration line values) := by
  have hp := count_partition line.items
  have ha := prepared_active_length line values hv
  have he : line.items.length - line.frozenCount =
      (active (suppliedItems line.items values)).length := by
    unfold CountAgrees at hc
    omega
  have hm := active_map_length clampOne (suppliedItems line.items values) clamp_frozen
  unfold runPass
  rw [prepare_exact line values hv]
  change (let prepared : Line := ⟨suppliedItems line.items values, line.frozenCount⟩
    let left := line.items.length - line.frozenCount
    let c := clampWalk left 0 prepared.items
    let h := freezeWalk (FlexViolation.kind c.violation)
      (iteration + 1 == line.items.length) left c.items
    some (Pass.mk prepared c h ⟨h.items, line.frozenCount + h.newlyFrozen⟩)) = _
  dsimp only
  rw [he, clamp_walk_exact]
  simp only [Int.zero_add]
  rw [← hm, freeze_walk_exact]
  rfl

theorem normalized_properties (iteration : Nat) (line : Line) (values : List Int)
    (hl : LineValid line) (hv : ProviderValid line values) :
    FrozenPreserved line.items (normalizedPass iteration line values).after.items ∧
    LineValid (normalizedPass iteration line values).after ∧
    line.frozenCount ≤ (normalizedPass iteration line values).after.frozenCount := by
  let xs := suppliedItems line.items values
  let choice := FlexViolation.kind (FlexViolation.total ((active xs).map asItem))
  let final := iteration + 1 == line.items.length
  let finish := finishOne choice final
  have hr := prepare_ready line values hl hv
  have hp := frozen_trans (frame_frozen hr.1) (clamp_preserves xs)
  have hfin := finish_preserves choice final (xs.map clampOne)
  refine ⟨frozen_trans hp hfin, ?_, ?_⟩
  · refine ⟨?_, finish_fresh choice final (xs.map clampOne), ?_⟩
    · change line.frozenCount + newCount finish (xs.map clampOne) =
        countedFrozen ((xs.map clampOne).map finish)
      rw [newCount_partition finish (xs.map clampOne) (finish_frozen choice final),
        count_map_same clampOne xs clamp_frozen, ← frame_count hr.1]
      rw [hl.1]
    · intro item hi
      obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
      exact finish_bounded choice final before (clamp_list_bounded xs hr.2 before hb)
  · change line.frozenCount ≤ line.frozenCount + _
    omega

theorem normalized_progress (iteration : Nat) (line : Line) (values : List Int)
    (hl : LineValid line) (hv : ProviderValid line values)
    (hn : line.items.length ≤ FlexViolation.maxCount) :
    remaining (normalizedPass iteration line values).after ≤ remaining line ∧
    (0 < remaining line → remaining (normalizedPass iteration line values).after < remaining line) := by
  have hr := prepare_ready line values hl hv
  have hlen := aligned_length hr.1
  have hprop := normalized_properties iteration line values hl hv
  have hafterlen := aligned_length hprop.1
  have hp := count_partition line.items
  have hp' := count_partition (normalizedPass iteration line values).after.items
  have hc := hl.1
  have hc' := hprop.2.1.1
  unfold CountAgrees at hc hc'
  unfold remaining
  constructor
  · omega
  · intro hnz
    have hactive := prepared_active_length line values hv
    have hnew := finish_progress (suppliedItems line.items values)
      (iteration + 1 == line.items.length) (by omega) hr.2 (by omega)
    have hcount : (normalizedPass iteration line values).after.frozenCount =
        line.frozenCount + newCount
          (finishOne (FlexViolation.kind (FlexViolation.total
            ((active (suppliedItems line.items values)).map asItem)))
            (iteration + 1 == line.items.length))
          ((suppliedItems line.items values).map clampOne) := rfl
    omega

end FlexViolationCaller
