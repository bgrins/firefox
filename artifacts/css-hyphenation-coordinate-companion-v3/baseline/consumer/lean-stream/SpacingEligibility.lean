import GlyphBreakBits

namespace HyphenSpacingEligibility

open LanguageBreak.GlyphBits

def formatting (value : BitVec 32) : Bool :=
  !simple value && value &&& 0x00800000 != 0

def update (glyphs : Nat → BitVec 32) (kinds : Nat → BitVec 2) : Nat → BitVec 32 :=
  fun index => sinkWrite (glyphs index) (kinds index)

def canBefore (glyphs : Nat → BitVec 32) (offset : Nat) (significantNewline : Bool) : Bool :=
  if significantNewline && newline (glyphs offset) then false
  else if offset = 0 then true
  else cluster (glyphs offset) && ligature (glyphs offset) &&
    !formatting (glyphs (offset-1)) && !tab (glyphs offset)

def canAfter (glyphs : Nat → BitVec 32) (length offset : Nat) (significantNewline : Bool) : Bool :=
  if significantNewline && newline (glyphs offset) then false
  else if offset+1 ≥ length then true
  else cluster (glyphs (offset+1)) && ligature (glyphs (offset+1)) &&
    !formatting (glyphs offset) && !tab (glyphs offset)

theorem formatting_preserved (value : BitVec 32) (kind : BitVec 2) :
    formatting (setBreak value kind) = formatting value := by
  have simpleField := (glyph_geometry_identity_preserved value kind).1
  have formatField := masked_field_preserved value kind 0x00800000 (by decide)
  simp only [formatting,simpleField,formatField]

theorem sink_getters_preserved (value : BitVec 32) (kind : BitVec 2) :
    cluster (sinkWrite value kind) = cluster value ∧
    ligature (sinkWrite value kind) = ligature value ∧
    tab (sinkWrite value kind) = tab value ∧
    newline (sinkWrite value kind) = newline value ∧
    formatting (sinkWrite value kind) = formatting value := by
  unfold sinkWrite
  split
  · exact ⟨rfl,rfl,rfl,rfl,rfl⟩
  · have h := glyph_geometry_identity_preserved value kind
    exact ⟨h.2.2.2.1,h.2.2.2.2.1,h.2.2.2.2.2.2.1,h.2.2.2.2.2.2.2,formatting_preserved value kind⟩

theorem before_eligibility_preserved (glyphs : Nat → BitVec 32) (kinds : Nat → BitVec 2)
    (offset : Nat) (significantNewline : Bool) :
    canBefore (update glyphs kinds) offset significantNewline = canBefore glyphs offset significantNewline := by
  have here := sink_getters_preserved (glyphs offset) (kinds offset)
  have previous := sink_getters_preserved (glyphs (offset-1)) (kinds (offset-1))
  simp only [canBefore,update,here.1,here.2.1,here.2.2.1,here.2.2.2.1,previous.2.2.2.2]

theorem after_eligibility_preserved (glyphs : Nat → BitVec 32) (kinds : Nat → BitVec 2)
    (length offset : Nat) (significantNewline : Bool) :
    canAfter (update glyphs kinds) length offset significantNewline = canAfter glyphs length offset significantNewline := by
  have here := sink_getters_preserved (glyphs offset) (kinds offset)
  have next := sink_getters_preserved (glyphs (offset+1)) (kinds (offset+1))
  simp only [canAfter,update,here.2.2.1,here.2.2.2.1,here.2.2.2.2,next.1,next.2.1]

theorem no_space_before_preserved_newline (glyphs : Nat → BitVec 32) (offset : Nat)
    (isNewline : newline (glyphs offset) = true) : canBefore glyphs offset true = false := by
  simp [canBefore,isNewline]

theorem no_space_after_preserved_newline (glyphs : Nat → BitVec 32) (length offset : Nat)
    (isNewline : newline (glyphs offset) = true) : canAfter glyphs length offset true = false := by
  simp [canAfter,isNewline]

end HyphenSpacingEligibility
