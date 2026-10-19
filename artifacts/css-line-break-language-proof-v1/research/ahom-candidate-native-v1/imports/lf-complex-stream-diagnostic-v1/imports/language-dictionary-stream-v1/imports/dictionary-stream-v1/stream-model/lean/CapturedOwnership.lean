import ScanWords

namespace LanguageBreak

def OwnershipInvariant (state : StreamState) : Prop :=
  state.ownedPieces.map Prod.fst = state.policy.transport.buffer.pieces ∧
  ∀ last, state.ownedPieces.getLast? = some last → last.2 = state.capturedLimits

theorem add_buffered_ownership (state : StreamState) (piece : BufferedPiece)
    (valid : OwnershipInvariant state) : OwnershipInvariant (addBuffered state piece) := by
  constructor
  · simpa [addBuffered,appendPiece] using congrArg (fun xs => xs ++ [piece]) valid.1
  · intro last found
    simp only [addBuffered,List.getLast?_append,List.getLast?_singleton] at found
    cases found
    rfl

theorem update_stream_ownership (providers : StreamProviders) (state : StreamState) (tag : Tag)
    (valid : OwnershipInvariant state) :
    OwnershipInvariant (updateStreamLanguage providers state tag).state := valid

theorem repeated_language_ownership (providers : StreamProviders) (tag : Tag) (count : Nat)
    (result : StreamResult) (valid : OwnershipInvariant result.state) :
    OwnershipInvariant (repeatLanguage providers tag count result).state := by
  induction count generalizing result with
  | zero => exact valid
  | succ count ih => exact ih _ (update_stream_ownership providers result.state tag valid)

theorem completed_immediate_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (valid : OwnershipInvariant scan.state) :
    OwnershipInvariant (completeImmediate providers width chunk scan).state := by
  unfold completeImmediate segmentImmediate
  repeat first | exact valid | split

theorem scan_step_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (noBreaks : Bool) (scan : Scan) (valid : OwnershipInvariant scan.state) :
    OwnershipInvariant (scanStep providers width chunk noBreaks scan).state := by
  dsimp only [scanStep]
  split
  · split
    · exact completed_immediate_ownership providers width chunk _ valid
    · exact valid
  · split
    · exact valid
    · exact update_stream_ownership providers _ chunk.language (add_buffered_ownership _ _ valid)

theorem scan_loop_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (noBreaks : Bool) (fuel : Nat) (scan : Scan)
    (valid : OwnershipInvariant scan.state) :
    OwnershipInvariant (scanLoop providers width chunk noBreaks fuel scan).state := by
  induction fuel generalizing scan with
  | zero => exact valid
  | succ fuel ih =>
    unfold scanLoop
    split
    · exact valid
    · exact ih _ (scan_step_ownership providers width chunk noBreaks scan valid)

theorem remainder_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (start : Nat) (input : StreamResult) (valid : OwnershipInvariant input.state) :
    OwnershipInvariant (scanRemainder providers width chunk start input).state := by
  unfold scanRemainder publishImmediate
  exact scan_loop_ownership providers width chunk _ _ _ valid

theorem flush_stream_ownership (providers : StreamProviders) (state : StreamState) :
    OwnershipInvariant (flushStream providers state).state := by
  constructor
  · rfl
  · intro last found
    simp [flushStream] at found

theorem prefix_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (state : StreamState) (valid : OwnershipInvariant state) :
    OwnershipInvariant (extendPrefix providers width chunk state).state := by
  dsimp only [extendPrefix]
  split
  · exact valid
  · exact repeated_language_ownership providers chunk.language _ _ (add_buffered_ownership _ _ valid)

