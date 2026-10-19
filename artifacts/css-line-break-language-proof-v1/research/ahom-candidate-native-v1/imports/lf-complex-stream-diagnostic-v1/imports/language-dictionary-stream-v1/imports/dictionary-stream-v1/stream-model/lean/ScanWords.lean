import ScanBounds

namespace LanguageBreak

theorem recache_word_invariant (p : Providers) (state : TransportState) (cache : Cache)
    (valid : WordInvariant p state) (cached : cache.Valid p) :
    WordInvariant p {state with cache := cache} :=
  ⟨cached,valid.cover,valid.nonempty,valid.idle,valid.uniform⟩

theorem segmented_word_invariant (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (units : List CodeUnit)
    (valid : WordInvariant providers.locale scan.state.policy.transport) :
    WordInvariant providers.locale (segmentImmediate providers width chunk scan units).state.policy.transport :=
  recache_word_invariant providers.locale scan.state.policy.transport _ valid
    (resolve_valid providers.locale scan.state.policy.transport.cache chunk.language valid.cache)

theorem completed_word_invariant (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (valid : WordInvariant providers.locale scan.state.policy.transport) :
    WordInvariant providers.locale (completeImmediate providers width chunk scan).state.policy.transport := by
  have segmented := segmented_word_invariant providers width chunk scan
    ((chunk.storage.decode.drop scan.wordStart).take (scan.position-scan.wordStart)) valid
  unfold completeImmediate
  repeat first | exact valid | exact segmented | split

theorem completed_buffer_unchanged (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) :
    (completeImmediate providers width chunk scan).state.policy.transport.buffer = scan.state.policy.transport.buffer := by
  unfold completeImmediate segmentImmediate
  repeat first | rfl | split

structure ScanInvariant (world : Nat → String) (providers : StreamProviders)
    (chunk : Chunk) (scan : Scan) : Prop where
  word : WordInvariant providers.locale scan.state.policy.transport
  identity : CacheFits world scan.state.policy.transport.cache
  ordered : scan.wordStart ≤ scan.position
  bounded : scan.position ≤ chunk.storage.decode.length
  empty : scan.finished = false → scan.state.policy.transport.buffer.units = []

theorem scan_step_word_invariant (world : Nat → String) (providers : StreamProviders)
    (width : Encoding) (chunk : Chunk) (noBreaks : Bool) (scan : Scan)
    (valid : ScanInvariant world providers chunk scan) (incoming : TagFits world chunk.language)
    (running : scan.finished = false) (inside : scan.position < chunk.storage.decode.length) :
    ScanInvariant world providers chunk (scanStep providers width chunk noBreaks scan) := by
  have oldEmpty := valid.empty running
  have ordered := valid.ordered
  have bounded := valid.bounded
  dsimp only [scanStep]
  split
  · split
    · constructor
      · exact completed_word_invariant providers width chunk _ valid.word
      · exact completed_immediate_world world providers width chunk _ valid.identity incoming
      · dsimp; omega
      · dsimp; omega
      · intro _
        rw [completed_buffer_unchanged]
        exact oldEmpty
    · exact ⟨valid.word,valid.identity,by dsimp; omega,by dsimp; omega,fun _ => oldEmpty⟩
  · split
    · exact ⟨valid.word,valid.identity,by dsimp; omega,by dsimp; omega,fun _ => oldEmpty⟩
    · constructor
      · change WordInvariant providers.locale (appendLabeledPiece providers.locale scan.state.policy.transport
          (pieceOf chunk scan.wordStart (chunk.storage.decode.length-scan.wordStart)))
        apply append_labeled_piece_invariant providers.locale scan.state.policy.transport _ valid.word
        · have start := valid.ordered
          simp only [pieceOf,encodePiece,List.length_take,List.length_drop]
          omega
        · exact world_stable_identity world _ chunk.language valid.identity incoming
      · exact update_world world providers.locale _ _ chunk.language valid.identity incoming
      · dsimp; omega
      · have start := valid.ordered; dsimp; omega
      · simp

theorem scan_loop_word_invariant (world : Nat → String) (providers : StreamProviders)
    (width : Encoding) (chunk : Chunk) (noBreaks : Bool) (fuel : Nat) (scan : Scan)
    (valid : ScanInvariant world providers chunk scan) (incoming : TagFits world chunk.language) :
    ScanInvariant world providers chunk (scanLoop providers width chunk noBreaks fuel scan) := by
  induction fuel generalizing scan with
  | zero => exact valid
  | succ fuel ih =>
    unfold scanLoop
    split
    · exact valid
    next active =>
      have running : scan.finished = false := by
        cases h : scan.finished <;> simp_all
      have inside : scan.position < chunk.storage.decode.length := by
        simp only [running,Bool.false_or,decide_eq_true_eq] at active
        omega
      exact ih _ (scan_step_word_invariant world providers width chunk noBreaks scan valid incoming running inside)

theorem last_space_start_bounds (units : List CodeUnit) (start : Nat) (bounded : start ≤ units.length) :
    start ≤ lastSpaceStart units start ∧ lastSpaceStart units start ≤ units.length := by
  unfold lastSpaceStart
  cases found : ((List.range units.length).filter
      (fun i => start ≤ i && asciiSpace (units[i]?.getD ⟨0,by decide⟩))).getLast? with
  | none => simp [bounded]
  | some position =>
    have member := List.mem_of_getLast? found
    simp only [List.mem_filter,List.mem_range,Bool.and_eq_true,decide_eq_true_eq] at member
    simp only [Option.getD_some]
    exact ⟨member.2.1,Nat.le_of_lt member.1⟩

theorem remainder_word_invariant (world : Nat → String) (providers : StreamProviders)
    (width : Encoding) (chunk : Chunk) (start : Nat) (input : StreamResult)
    (valid : WordInvariant providers.locale input.state.policy.transport)
    (identity : CacheFits world input.state.policy.transport.cache)
    (incoming : TagFits world chunk.language)
    (empty : input.state.policy.transport.buffer.units = []) (bounded : start ≤ chunk.storage.decode.length) :
    WordInvariant providers.locale (scanRemainder providers width chunk start input).state.policy.transport := by
  unfold scanRemainder publishImmediate
  apply (scan_loop_word_invariant world providers width chunk _ _ _ ?_ incoming).word
  constructor
  · exact valid
  · exact identity
  · exact Nat.le_refl _
  · split
    · exact (last_space_start_bounds chunk.storage.decode start bounded).2
    · exact bounded
  · exact fun _ => empty

theorem flush_stream_word_invariant (providers : StreamProviders) (state : StreamState)
    (valid : WordInvariant providers.locale state.policy.transport) :
    WordInvariant providers.locale (flushStream providers state).state.policy.transport :=
  flush_word_invariant providers.locale state.policy valid

theorem extend_prefix_all_word_invariant (world : Nat → String) (providers : StreamProviders)
    (width : Encoding) (chunk : Chunk) (state : StreamState)
    (valid : WordInvariant providers.locale state.policy.transport)
    (identity : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    WordInvariant providers.locale (extendPrefix providers width chunk state).state.policy.transport := by
  by_cases empty : (chunk.storage.decode.takeWhile (fun u => !asciiSpace u)) = []
  · simpa [extendPrefix,empty] using valid
  · exact extend_prefix_word_invariant providers width chunk state valid
      (world_stable_identity world _ chunk.language identity incoming) empty

theorem append_core_word_invariant (world : Nat → String) (providers : StreamProviders)
    (width : Encoding) (chunk : Chunk) (state : StreamState)
    (valid : WordInvariant providers.locale state.policy.transport)
    (identity : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    WordInvariant providers.locale (appendCore providers width chunk state).state.policy.transport := by
  dsimp only [appendCore]
  split
  · exact valid
  · split
    next empty =>
      exact remainder_word_invariant world providers width chunk 0 _ valid identity incoming
        (List.isEmpty_iff.mp empty) (Nat.zero_le _)
    next pending =>
      have extended := extend_prefix_all_word_invariant world providers width chunk state valid identity incoming
      have extendedWorld := extend_prefix_world world providers width chunk state identity incoming
      split
      · exact extended
      · exact remainder_word_invariant world providers width chunk _ _
          (flush_stream_word_invariant providers _ extended) extendedWorld incoming rfl
          (List.takeWhile_sublist (l := chunk.storage.decode) (fun u => !asciiSpace u)).length_le

theorem append_stream_word_invariant (world : Nat → String) (providers : StreamProviders)
    (chunk : Chunk) (state : StreamState)
    (valid : WordInvariant providers.locale state.policy.transport)
    (identity : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    WordInvariant providers.locale (appendStream providers chunk state).state.policy.transport := by
  cases stored : chunk.storage with
  | bytes units =>
    simp only [appendStream,stored]
    split <;> exact append_core_word_invariant world providers _ _ state valid identity incoming
  | utf16 units =>
    simp only [appendStream,stored]
    exact append_core_word_invariant world providers _ _ state valid identity incoming

theorem step_stream_word_invariant (world : Nat → String) (providers : StreamProviders)
    (state : StreamState) (op : Operation)
    (valid : WordInvariant providers.locale state.policy.transport)
    (identity : CacheFits world state.policy.transport.cache) (incoming : OperationFits world op) :
    WordInvariant providers.locale (stepStream providers state op).state.policy.transport := by
  cases op with
  | append chunk => exact append_stream_word_invariant world providers chunk state valid identity incoming
  | word value =>
    change WordInvariant providers.locale (wordStream providers state value).state.policy.transport
    unfold wordStream
    split
    · exact flush_stream_word_invariant providers state valid
    · exact valid
  | line value =>
    change WordInvariant providers.locale (lineStream providers state value).state.policy.transport
    unfold lineStream
    split
    · exact flush_stream_word_invariant providers state valid
    · exact valid
  | limits value => exact valid
  | continuation value => exact valid
  | whitespace value => exact flush_stream_word_invariant providers state valid
  | reset => exact flush_stream_word_invariant providers state valid

theorem arbitrary_operations_word_invariant (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (result : StreamResult)
    (valid : WordInvariant providers.locale result.state.policy.transport)
    (identity : CacheFits world result.state.policy.transport.cache)
    (incoming : ∀ op ∈ ops, OperationFits world op) :
    WordInvariant providers.locale (runStream providers result ops).state.policy.transport := by
  induction ops generalizing result with
  | nil => exact valid
  | cons op rest ih =>
    apply ih
    · exact step_stream_word_invariant world providers result.state op valid identity (incoming op (by simp))
    · exact step_stream_world world providers result.state op identity (incoming op (by simp))
    · intro next member
      exact incoming next (by simp [member])

theorem constructor_sequence_word_invariant (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (incoming : ∀ op ∈ ops, OperationFits world op) :
    WordInvariant providers.locale (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport :=
  arbitrary_operations_word_invariant world providers ops _
    (initial_word_invariant providers.locale) (constructor_world world) incoming

theorem constructed_uniform_word_language (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (tag : Tag) (incoming : ∀ op ∈ ops, OperationFits world op)
    (pending : (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.pieces ≠ [])
    (uniform : ∀ piece ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.pieces,
      piece.language = tag) :
    Aligned providers.locale (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.language tag :=
  (constructor_sequence_word_invariant world providers ops incoming).uniform tag pending uniform

theorem constructed_buffered_provider_language (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (tag : Tag) (incoming : ∀ op ∈ ops, OperationFits world op)
    (pending : (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.pieces ≠ [])
    (uniform : ∀ piece ∈ (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.pieces,
      piece.language = tag)
    (ordinary : (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.linePolicy.val ≠ 4)
    (needed : (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.mightBreak = true ∨
      (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.wordPolicy.val = 1) :
    (segmentBuffered providers.breaks (runStream providers ⟨initialStream {},[]⟩ ops).state.policy).2 =
      [.segmentation (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.buffer.units
        (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.wordPolicy
        (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.linePolicy (reference providers.locale tag)] :=
  uniform_buffer_segmentation_language providers.breaks _ providers.locale tag
    (constructed_uniform_word_language world providers ops tag incoming pending uniform) ordinary needed

end LanguageBreak
