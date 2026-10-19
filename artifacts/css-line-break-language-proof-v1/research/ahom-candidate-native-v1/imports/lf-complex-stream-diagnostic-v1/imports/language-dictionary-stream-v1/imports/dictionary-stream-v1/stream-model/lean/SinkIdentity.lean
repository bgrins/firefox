import Flush
import ProjectionMutation

namespace LanguageBreak

def aliasedPiece (identity : Nat) : BufferedPiece :=
  { mutationPiece 4 0 with sinkIdentity := identity }

theorem aliased_run_coordinates :
    (projectPiece 0 false (aliasedPiece 7) fixtureBreak).map PositionedWrite.destination =
    (projectPiece 0 false (aliasedPiece 8) fixtureBreak).map PositionedWrite.destination := by decide

theorem aliased_sink_instances_distinct :
    (projectPiece 0 false (aliasedPiece 7) fixtureBreak).map PositionedWrite.sinkIdentity ≠
    (projectPiece 0 false (aliasedPiece 8) fixtureBreak).map PositionedWrite.sinkIdentity := by decide

theorem encoding_preserves_sink_instance (chunk : Chunk) :
    (encodePiece chunk).sinkIdentity = chunk.sinkIdentity ∧
    (encodePiece chunk.widen).sinkIdentity = chunk.sinkIdentity := ⟨rfl,rfl⟩

theorem sink_instance_follows_piece (wordOffset : Nat) (first : Bool) (piece : BufferedPiece)
    (provider : Nat → BreakKind) (write : PositionedWrite)
    (member : write ∈ projectPiece wordOffset first piece provider) :
    write.sinkIdentity = piece.sinkIdentity ∧ write.sourceOwner = piece.sourceOwner ∧
    piece.sinkOwner = some write.destination.owner := by
  have bounds := projected_range_and_owner wordOffset first piece provider write member
  exact ⟨projected_sink_identity wordOffset first piece provider write member,bounds.2.1,bounds.1⟩

end LanguageBreak
