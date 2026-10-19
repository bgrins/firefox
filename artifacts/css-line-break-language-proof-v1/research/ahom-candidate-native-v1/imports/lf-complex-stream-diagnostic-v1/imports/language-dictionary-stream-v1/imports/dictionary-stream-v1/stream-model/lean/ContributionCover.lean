import Buffer

namespace LanguageBreak

def wordCoordinates (pieces : List BufferedPiece) (start : Nat) : List Nat :=
  (locate start pieces).flatMap locatedCoordinates

theorem contribution_cover (pieces : List BufferedPiece) (start : Nat) :
    wordCoordinates pieces start = List.range' start (flattenPieces pieces).length := by
  induction pieces generalizing start with
  | nil => simp [wordCoordinates,locate,flattenPieces]
  | cons piece rest ih =>
    change List.range' start piece.units.length ++ wordCoordinates rest (start+piece.units.length) = _
    rw [ih]
    simp [flattenPieces]

theorem word_coordinate_bounds (pieces : List BufferedPiece) (start position : Nat)
    (member : position ∈ wordCoordinates pieces start) :
    start ≤ position ∧ position < start + (flattenPieces pieces).length := by
  rw [contribution_cover] at member
  simpa using member

theorem covers_each_word_position (pieces : List BufferedPiece) (position : Nat)
    (bound : position < (flattenPieces pieces).length) :
    position ∈ wordCoordinates pieces 0 := by
  rw [contribution_cover]
  simpa using bound

theorem contribution_coordinates_disjoint (pieces : List BufferedPiece) (start : Nat) :
    (wordCoordinates pieces start).Nodup := by
  rw [contribution_cover]
  exact List.nodup_range'

end LanguageBreak
