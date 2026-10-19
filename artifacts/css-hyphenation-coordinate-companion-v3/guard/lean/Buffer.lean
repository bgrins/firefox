import WordLanguage
import Sink

namespace LanguageBreak

abbrev CodeUnit := Fin 65536

inductive StoredUnits where
  | bytes (units : List (Fin 256))
  | utf16 (units : List CodeUnit)
  deriving DecidableEq, Repr

def widenByte (byte : Fin 256) : CodeUnit := ⟨byte.val,by omega⟩

def StoredUnits.decode : StoredUnits → List CodeUnit
  | .bytes units => units.map widenByte
  | .utf16 units => units

def StoredUnits.widen (units : StoredUnits) : StoredUnits := .utf16 units.decode

theorem widening_preserves_units (units : StoredUnits) : units.widen.decode = units.decode := rfl

structure Chunk where
  sourceOwner : Nat
  language : Tag
  sinkOwner : Option Nat
  sinkOffset : Nat
  storage : StoredUnits
  suppressInitial : Bool
  suppressInside : Bool
  capitalization : Bool
  hyphenation : Bool
  chunkOffset : Nat := 0
  sinkIdentity : Nat := 0
  skipNoBreaks : Bool := false
  deriving DecidableEq, Repr

def Chunk.widen (chunk : Chunk) : Chunk := { chunk with storage := chunk.storage.widen }

theorem widening_preserves_metadata (chunk : Chunk) :
    chunk.widen.sourceOwner = chunk.sourceOwner ∧
    chunk.widen.language = chunk.language ∧
    chunk.widen.sinkOwner = chunk.sinkOwner ∧
    chunk.widen.sinkOffset = chunk.sinkOffset ∧
    chunk.widen.suppressInitial = chunk.suppressInitial ∧
    chunk.widen.suppressInside = chunk.suppressInside ∧
    chunk.widen.capitalization = chunk.capitalization ∧
    chunk.widen.hyphenation = chunk.hyphenation ∧
    chunk.widen.sinkIdentity = chunk.sinkIdentity ∧
    chunk.widen.skipNoBreaks = chunk.skipNoBreaks := by simp [Chunk.widen]

structure BufferedPiece where
  sourceOwner : Nat
  language : Tag
  sinkOwner : Option Nat
  sinkOffset : Nat
  units : List CodeUnit
  suppressInitial : Bool
  suppressInside : Bool
  capitalization : Bool
  hyphenation : Bool
  chunkOffset : Nat
  sinkIdentity : Nat := 0
  skipNoBreaks : Bool := false
  deriving DecidableEq, Repr

def BufferedPiece.contribution (piece : BufferedPiece) : Contribution :=
  ⟨piece.sourceOwner,piece.sinkOwner,piece.sinkOffset,piece.units.length⟩

structure LocatedPiece where
  wordOffset : Nat
  piece : BufferedPiece
  deriving DecidableEq, Repr

def flattenPieces (pieces : List BufferedPiece) : List CodeUnit := pieces.flatMap BufferedPiece.units

def locate (start : Nat) : List BufferedPiece → List LocatedPiece
  | [] => []
  | piece::rest => ⟨start,piece⟩ :: locate (start+piece.units.length) rest

theorem flatten_append (left right : List BufferedPiece) :
    flattenPieces (left++right) = flattenPieces left ++ flattenPieces right := by
  simp [flattenPieces]

theorem locate_append (left right : List BufferedPiece) (start : Nat) :
    locate start (left++right) = locate start left ++ locate (start+(flattenPieces left).length) right := by
  induction left generalizing start with
  | nil => simp [locate,flattenPieces]
  | cons piece rest ih =>
    simp only [List.cons_append,locate,List.cons_append,List.cons.injEq,true_and]
    rw [ih]
    simp [flattenPieces,Nat.add_assoc]

def locatedCoordinates (entry : LocatedPiece) : List Nat := List.range' entry.wordOffset entry.piece.units.length

theorem locate_first (piece : BufferedPiece) (rest : List BufferedPiece) (start : Nat) :
    (locate start (piece::rest)).head? = some ⟨start,piece⟩ := rfl

structure WordBuffer where
  pieces : List BufferedPiece := []
  units : List CodeUnit := []
  deriving DecidableEq, Repr

def WordBuffer.Valid (buffer : WordBuffer) : Prop := buffer.units = flattenPieces buffer.pieces

def appendPiece (buffer : WordBuffer) (piece : BufferedPiece) : WordBuffer :=
  { pieces := buffer.pieces++[piece],units := buffer.units++piece.units }

theorem empty_buffer_valid : ({} : WordBuffer).Valid := rfl

theorem append_preserves_cover (buffer : WordBuffer) (piece : BufferedPiece) (valid : buffer.Valid) :
    (appendPiece buffer piece).Valid := by
  simp only [WordBuffer.Valid,appendPiece,flatten_append]
  rw [valid]
  simp [flattenPieces]

def appendPieces (buffer : WordBuffer) (pieces : List BufferedPiece) : WordBuffer := pieces.foldl appendPiece buffer

theorem arbitrary_pieces_preserve_cover (buffer : WordBuffer) (pieces : List BufferedPiece) (valid : buffer.Valid) :
    (appendPieces buffer pieces).Valid := by
  induction pieces generalizing buffer with
  | nil => exact valid
  | cons piece rest ih => exact ih (appendPiece buffer piece) (append_preserves_cover buffer piece valid)

theorem append_pieces_units (buffer : WordBuffer) (pieces : List BufferedPiece) :
    (appendPieces buffer pieces).units = buffer.units ++ flattenPieces pieces := by
  induction pieces generalizing buffer with
  | nil => simp [appendPieces,flattenPieces]
  | cons piece rest ih =>
    simp only [appendPieces,List.foldl_cons]
    rw [show (List.foldl appendPiece (appendPiece buffer piece) rest).units =
      (appendPiece buffer piece).units ++ flattenPieces rest from ih (appendPiece buffer piece)]
    simp [appendPiece,flattenPieces,List.append_assoc]

theorem partition_same_provider_contents (left right : List BufferedPiece)
    (sameStream : flattenPieces left = flattenPieces right) :
    (appendPieces {} left).units = (appendPieces {} right).units := by
  rw [append_pieces_units,append_pieces_units,sameStream]

def encodePiece (chunk : Chunk) : BufferedPiece :=
  ⟨chunk.sourceOwner,chunk.language,chunk.sinkOwner,chunk.sinkOffset,chunk.storage.decode,
   chunk.suppressInitial,chunk.suppressInside,chunk.capitalization,chunk.hyphenation,chunk.chunkOffset,chunk.sinkIdentity,chunk.skipNoBreaks⟩

theorem encode_widen_same_piece (chunk : Chunk) : encodePiece chunk.widen = encodePiece chunk := rfl

theorem width_transition_contents (initial : WordBuffer) (left right : Chunk) :
    (appendPiece (appendPiece initial (encodePiece left.widen)) (encodePiece right.widen)).units =
    (appendPiece (appendPiece initial (encodePiece left)) (encodePiece right)).units := rfl

end LanguageBreak
