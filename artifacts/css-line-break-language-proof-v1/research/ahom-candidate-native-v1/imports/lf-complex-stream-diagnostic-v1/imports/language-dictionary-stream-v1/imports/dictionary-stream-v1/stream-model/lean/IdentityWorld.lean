import StreamLanguage

namespace LanguageBreak

def TagFits (world : Nat → String) : Tag → Prop
  | .absent => True
  | .atom id text => text = world id

def CacheFits (world : Nat → String) (cache : Cache) : Prop :=
  ∀ id text, cache.retained = some (id,text) → text = world id

theorem world_stable_identity (world : Nat → String) (cache : Cache) (tag : Tag)
    (stored : CacheFits world cache) (incoming : TagFits world tag) : StableIdentity cache tag := by
  intro old text id retained atom
  subst tag
  exact (stored id old retained).trans incoming.symm

theorem resolve_world (world : Nat → String) (p : Providers) (cache : Cache) (tag : Tag)
    (stored : CacheFits world cache) (incoming : TagFits world tag) :
    CacheFits world (resolve p cache tag).2 := by
  cases tag with
  | absent => exact stored
  | atom id text =>
    simp only [resolve]
    split
    · exact stored
    · cases p.parseAndResolve text with
      | invalid => exact stored
      | providerError => exact stored
      | script value =>
        intro other actual retained
        simp only [Option.some.injEq,Prod.mk.injEq] at retained
        rcases retained with ⟨rfl,rfl⟩
        exact incoming

theorem update_world (world : Nat → String) (p : Providers) (cache : Cache) (word : WordLanguage)
    (tag : Tag) (stored : CacheFits world cache) (incoming : TagFits world tag) :
    CacheFits world (updateLanguage p cache word tag).1 := by
  unfold updateLanguage
  split
  · exact stored
  · split
    · exact resolve_world world p cache tag stored incoming
    · exact stored