theorem append_core_ownership (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (state : StreamState) (valid : OwnershipInvariant state) :
    OwnershipInvariant (appendCore providers width chunk state).state := by
  dsimp only [appendCore]
  split
  · exact valid
  · split
    · exact remainder_ownership providers width chunk _ _ valid
    · split
      · exact prefix_ownership providers width chunk state valid
      · exact remainder_ownership providers width chunk _ _ (flush_stream_ownership providers _)

theorem append_stream_ownership (providers : StreamProviders) (chunk : Chunk)
    (state : StreamState) (valid : OwnershipInvariant state) :
    OwnershipInvariant (appendStream providers chunk state).state := by
  cases stored : chunk.storage with
  | bytes units =>
    simp only [appendStream,stored]
    split <;> exact append_core_ownership providers _ _ state valid
  | utf16 units =>
    simp only [appendStream,stored]
    exact append_core_ownership providers _ _ state valid

theorem step_stream_ownership (providers : StreamProviders) (state : StreamState)
    (op : Operation) (valid : OwnershipInvariant state) :
    OwnershipInvariant (stepStream providers state op).state := by
  cases op with
  | append chunk => exact append_stream_ownership providers chunk state valid
  | word value =>
    change OwnershipInvariant (wordStream providers state value).state
    unfold wordStream
    split
    · exact flush_stream_ownership providers state
    · exact valid
  | line value =>
    change OwnershipInvariant (lineStream providers state value).state
    unfold lineStream
    split
    · exact flush_stream_ownership providers state
    · exact valid
  | limits value => exact valid
  | continuation value => exact valid
  | whitespace value => exact flush_stream_ownership providers state
  | reset => exact flush_stream_ownership providers state

theorem arbitrary_operations_ownership (providers : StreamProviders) (ops : List Operation)
    (result : StreamResult) (valid : OwnershipInvariant result.state) :
    OwnershipInvariant (runStream providers result ops).state := by
  induction ops generalizing result with
  | nil => exact valid
  | cons op rest ih => exact ih _ (step_stream_ownership providers result.state op valid)

theorem constructor_sequence_ownership (providers : StreamProviders) (ops : List Operation) :
    OwnershipInvariant (runStream providers ⟨initialStream {},[]⟩ ops).state := by
  apply arbitrary_operations_ownership
  exact ⟨rfl,by intro last found; simp [initialStream] at found⟩

theorem active_capture_is_last_contributor (providers : StreamProviders) (ops : List Operation)
    (last : BufferedPiece × AuxLimits)
    (found : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces.getLast? = some last) :
    (runStream providers ⟨initialStream {},[]⟩ ops).state.capturedLimits = last.2 :=
  ((constructor_sequence_ownership providers ops).2 last found).symm

theorem constructed_last_contributor_nonempty (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (incoming : ∀ op ∈ ops, OperationFits world op)
    (last : BufferedPiece × AuxLimits)
    (found : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces.getLast? = some last) :
    0 < last.1.units.length := by
  have member := List.mem_of_getLast? found
  have mapped : last.1 ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces.map Prod.fst :=
    List.mem_map.mpr ⟨last,member,rfl⟩
  rw [(constructor_sequence_ownership providers ops).1] at mapped
  exact (constructor_sequence_word_invariant world providers ops incoming).nonempty last.1 mapped

theorem delimiter_setter_preserves_active_capture (providers : StreamProviders)
    (state : StreamState) (limits : AuxLimits) :
    (stepStream providers state (.limits limits)).state.capturedLimits = state.capturedLimits := rfl

theorem flush_leaves_inactive_capture_bytes (providers : StreamProviders) (state : StreamState) :
    (flushStream providers state).state.capturedLimits = state.capturedLimits ∧
    (flushStream providers state).state.ownedPieces = [] := ⟨rfl,rfl⟩

theorem constructed_uniform_word_limits (providers : StreamProviders) (ops : List Operation)
    (limits : AuxLimits)
    (pending : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces ≠ [])
    (uniform : ∀ piece ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces,
      piece.2 = limits) :
    (runStream providers ⟨initialStream {},[]⟩ ops).state.capturedLimits = limits := by
  generalize found : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces.getLast? = last
  cases last with
  | none =>
    have empty := List.getLast?_eq_none_iff.mp found
    exact False.elim (pending empty)
  | some piece =>
    exact (active_capture_is_last_contributor providers ops piece found).trans
      (uniform piece (List.mem_of_getLast? found))

theorem uniform_buffered_hyphenation_uses_word_limits (providers : StreamProviders)
    (ops : List Operation) (limits : AuxLimits) (breaks : List BreakKind)
    (pending : (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces ≠ [])
    (uniform : ∀ piece ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.ownedPieces,
      piece.2 = limits) :
    hyphenateBuffered providers.breaks (runStream providers ⟨initialStream {},[]⟩ ops).state.policy
      (runStream providers ⟨initialStream {},[]⟩ ops).state.capturedLimits breaks =
    hyphenateBuffered providers.breaks (runStream providers ⟨initialStream {},[]⟩ ops).state.policy limits breaks := by
  rw [constructed_uniform_word_limits providers ops limits pending uniform]

end LanguageBreak
