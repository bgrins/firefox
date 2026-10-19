import Operations

namespace LanguageBreak

theorem segment_immediate_current_language (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (units : List CodeUnit)
    (valid : scan.state.policy.transport.cache.Valid providers.locale)
    (stable : StableIdentity scan.state.policy.transport.cache chunk.language) :
    (segmentImmediate providers width chunk scan units).events = scan.events ++
      [.resolve chunk.language,.segment width units scan.state.policy.wordPolicy scan.state.policy.linePolicy
        (reference providers.locale chunk.language)] := by
  simp only [segmentImmediate]
  rw [resolve_correct providers.locale scan.state.policy.transport.cache chunk.language valid stable]

theorem segment_immediate_cache_valid (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (units : List CodeUnit)
    (valid : scan.state.policy.transport.cache.Valid providers.locale) :
    (segmentImmediate providers width chunk scan units).state.policy.transport.cache.Valid providers.locale :=
  resolve_valid providers.locale scan.state.policy.transport.cache chunk.language valid

theorem completed_immediate_cache_valid (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (valid : scan.state.policy.transport.cache.Valid providers.locale) :
    (completeImmediate providers width chunk scan).state.policy.transport.cache.Valid providers.locale := by
  have segmented := segment_immediate_cache_valid providers width chunk scan
    ((chunk.storage.decode.drop scan.wordStart).take (scan.position-scan.wordStart)) valid
  unfold completeImmediate
  repeat first | exact valid | exact segmented | split

theorem update_stream_cache_valid (providers : StreamProviders) (state : StreamState) (tag : Tag)
    (valid : state.policy.transport.cache.Valid providers.locale) :
    (updateStreamLanguage providers state tag).state.policy.transport.cache.Valid providers.locale :=
  update_cache_valid providers.locale state.policy.transport.cache state.policy.transport.language tag valid

theorem repeated_stream_cache_valid (providers : StreamProviders) (tag : Tag) (count : Nat)
    (result : StreamResult) (valid : result.state.policy.transport.cache.Valid providers.locale) :
    (repeatLanguage providers tag count result).state.policy.transport.cache.Valid providers.locale := by
  induction count generalizing result with
  | zero => exact valid
  | succ n ih =>
    exact ih _ (update_stream_cache_valid providers result.state tag valid)

theorem flush_stream_cache_valid (providers : StreamProviders) (state : StreamState)
    (valid : state.policy.transport.cache.Valid providers.locale) :
    (flushStream providers state).state.policy.transport.cache.Valid providers.locale := valid

theorem scan_step_cache_valid (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (scan : Scan) (valid : scan.state.policy.transport.cache.Valid providers.locale) :
    (scanStep providers width chunk noBreaks scan).state.policy.transport.cache.Valid providers.locale := by
  dsimp only [scanStep]
  split
  · split
    · exact completed_immediate_cache_valid providers width chunk _ valid
    · exact valid
  · split
    · exact valid
    · exact update_stream_cache_valid providers _ chunk.language valid

theorem scan_loop_cache_valid (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (fuel : Nat) (scan : Scan)
    (valid : scan.state.policy.transport.cache.Valid providers.locale) :
    (scanLoop providers width chunk noBreaks fuel scan).state.policy.transport.cache.Valid providers.locale := by
  induction fuel generalizing scan with
  | zero => exact valid
  | succ n ih =>
    unfold scanLoop
    split
    · exact valid
    · exact ih _ (scan_step_cache_valid providers width chunk noBreaks scan valid)

theorem remainder_cache_valid (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (start : Nat) (input : StreamResult)
    (valid : input.state.policy.transport.cache.Valid providers.locale) :
    (scanRemainder providers width chunk start input).state.policy.transport.cache.Valid providers.locale := by
  unfold scanRemainder publishImmediate
  exact scan_loop_cache_valid providers width chunk _ _ _ valid

theorem extend_prefix_cache_valid (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (valid : state.policy.transport.cache.Valid providers.locale) :
    (extendPrefix providers width chunk state).state.policy.transport.cache.Valid providers.locale := by
  dsimp only [extendPrefix]
  split
  · exact valid
  · exact repeated_stream_cache_valid providers chunk.language _ _ valid

theorem append_core_cache_valid (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (valid : state.policy.transport.cache.Valid providers.locale) :
    (appendCore providers width chunk state).state.policy.transport.cache.Valid providers.locale := by
  dsimp only [appendCore]
  split
  · exact valid
  · split
    · exact remainder_cache_valid providers width chunk 0 _ valid
    · have extended := extend_prefix_cache_valid providers width chunk state valid
      split
      · exact extended
      · exact remainder_cache_valid providers width chunk _ _ (flush_stream_cache_valid providers _ extended)

theorem append_stream_cache_valid (providers : StreamProviders) (chunk : Chunk) (state : StreamState)
    (valid : state.policy.transport.cache.Valid providers.locale) :
    (appendStream providers chunk state).state.policy.transport.cache.Valid providers.locale := by
  cases stored : chunk.storage with
  | bytes values =>
    simp only [appendStream,stored]
    split <;> exact append_core_cache_valid providers _ _ state valid
  | utf16 values =>
    simp only [appendStream,stored]
    exact append_core_cache_valid providers _ _ state valid

theorem step_stream_cache_valid (providers : StreamProviders) (state : StreamState) (op : Operation)
    (valid : state.policy.transport.cache.Valid providers.locale) :
    (stepStream providers state op).state.policy.transport.cache.Valid providers.locale := by
  cases op with
  | append chunk => exact append_stream_cache_valid providers chunk state valid
  | word value =>
    change (wordStream providers state value).state.policy.transport.cache.Valid providers.locale
    unfold wordStream
    split <;> exact valid
  | line value =>
    change (lineStream providers state value).state.policy.transport.cache.Valid providers.locale
    unfold lineStream
    split <;> exact valid
  | limits value => exact valid
  | continuation value => exact valid
  | whitespace value => exact valid
  | reset => exact valid

theorem arbitrary_operations_cache_valid (providers : StreamProviders) (ops : List Operation)
    (result : StreamResult) (valid : result.state.policy.transport.cache.Valid providers.locale) :
    (runStream providers result ops).state.policy.transport.cache.Valid providers.locale := by
  induction ops generalizing result with
  | nil => exact valid
  | cons op rest ih =>
    exact ih _ (step_stream_cache_valid providers result.state op valid)

end LanguageBreak