theorem segment_immediate_world (world : Nat → String) (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (units : List CodeUnit)
    (valid : CacheFits world scan.state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (segmentImmediate providers width chunk scan units).state.policy.transport.cache :=
  resolve_world world providers.locale scan.state.policy.transport.cache chunk.language valid incoming

theorem completed_immediate_world (world : Nat → String) (providers : StreamProviders) (width : Encoding)
    (chunk : Chunk) (scan : Scan) (valid : CacheFits world scan.state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (completeImmediate providers width chunk scan).state.policy.transport.cache := by
  have segmented := segment_immediate_world world providers width chunk scan
    ((chunk.storage.decode.drop scan.wordStart).take (scan.position-scan.wordStart)) valid incoming
  unfold completeImmediate
  repeat first | exact valid | exact segmented | split

theorem update_stream_world (world : Nat → String) (providers : StreamProviders) (state : StreamState) (tag : Tag)
    (valid : CacheFits world state.policy.transport.cache) (incoming : TagFits world tag) :
    CacheFits world (updateStreamLanguage providers state tag).state.policy.transport.cache :=
  update_world world providers.locale state.policy.transport.cache state.policy.transport.language tag valid incoming

theorem repeated_stream_world (world : Nat → String) (providers : StreamProviders) (tag : Tag) (count : Nat)
    (result : StreamResult) (valid : CacheFits world result.state.policy.transport.cache) (incoming : TagFits world tag) :
    CacheFits world (repeatLanguage providers tag count result).state.policy.transport.cache := by
  induction count generalizing result with
  | zero => exact valid
  | succ n ih =>
    exact ih _ (update_stream_world world providers result.state tag valid incoming)

theorem flush_stream_world (world : Nat → String) (providers : StreamProviders) (state : StreamState)
    (valid : CacheFits world state.policy.transport.cache) :
    CacheFits world (flushStream providers state).state.policy.transport.cache := valid

theorem scan_step_world (world : Nat → String) (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (scan : Scan) (valid : CacheFits world scan.state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (scanStep providers width chunk noBreaks scan).state.policy.transport.cache := by
  dsimp only [scanStep]
  split
  · split
    · exact completed_immediate_world world providers width chunk _ valid incoming
    · exact valid
  · split
    · exact valid
    · exact update_stream_world world providers _ chunk.language valid incoming

theorem scan_loop_world (world : Nat → String) (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (noBreaks : Bool) (fuel : Nat) (scan : Scan)
    (valid : CacheFits world scan.state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (scanLoop providers width chunk noBreaks fuel scan).state.policy.transport.cache := by
  induction fuel generalizing scan with
  | zero => exact valid
  | succ n ih =>
    unfold scanLoop
    split
    · exact valid
    · exact ih _ (scan_step_world world providers width chunk noBreaks scan valid incoming)

theorem remainder_world (world : Nat → String) (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (start : Nat) (input : StreamResult)
    (valid : CacheFits world input.state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (scanRemainder providers width chunk start input).state.policy.transport.cache := by
  unfold scanRemainder publishImmediate
  exact scan_loop_world world providers width chunk _ _ _ valid incoming

theorem extend_prefix_world (world : Nat → String) (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (valid : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (extendPrefix providers width chunk state).state.policy.transport.cache := by
  dsimp only [extendPrefix]
  split
  · exact valid
  · exact repeated_stream_world world providers chunk.language _ _ valid incoming

theorem append_core_world (world : Nat → String) (providers : StreamProviders) (width : Encoding) (chunk : Chunk)
    (state : StreamState) (valid : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (appendCore providers width chunk state).state.policy.transport.cache := by
  dsimp only [appendCore]
  split
  · exact valid
  · split
    · exact remainder_world world providers width chunk 0 _ valid incoming
    · have extended := extend_prefix_world world providers width chunk state valid incoming
      split
      · exact extended
      · exact remainder_world world providers width chunk _ _ (flush_stream_world world providers _ extended) incoming

theorem append_stream_world (world : Nat → String) (providers : StreamProviders) (chunk : Chunk) (state : StreamState)
    (valid : CacheFits world state.policy.transport.cache) (incoming : TagFits world chunk.language) :
    CacheFits world (appendStream providers chunk state).state.policy.transport.cache := by
  cases stored : chunk.storage with
  | bytes values =>
    simp only [appendStream,stored]
    split <;> exact append_core_world world providers _ _ state valid incoming
  | utf16 values =>
    simp only [appendStream,stored]
    exact append_core_world world providers _ _ state valid incoming


def OperationFits (world : Nat → String) : Operation → Prop
  | .append chunk => TagFits world chunk.language
  | _ => True

theorem step_stream_world (world : Nat → String) (providers : StreamProviders)
    (state : StreamState) (op : Operation) (stored : CacheFits world state.policy.transport.cache)
    (incoming : OperationFits world op) :
    CacheFits world (stepStream providers state op).state.policy.transport.cache := by
  cases op with
  | append chunk => exact append_stream_world world providers chunk state stored incoming
  | word value =>
    change CacheFits world (wordStream providers state value).state.policy.transport.cache
    unfold wordStream
    split <;> exact stored
  | line value =>
    change CacheFits world (lineStream providers state value).state.policy.transport.cache
    unfold lineStream
    split <;> exact stored
  | limits value => exact stored
  | continuation value => exact stored
  | whitespace value => exact stored
  | reset => exact stored

theorem arbitrary_operations_world (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (result : StreamResult)
    (stored : CacheFits world result.state.policy.transport.cache)
    (incoming : ∀ op ∈ ops, OperationFits world op) :
    CacheFits world (runStream providers result ops).state.policy.transport.cache := by
  induction ops generalizing result with
  | nil => exact stored
  | cons op rest ih =>
    apply ih
    · exact step_stream_world world providers result.state op stored (incoming op (by simp))
    · intro next member
      exact incoming next (by simp [member])

theorem constructor_world (world : Nat → String) :
    CacheFits world (initialStream {}).policy.transport.cache := by
  simp [initialStream,CacheFits]

theorem constructed_sequence_stable (world : Nat → String) (providers : StreamProviders)
    (ops : List Operation) (tag : Tag)
    (incoming : ∀ op ∈ ops, OperationFits world op) (next : TagFits world tag) :
    StableIdentity (runStream providers ⟨initialStream {},[]⟩ ops).state.policy.transport.cache tag :=
  world_stable_identity world _ tag
    (arbitrary_operations_world world providers ops _ (constructor_world world) incoming) next

end LanguageBreak
