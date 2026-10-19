import Emphasis
import RawWords
import RunGeometry

namespace Emphasis.Witness

theorem original_other : candidate .Co false ≠ original .Co false := by decide +kernel
theorem all_other : specified .Cc false ≠ true := by decide +kernel
theorem missing_punctuation : specified .Po true ≠ false := by decide +kernel
theorem added_punctuation : specified .Po false ≠ true := by decide +kernel

def high : Unit := ⟨0xDBFF, by decide⟩
def low : Unit := ⟨0xDFFD, by decide⟩

theorem wrong_pair_value : privateUseRange (nativePairValue high low) ≠
    privateUseRange (nativePairValue high low + 1) := by decide +kernel

theorem one_pair_unit : ([false,false] : List Bool) ≠ [false,true] := by decide +kernel

def puaHigh : Unit := ⟨0xDB80, by decide⟩
def puaLow : Unit := ⟨0xDC00, by decide⟩
def space : Unit := ⟨32, by decide⟩

theorem skip_after_pair : loopFlags privateUseRange [puaHigh,puaLow,space] ≠
    [true,true,true] := by decide +kernel

theorem revisit_pair_tail : loopFlags privateUseRange [puaHigh,puaLow] ≠
    [true,false] := by decide +kernel

theorem lost_common_flags : Raw.suppress 0xe07b01c8 ≠ (0x00410001 : Raw.Word) := by decide +kernel

def common : Common := ⟨⟨3, by decide⟩,false⟩
def simpleGlyph : Glyph := .simple common ⟨456, by decide⟩ ⟨123, by decide⟩
def badAdvance : Glyph := .complex common { simpleFlags with noEmphasis := true } [⟨456,0,0,0⟩]

theorem lost_advance : unaffected (suppress simpleGlyph) ≠ unaffected badAdvance := by decide +kernel

theorem last_unit_fold : nativeAny [true,false] false ≠ false := by decide +kernel

def datum : Run.Datum := ⟨simpleGlyph,0,4,0⟩
def action : Run.Action := .cluster [datum]

theorem suppress_draw : (Run.nativeActions 2 [action] 0).2 ≠ [] := by decide +kernel
theorem duplicate_draw : (Run.nativeActions 2 [action] 0).2 ≠ [2,2] := by decide +kernel

theorem skip_ligature_interval : Run.shrink 0 [false,true,true] true ≠ (3,3) := by decide +kernel
theorem truncate_ligature_interval : Run.shrink 0 [true,true,false] false ≠ (0,0) := by decide +kernel

theorem skip_following_font_runs :
    (Run.nativeActions 2 [action,action] 0).2 ≠ (Run.nativeActions 2 [action] 0).2 := by decide +kernel

theorem omit_before_spacing :
    Run.nativePositionTwice [{datum with before := 2}] 0 2 ≠
    Run.nativePositionTwice [datum] 0 2 := by decide +kernel

theorem nonvacuous_space_combining : nativeAny [false,true] false = true := by decide +kernel
theorem nonvacuous_no_marks : nativeAny [false,false] false = false := by decide +kernel
theorem nonvacuous_nonzero_partial_range : Run.shrink 7 [false,true,true,false] false = (8,9) := by decide +kernel

end Emphasis.Witness
