import WordInvariant

namespace LanguageBreak

theorem update_stream_idempotent (providers : StreamProviders) (state : StreamState) (tag : Tag) :
    (updateStreamLanguage providers (updateStreamLanguage providers state tag).state tag).state =
      (updateStreamLanguage providers state tag).state := by
  have same := update_idempotent providers.locale state.policy.transport.cache state.policy.transport.language tag
  simp only [updateStreamLanguage]
  dsimp only at same
  rw [same]

theorem repeated_language_state (providers : StreamProviders) (tag : Tag) (n : Nat) (result : StreamResult) :
    (repeatLanguage providers tag (n+1) result).state = (updateStreamLanguage providers result.state tag).state := by
  induction n generalizing result with
  | zero => rfl
  | succ n ih =>
    change (repeatLanguage providers tag (n+1)
      ⟨(updateStreamLanguage providers result.state tag).state,result.events++(updateStreamLanguage providers result.state tag).events⟩).state = _
    rw [ih]
    exact update_stream_idempotent providers result.state tag

theorem repeated_language_positive_state (providers : StreamProviders) (tag : Tag) (count : Nat)
    (result : StreamResult) (positive : 0 < count) :
    (repeatLanguage providers tag count result).state = (updateStreamLanguage providers result.state tag).state := by
  cases count with
  | zero => omega
  | succ n => exact repeated_language_state providers tag n result

theorem add_then_update_transport (providers : StreamProviders) (state : StreamState) (piece : BufferedPiece) :
    (updateStreamLanguage providers (addBuffered state piece) piece.language).state.policy.transport =
      appendLabeledPiece providers.locale state.policy.transport piece := rfl

theorem extend_prefix_transport (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (nonempty : (chunk.storage.decode.takeWhile (fun u => !asciiSpace u)) ≠ []) :
    (extendPrefix providers width chunk state).state.policy.transport =
      appendLabeledPiece providers.locale state.policy.transport
        (pieceOf chunk 0 (chunk.storage.decode.takeWhile (fun u => !asciiSpace u)).length) := by
  have length : 0 < (chunk.storage.decode.takeWhile (fun u => !asciiSpace u)).length := List.length_pos_iff.mpr nonempty
  unfold extendPrefix
  simp only [List.isEmpty_iff,nonempty,ite_eq_right,not_false_eq_true]
  rw [repeated_language_positive_state providers chunk.language _ _ (by split <;> omega)]
  rfl

theorem extend_prefix_word_invariant (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (valid : WordInvariant providers.locale state.policy.transport)
    (stable : StableIdentity state.policy.transport.cache chunk.language)
    (nonempty : (chunk.storage.decode.takeWhile (fun u => !asciiSpace u)) ≠ []) :
    WordInvariant providers.locale (extendPrefix providers width chunk state).state.policy.transport := by
  rw [extend_prefix_transport providers width chunk state nonempty]
  apply append_labeled_piece_invariant providers.locale state.policy.transport _ valid
  · have positive := List.length_pos_iff.mpr nonempty
    have bound := (List.takeWhile_sublist (l := chunk.storage.decode) (fun u => !asciiSpace u)).length_le
    simpa [pieceOf,encodePiece,List.length_take,Nat.min_eq_left bound] using positive
  · exact stable

end LanguageBreak
