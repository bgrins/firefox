import AppendCache

namespace LanguageBreak

structure WordInvariant (p : Providers) (state : TransportState) : Prop where
  cache : state.cache.Valid p
  cover : state.buffer.Valid
  nonempty : ∀ piece ∈ state.buffer.pieces, 0 < piece.units.length
  idle : state.buffer.pieces = [] → state.language.current = .absent ∧ state.language.mixed = false
  uniform : ∀ tag, state.buffer.pieces ≠ [] →
    (∀ piece ∈ state.buffer.pieces, piece.language = tag) → Aligned p state.language tag

def appendLabeledPiece (p : Providers) (state : TransportState) (piece : BufferedPiece) : TransportState :=
  let next := updateLanguage p state.cache state.language piece.language
  ⟨next.1,next.2,appendPiece state.buffer piece⟩

theorem initial_word_invariant (p : Providers) : WordInvariant p (initialStream {}).policy.transport := by
  constructor
  · exact empty_valid p
  · rfl
  · simp [initialStream]
  · simp [initialStream]
  · simp [initialStream]

theorem append_labeled_piece_invariant (p : Providers) (state : TransportState) (piece : BufferedPiece)
    (valid : WordInvariant p state) (positive : 0 < piece.units.length)
    (stable : StableIdentity state.cache piece.language) :
    WordInvariant p (appendLabeledPiece p state piece) := by
  constructor
  · exact update_cache_valid p state.cache state.language piece.language valid.cache
  · exact append_preserves_cover state.buffer piece valid.cover
  · intro other member
    change other ∈ state.buffer.pieces ++ [piece] at member
    simp only [List.mem_append,List.mem_singleton] at member
    rcases member with previous | rfl
    · exact valid.nonempty other previous
    · exact positive
  · simp [appendLabeledPiece,appendPiece]
  · intro tag pending uniform
    have language : piece.language = tag := uniform piece (by simp [appendLabeledPiece,appendPiece])
    change Aligned p (updateLanguage p state.cache state.language piece.language).2 tag
    by_cases empty : state.buffer.pieces = []
    · obtain ⟨current,mixed⟩ := valid.idle empty
      have answer := resolve_correct p state.cache piece.language valid.cache stable
      simp only [Aligned,updateLanguage,current,mixed,ne_eq,not_true_eq_false,false_and,↓reduceIte]
      exact ⟨language,True.intro,by simpa only [language] using answer⟩
    · have old : Aligned p state.language tag := valid.uniform tag empty (by
        intro other member
        exact uniform other (by simp [appendLabeledPiece,appendPiece,member]))
      rw [language]
      exact same_update_aligned p state.cache state.language tag old

theorem flush_word_invariant (p : Providers) (state : PolicyState)
    (valid : WordInvariant p state.transport) : WordInvariant p (clearWord state).transport := by
  constructor
  · exact valid.cache
  · rfl
  · simp [clearWord]
  · simp [clearWord,flushLanguage]
  · simp [clearWord]

theorem invariant_empty_units_empty_pieces (p : Providers) (state : TransportState)
    (valid : WordInvariant p state) (empty : state.buffer.units = []) : state.buffer.pieces = [] := by
  cases pieces : state.buffer.pieces with
  | nil => rfl
  | cons piece rest =>
    have positive := valid.nonempty piece (by simp [pieces])
    have cover := valid.cover
    simp only [WordBuffer.Valid,flattenPieces,pieces,List.flatMap_cons] at cover
    rw [empty] at cover
    have length := congrArg List.length cover
    simp only [List.length_nil,List.length_append] at length
    omega

theorem invariant_ready_for_new_word (p : Providers) (state : TransportState)
    (valid : WordInvariant p state) (empty : state.buffer.units = []) :
    state.language.current = .absent ∧ state.language.mixed = false :=
  valid.idle (invariant_empty_units_empty_pieces p state valid empty)

end LanguageBreak
