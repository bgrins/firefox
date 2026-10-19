import Projection
import WordWitness

namespace LanguageBreak

def mutationPiece (offset localOffset : Nat) : BufferedPiece :=
  { encodePiece (witnessChunk 1 (.atom 1 "ja") true offset) with
    units := [⟨65,by decide⟩,⟨176,by decide⟩,⟨65,by decide⟩],chunkOffset := localOffset }

def fixtureBreak (position : Nat) : BreakKind := if position < 2 then .normal else .none

def zeroOffset (piece : BufferedPiece) : BufferedPiece :=
  {piece with sinkOffset := piece.sinkOffset-piece.chunkOffset,chunkOffset := 0}

def publish (storage : Coordinate → Glyph) (writes : List PositionedWrite) : Coordinate → Glyph :=
  writes.foldl (fun state write => applyAt state write.destination write.kind) storage

def blankGlyphs (_ : Coordinate) : Glyph := ⟨.none,true,false⟩

theorem wrong_first_skip_counterexample :
    (publish blankGlyphs (projectPiece 0 false (mutationPiece 0 0) fixtureBreak) ⟨11,0⟩).kind ≠
      (publish blankGlyphs (projectPiece 0 true (mutationPiece 0 0) fixtureBreak) ⟨11,0⟩).kind := by decide

theorem wrong_offset_counterexample :
    (publish blankGlyphs (projectPiece 0 true (zeroOffset (mutationPiece 2 2)) fixtureBreak) ⟨11,1⟩).kind ≠
      (publish blankGlyphs (projectPiece 0 true (mutationPiece 2 2) fixtureBreak) ⟨11,1⟩).kind := by decide

end LanguageBreak

def main : IO Unit := do
  let wrongFirst := (LanguageBreak.publish LanguageBreak.blankGlyphs
    (LanguageBreak.projectPiece 0 false (LanguageBreak.mutationPiece 0 0) LanguageBreak.fixtureBreak) ⟨11,0⟩).kind
  let correctFirst := (LanguageBreak.publish LanguageBreak.blankGlyphs
    (LanguageBreak.projectPiece 0 true (LanguageBreak.mutationPiece 0 0) LanguageBreak.fixtureBreak) ⟨11,0⟩).kind
  let wrongOffset := (LanguageBreak.publish LanguageBreak.blankGlyphs
    (LanguageBreak.projectPiece 0 true (LanguageBreak.zeroOffset (LanguageBreak.mutationPiece 2 2)) LanguageBreak.fixtureBreak) ⟨11,1⟩).kind
  let correctOffset := (LanguageBreak.publish LanguageBreak.blankGlyphs
    (LanguageBreak.projectPiece 0 true (LanguageBreak.mutationPiece 2 2) LanguageBreak.fixtureBreak) ⟨11,1⟩).kind
  IO.println s!"wrong-first-skip mutant={repr wrongFirst} reference={repr correctFirst}"
  IO.println s!"wrong-sink-offset mutant={repr wrongOffset} reference={repr correctOffset}"
  if wrongFirst == correctFirst || wrongOffset == correctOffset then
    throw (IO.userError "mutation survived")
