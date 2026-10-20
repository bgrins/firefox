import StickyPipeline
namespace StickyChallenges
open StickyAxis StickyGeometry StickyContinuations StickyRanges

def firstFrame : Frame := ⟨1,10,some 10,⟨10,5⟩,⟨10,5⟩⟩
def secondFrame : Frame := ⟨2,30,some 30,⟨30,5⟩,⟨30,5⟩⟩

theorem auto_requires_both_witness :
    (nativeNormalize ⟨none,some 20⟩ 100 200 true).far ≠ 20 := by decide +kernel

theorem auto_becomes_constraint_witness :
    (movementEdges ⟨none,some 20⟩ (nativeNormalize ⟨none,some 20⟩ 100 200 true) 160 100 200).1 = none ∧
    StickyPosition.native 0 160 160 0 600 ≠ StickyPosition.native 0 (-536870911) 160 0 600 := by decide +kernel

theorem child_mode_witness :
    StickyWritingMode.normalizeWithContainingMode
      (StickyWritingMode.flags .verticalRl false .mixed) 0 ⟨some 20,none⟩ 100 200 .x ≠
    StickyWritingMode.normalizeWithContainingMode 0 0 ⟨some 20,none⟩ 100 200 .x := by decide +kernel

theorem omit_near_clamp_witness :
    StickyPosition.native 0 20 80 0 100 ≠ min 0 (max 80 0) := by decide +kernel

theorem missing_normal_moves_witness :
    (nativeDispatch 50 [{firstFrame with storedNormal:=none}]).1 ≠
      (nativeLoop 40 [{firstFrame with storedNormal:=none}]).1 := by decide +kernel

theorem collapse_continuations_witness :
    ((nativeLoop 5 [firstFrame,secondFrame]).1.map Frame.current) = [15,35] ∧
    ((nativeLoop 5 [firstFrame,secondFrame]).1.map Frame.current) ≠ [15,15] := by decide +kernel

def refreshRaw : Raw := ⟨⟨0,200⟩,⟨0,200⟩,⟨0,800⟩,0,0,100,0,0,160,⟨none,none⟩⟩

theorem skip_offset_refresh_witness :
    position 0 (nativeLimits refreshRaw true false (-536870911) 536870912) ≠
      position 0 (nativeLimits {refreshRaw with insets:=⟨some 0,none⟩} true false (-536870911) 536870912) := by decide +kernel

def strictEarliest (offset endAt endMax startAt startMax : Int) : Int :=
  if endMax ≠ 0 ∧ offset < endAt then offset-endMax
  else if startMax ≠ 0 ∧ offset > startAt then offset+startMax else offset

theorem earliest_strict_witness : earliest 0 0 20 50 30 ≠ strictEarliest 0 0 20 50 30 := by decide +kernel

theorem logical_end_only_witness :
    nativeNormalize ⟨some (-20),some 10⟩ 100 200 false = ⟨-110,10⟩ := by decide +kernel

theorem explicit_edge_can_equal_sentinel :
    100-(-536870822)-10 = (536870912 : Int) := by decide +kernel

end StickyChallenges
