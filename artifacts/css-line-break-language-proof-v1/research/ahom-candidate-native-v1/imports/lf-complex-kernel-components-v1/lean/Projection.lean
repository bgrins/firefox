import ContributionCover

namespace LanguageBreak

def positionSuppressed (piece : BufferedPiece) (index : Nat) : Bool :=
  if piece.chunkOffset + index = 0 then piece.suppressInitial else piece.suppressInside

def bufferedMask (piece : BufferedPiece) (index : Nat) (kind : BreakKind) : BreakKind :=
  let initial := if piece.suppressInitial && piece.chunkOffset == 0 && index == 0 then .none else kind
  if piece.suppressInside && (if piece.chunkOffset == 0 then 1 else 0) ≤ index then .none else initial

theorem buffered_mask_matches_position (piece : BufferedPiece) (index : Nat) (kind : BreakKind) :
    bufferedMask piece index kind = if positionSuppressed piece index then .none else kind := by
  by_cases chunk : piece.chunkOffset = 0
  · by_cases first : index = 0
    · simp [bufferedMask,positionSuppressed,chunk,first]
    · have positive : 1 ≤ index := by omega
      simp [bufferedMask,positionSuppressed,chunk,first,positive]
  · simp [bufferedMask,positionSuppressed,chunk]

structure PositionedWrite where
  wordOffset : Nat
  sourceOwner : Nat
  destination : Coordinate
  kind : BreakKind
  sinkIdentity : Nat
  deriving DecidableEq, Repr

def projectPiece (wordOffset : Nat) (first : Bool) (piece : BufferedPiece)
    (provider : Nat → BreakKind) : List PositionedWrite :=
  match piece.sinkOwner with
  | none => []
  | some owner =>
    ((List.range piece.units.length).filter (fun i => !(first && i == 0))).map fun i =>
      ⟨wordOffset+i,piece.sourceOwner,⟨owner,piece.sinkOffset+i⟩,
       bufferedMask piece i (provider (wordOffset+i)),piece.sinkIdentity⟩

theorem projected_range_and_owner (wordOffset : Nat) (first : Bool) (piece : BufferedPiece)
    (provider : Nat → BreakKind) (write : PositionedWrite)
    (member : write ∈ projectPiece wordOffset first piece provider) :
    piece.sinkOwner = some write.destination.owner ∧ write.sourceOwner = piece.sourceOwner ∧
    wordOffset ≤ write.wordOffset ∧ write.wordOffset < wordOffset + piece.units.length ∧
    piece.sinkOffset ≤ write.destination.offset ∧
    write.destination.offset < piece.sinkOffset + piece.units.length := by
  unfold projectPiece at member
  split at member
  next absent => simp at member
  next owner present =>
    simp only [List.mem_map,List.mem_filter,List.mem_range] at member
    obtain ⟨index,⟨bound,kept⟩,rfl⟩ := member
    dsimp only
    exact ⟨present,rfl,by omega,by omega,by omega,by omega⟩

theorem projected_sink_identity (wordOffset : Nat) (first : Bool) (piece : BufferedPiece)
    (provider : Nat → BreakKind) (write : PositionedWrite)
    (member : write ∈ projectPiece wordOffset first piece provider) :
    write.sinkIdentity = piece.sinkIdentity := by
  unfold projectPiece at member
  split at member
  next absent => simp at member
  next owner present =>
    simp only [List.mem_map] at member
    obtain ⟨index,kept,rfl⟩ := member
    rfl

theorem first_word_character_not_published (wordOffset : Nat) (piece : BufferedPiece)
    (provider : Nat → BreakKind) (write : PositionedWrite)
    (member : write ∈ projectPiece wordOffset true piece provider) :
    write.wordOffset ≠ wordOffset := by
  unfold projectPiece at member
  split at member
  next absent => simp at member
  next owner present =>
    simp only [List.mem_map,List.mem_filter,List.mem_range] at member
    obtain ⟨index,⟨bound,kept⟩,rfl⟩ := member
    have nonzero : index ≠ 0 := by
      intro zero
      subst index
      simp at kept
    change wordOffset+index ≠ wordOffset
    omega

end LanguageBreak
