import Std

namespace LanguageBreak.GlyphBits

def breakMask : BitVec 32 := 0x60000000

def toggle (value : BitVec 32) (kind : BitVec 2) : BitVec 32 :=
  (((kind.zeroExtend 32) <<< 29) ^^^ value) &&& breakMask

def setBreak (value : BitVec 32) (kind : BitVec 2) : BitVec 32 := value ^^^ toggle value kind

def breakKind (value : BitVec 32) : BitVec 32 := (value &&& breakMask) >>> 29

def nonbreakBits (value : BitVec 32) : BitVec 32 := value &&& ~~~breakMask

theorem generic_mask_replacement (value incoming mask : BitVec 32) :
    (value ^^^ ((incoming ^^^ value) &&& mask)) &&& mask = incoming &&& mask := by
  apply BitVec.eq_of_getLsbD_eq_iff.mpr
  intro i inside
  simp only [BitVec.getLsbD_and,BitVec.getLsbD_xor]
  cases value.getLsbD i <;> cases incoming.getLsbD i <;> cases mask.getLsbD i <;> rfl

theorem generic_other_bits (value incoming mask : BitVec 32) :
    (value ^^^ ((incoming ^^^ value) &&& mask)) &&& ~~~mask = value &&& ~~~mask := by
  apply BitVec.eq_of_getLsbD_eq_iff.mpr
  intro i inside
  simp only [BitVec.getLsbD_and,BitVec.getLsbD_xor,BitVec.getLsbD_not,inside,decide_true,Bool.true_and]
  cases value.getLsbD i <;> cases incoming.getLsbD i <;> cases mask.getLsbD i <;> rfl

theorem exact_replacement (value : BitVec 32) (kind : BitVec 2) :
    breakKind (setBreak value kind) = kind.zeroExtend 32 := by
  unfold breakKind setBreak toggle
  rw [generic_mask_replacement]
  apply BitVec.eq_of_getLsbD_eq_iff.mpr
  intro i inside
  have indices : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 ∨ i = 4 ∨ i = 5 ∨ i = 6 ∨ i = 7 ∨ i = 8 ∨ i = 9 ∨ i = 10 ∨ i = 11 ∨ i = 12 ∨ i = 13 ∨ i = 14 ∨ i = 15 ∨ i = 16 ∨ i = 17 ∨ i = 18 ∨ i = 19 ∨ i = 20 ∨ i = 21 ∨ i = 22 ∨ i = 23 ∨ i = 24 ∨ i = 25 ∨ i = 26 ∨ i = 27 ∨ i = 28 ∨ i = 29 ∨ i = 30 ∨ i = 31 := by omega
  rcases indices with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals simp [breakMask]

theorem other_bits_preserved (value : BitVec 32) (kind : BitVec 2) :
    nonbreakBits (setBreak value kind) = nonbreakBits value :=
  generic_other_bits value (kind.zeroExtend 32 <<< 29) breakMask

theorem change_result_exact (value : BitVec 32) (kind : BitVec 2) :
    setBreak value kind ^^^ value = toggle value kind := by
  unfold setBreak
  apply BitVec.eq_of_getLsbD_eq_iff.mpr
  intro i inside
  simp only [BitVec.getLsbD_xor]
  cases value.getLsbD i <;> cases (toggle value kind).getLsbD i <;> rfl

theorem masked_field_preserved (value : BitVec 32) (kind : BitVec 2) (mask : BitVec 32)
    (outside : (~~~breakMask) &&& mask = mask) :
    (setBreak value kind) &&& mask = value &&& mask := by
  calc
    (setBreak value kind) &&& mask = nonbreakBits (setBreak value kind) &&& mask := by
      simp only [nonbreakBits,BitVec.and_assoc,outside]
    _ = nonbreakBits value &&& mask := by rw [other_bits_preserved]
    _ = value &&& mask := by simp only [nonbreakBits,BitVec.and_assoc,outside]

