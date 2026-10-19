import Flush

namespace LanguageBreak

structure SinkDescriptor where
  owner : Nat
  base : Nat
  capacity : Nat
  deriving DecidableEq, Repr

def BufferedPiece.Admitted (sinks : Nat → SinkDescriptor) (piece : BufferedPiece) : Prop :=
  0 < piece.units.length ∧
  ∀ owner, piece.sinkOwner = some owner →
    (sinks piece.sinkIdentity).owner = owner ∧
    piece.sinkOffset = (sinks piece.sinkIdentity).base + piece.chunkOffset ∧
    piece.chunkOffset + piece.units.length ≤ (sinks piece.sinkIdentity).capacity

def callbackRange (sinks : Nat → SinkDescriptor) (identity owner offset count : Nat) : Prop :=
  (sinks identity).owner = owner ∧ (sinks identity).base ≤ offset ∧
  offset + count ≤ (sinks identity).base + (sinks identity).capacity

def FlushEvent.InRange (sinks : Nat → SinkDescriptor) : FlushEvent → Prop
  | .breaks identity owner offset values => callbackRange sinks identity owner offset values.length
  | .capitals identity owner offset values => callbackRange sinks identity owner offset values.length
  | _ => True

theorem admitted_piece_callback (sinks : Nat → SinkDescriptor) (piece : BufferedPiece)
    (owner skip count : Nat) (admitted : piece.Admitted sinks)
    (present : piece.sinkOwner = some owner) (within : skip + count ≤ piece.units.length) :
    callbackRange sinks piece.sinkIdentity owner (piece.sinkOffset+skip) count := by
  obtain ⟨positive,range⟩ := admitted
  obtain ⟨identity,offset,bound⟩ := range owner present
  unfold callbackRange
  exact ⟨identity,by omega,by omega⟩

theorem emit_callbacks_in_range (providers : BreakProviders) (units : List CodeUnit)
    (continuation : Bool) (breaks : List BreakKind) (offset : Nat) (first : Bool)
    (capitalized : Option (List Bool)) (pieces : List BufferedPiece)
    (sinks : Nat → SinkDescriptor) (admitted : ∀ piece ∈ pieces, piece.Admitted sinks) :
    ∀ event ∈ emitBuffered providers units continuation breaks offset first capitalized pieces,
      event.InRange sinks := by
  induction pieces generalizing offset first capitalized with
  | nil => simp [emitBuffered]
  | cons piece rest ih =>
    have current := admitted piece (by simp)
    have tail : ∀ piece ∈ rest, piece.Admitted sinks := by
      intro piece member
      exact admitted piece (by simp [member])
    have recurse := ih (offset+piece.units.length) false capitalized tail
    unfold emitBuffered
    split
    next absent => exact recurse
    next owner present =>
      let skip := if first then 1 else 0
      have skipBound : skip ≤ piece.units.length := by
        dsimp [skip]
        split <;> have positive := current.1 <;> omega
      have breakRange : callbackRange sinks piece.sinkIdentity owner (piece.sinkOffset+skip)
          ((((List.range piece.units.length).map fun i =>
            bufferedMask piece i (breaks[offset+i]?.getD .none)).drop skip).length) := by
        apply admitted_piece_callback sinks piece owner skip _ current present
        simp only [List.length_drop,List.length_map,List.length_range]
        omega
      by_cases wantsCaps : (!continuation && piece.capitalization) = true
      · simp only [ite_eq_left wantsCaps]
        have capRange : callbackRange sinks piece.sinkIdentity owner piece.sinkOffset
            (((capitalized.getD (providers.capitalize units)).drop offset).take piece.units.length).length := by
          simpa using admitted_piece_callback sinks piece owner 0 _ current present
            (by simp only [Nat.zero_add]; omega)
        have capRecurse := ih (offset+piece.units.length) false
          (some (capitalized.getD (providers.capitalize units))) tail
        intro event member
        simp only [List.mem_append,List.mem_cons,List.not_mem_nil,or_false] at member
        rcases member with ((rfl | middle) | rfl) | remaining
        · exact breakRange
        · split at middle <;> simp_all [FlushEvent.InRange]
        · exact capRange
        · exact capRecurse event remaining
      · simp only [ite_eq_right wantsCaps]
        intro event member
        simp only [List.mem_cons] at member
        rcases member with rfl | remaining
        · exact breakRange
        · exact recurse event remaining

end LanguageBreak
