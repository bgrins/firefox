import PublicationWitnesses
open InvalidPublication
namespace IndependentReview

def resetEnv : Environment Nat Nat Nat := ⟨fun _ => false, fun _ => some 20, id, id⟩
def inheritedEnv : Environment Nat Nat Nat := ⟨fun _ => true, fun _ => some 20, id, id⟩
def starting : State Nat Nat := ⟨fun _ _ => some 44, fun _ => false, false⟩
def lower : Entry Nat Nat Nat := ⟨7, .payload 55, true, true⟩

theorem excluded_flags_do_not_win :
    selected resetEnv (run resetEnv starting [⟨7, .invalid, true, false⟩, lower]) 7 = some 55 := rfl

theorem excluded_priority_does_not_win :
    selected resetEnv (run resetEnv starting [⟨7, .invalid, false, true⟩, lower]) 7 = some 55 := rfl

theorem missing_reset_seed_changes_original_result :
    selected resetEnv (step resetEnv starting (originalConvert id ⟨7, none⟩)) 7 = some 44 ∧
    selected resetEnv (step resetEnv starting (originalConvert id ⟨7, none⟩)) 7 ≠ resetEnv.initial 7 := by decide

theorem inherited_initial_does_not_need_reset_seed :
    selected inheritedEnv (step inheritedEnv starting (originalConvert id ⟨7, none⟩)) 7 = some 20 := rfl

def badCodec : Environment Nat Nat Nat := ⟨fun _ => false, fun _ => some 20, id, fun _ => 99⟩

theorem nonpreserving_codec_changes_valid_payload :
    selected badCodec (step badCodec starting (convert badCodec.encode ⟨7, some 44⟩)) 7 = some 99 ∧
    fromDeclaration badCodec (convert badCodec.encode ⟨7, some 44⟩) ≠ some ⟨7, some 44⟩ := by decide

theorem invalid_does_not_require_codec_preservation :
    selected badCodec (step badCodec starting (convert badCodec.encode ⟨7, none⟩)) 7 = none := rfl

def noInitial : Environment Nat Nat Nat := ⟨fun _ => true, fun _ => none, id, id⟩

theorem original_with_invalid_initial_is_not_a_counterexample :
    selected noInitial (step noInitial starting (originalConvert id ⟨7, none⟩)) 7 =
    selected noInitial (step noInitial starting (convert id ⟨7, none⟩)) 7 := rfl

theorem changing_registration_route_exposes_other_partition :
    selected inheritedEnv (step resetEnv starting (convert id ⟨7, none⟩)) 7 = some 44 ∧
    selected resetEnv (step resetEnv starting (convert id ⟨7, none⟩)) 7 = none := by decide

theorem foreign_suffix_may_change_cycles_but_not_invalidity :
    let result := run resetEnv starting [convert id ⟨7, none⟩, ⟨8, .provided (some 88) true, true, true⟩]
    selected resetEnv result 7 = none ∧ result.cycles = true ∧ selected resetEnv result 8 = some 88 := by decide

def parentValue : LiveCount.Store Nat Nat := ⟨[[], [(7, some 44)]], 1⟩

theorem unsound_comparator_defeats_shared_removal :
    LiveCount.lookup (LiveCount.doInsert false (fun _ _ => true) parentValue 7 none).chain 7 = some 44 := rfl

theorem removal_specialization_masks_parent :
    LiveCount.lookup (LiveCount.doInsert false removalCompare parentValue 7 none).chain 7 = none := rfl

theorem local_absence_and_tombstone_differ :
    LiveCount.lookup ([[], [(7, some 44)]] : LiveCount.Chain Nat Nat) 7 = some 44 ∧
    LiveCount.lookup ([[(7, none)], [(7, some 44)]] : LiveCount.Chain Nat Nat) 7 = none := by decide

theorem unready_count_is_not_repaired :
    (LiveCount.doInsert true removalCompare (⟨[[(7, some 44)]], 100⟩ : LiveCount.Store Nat Nat) 7 none).stored = 99 := rfl

theorem duplicate_roster_breaks_count_transition_without_uniqueness :
    LiveCount.count [7,7] ([[ (7, some 44) ]] : LiveCount.Chain Nat Nat) = 2 ∧
    LiveCount.count [7,7] (LiveCount.insert [[(7, some 44)]] 7 none) = 0 ∧
    LiveCount.updateCount 2 true false = 1 := by decide

end IndependentReview

#print axioms IndependentReview.excluded_flags_do_not_win
#print axioms IndependentReview.excluded_priority_does_not_win
#print axioms IndependentReview.missing_reset_seed_changes_original_result
#print axioms IndependentReview.inherited_initial_does_not_need_reset_seed
#print axioms IndependentReview.nonpreserving_codec_changes_valid_payload
#print axioms IndependentReview.invalid_does_not_require_codec_preservation
#print axioms IndependentReview.original_with_invalid_initial_is_not_a_counterexample
#print axioms IndependentReview.changing_registration_route_exposes_other_partition
#print axioms IndependentReview.foreign_suffix_may_change_cycles_but_not_invalidity
#print axioms IndependentReview.unsound_comparator_defeats_shared_removal
#print axioms IndependentReview.removal_specialization_masks_parent
#print axioms IndependentReview.local_absence_and_tombstone_differ
#print axioms IndependentReview.unready_count_is_not_repaired
#print axioms IndependentReview.duplicate_roster_breaks_count_transition_without_uniqueness