def simple (value : BitVec 32) : Bool := value &&& 0x80000000 != 0

def advance (value : BitVec 32) : BitVec 32 := (value &&& 0x0fff0000) >>> 16

def glyph (value : BitVec 32) : BitVec 32 := value &&& 0x0000ffff

def cluster (value : BitVec 32) : Bool := simple value || value &&& 0x00020000 == 0

def ligature (value : BitVec 32) : Bool := simple value || value &&& 0x00040000 == 0

def space (value : BitVec 32) : Bool := value &&& 0x10000000 != 0

def tab (value : BitVec 32) : Bool := !simple value && value &&& 0x00100000 != 0

def newline (value : BitVec 32) : Bool := !simple value && value &&& 0x00200000 != 0

theorem glyph_geometry_identity_preserved (value : BitVec 32) (kind : BitVec 2) :
    simple (setBreak value kind) = simple value ∧
    advance (setBreak value kind) = advance value ∧
    glyph (setBreak value kind) = glyph value ∧
    cluster (setBreak value kind) = cluster value ∧
    ligature (setBreak value kind) = ligature value ∧
    space (setBreak value kind) = space value ∧
    tab (setBreak value kind) = tab value ∧
    newline (setBreak value kind) = newline value := by
  have masks (mask : BitVec 32) (outside : (~~~breakMask) &&& mask = mask) :=
    masked_field_preserved value kind mask outside
  have h0 := masks 0x80000000 (by decide)
  have h1 := masks 0x0fff0000 (by decide)
  have h2 := masks 0x0000ffff (by decide)
  have h3 := masks 0x00020000 (by decide)
  have h4 := masks 0x00040000 (by decide)
  have h5 := masks 0x10000000 (by decide)
  have h6 := masks 0x00100000 (by decide)
  have h7 := masks 0x00200000 (by decide)
  simp only [simple,advance,glyph,cluster,ligature,space,tab,newline,h0,h1,h2,h3,h4,h5,h6,h7,and_self]

def detailedSpacing (value : BitVec 32) : Bool :=
  !simple value && value &&& 0x00080000 != 0

theorem detailed_spacing_preserved (value : BitVec 32) (kind : BitVec 2) :
    detailedSpacing (setBreak value kind) = detailedSpacing value := by
  have h0 := masked_field_preserved value kind 0x80000000 (by decide)
  have h1 := masked_field_preserved value kind 0x00080000 (by decide)
  simp only [detailedSpacing,simple,h0,h1]

def advanceForGlyph (value : BitVec 32) (details : List Int) (letterSpacing : Int) : Int :=
  if simple value then (advance value).toNat else
  let count := (glyph value).toNat
  if count = 0 then 0 else
  let initial := if detailedSpacing value then ((count-1 : Nat) : Int)*letterSpacing else 0
  (details.take count).foldl (·+·) initial

theorem advance_for_glyph_preserved (value : BitVec 32) (kind : BitVec 2)
    (details : List Int) (letterSpacing : Int) :
    advanceForGlyph (setBreak value kind) details letterSpacing =
      advanceForGlyph value details letterSpacing := by
  have fields := glyph_geometry_identity_preserved value kind
  unfold advanceForGlyph
  rw [fields.1,fields.2.1,fields.2.2.1,detailed_spacing_preserved]

def sinkWrite (value : BitVec 32) (kind : BitVec 2) : BitVec 32 :=
  if kind == 0 then value else setBreak value kind

theorem zero_sink_write_preserved (value : BitVec 32) : sinkWrite value 0 = value := by
  simp [sinkWrite]

theorem sink_write_geometry_identity (value : BitVec 32) (kind : BitVec 2) :
    nonbreakBits (sinkWrite value kind) = nonbreakBits value := by
  unfold sinkWrite
  split
  · rfl
  · exact other_bits_preserved value kind

end LanguageBreak.GlyphBits
