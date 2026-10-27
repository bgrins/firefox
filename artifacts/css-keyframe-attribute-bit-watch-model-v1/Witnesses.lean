import Bits

namespace AttributeWatchBits

def missingEntry : AttributeWatches.Entry := ⟨7, 5, [⟨11, none⟩]⟩
def otherEntry : AttributeWatches.Entry := ⟨7, 5, [⟨12, some 5⟩]⟩
def absentHistory : List AttributeWatches.Event := [.install 1 missingEntry, .change 7 11]
def sharedHistory : List AttributeWatches.Event :=
  [.install 1 missingEntry, .install 2 otherEntry, .remove 1, .change 7 12]
def extraHistory : List AttributeWatches.Event := [.install 1 missingEntry, .change 7 99]
def replacementHistory : List AttributeWatches.Event :=
  [.install 1 missingEntry, .install 1 ⟨7, 5, []⟩, .change 7 11]

theorem initially_absent_is_admitted :
    (AttributeWatches.run absentHistory).pending = [7] ∧ (run absentHistory).pending = [7] := by
  decide +kernel

theorem surviving_effect_is_admitted :
    (AttributeWatches.run sharedHistory).pending = [7] ∧ (run sharedHistory).pending = [7] := by
  decide +kernel

theorem different_name_is_intentional_extra :
    (AttributeWatches.run extraHistory).pending = [] ∧ (run extraHistory).pending = [7] := by
  decide +kernel

theorem equal_value_empty_replacement_clears_bit :
    (AttributeWatches.run replacementHistory).pending = [] ∧ (run replacementHistory).pending = [] := by
  decide +kernel

end AttributeWatchBits
