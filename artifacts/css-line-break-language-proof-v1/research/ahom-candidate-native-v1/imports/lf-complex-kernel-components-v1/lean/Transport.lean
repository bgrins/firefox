import Buffer

namespace LanguageBreak

def Aligned (p : Providers) (word : WordLanguage) (tag : Tag) : Prop :=
  word.current = tag ∧ word.mixed = false ∧ word.script = reference p tag

theorem first_update_aligned (p : Providers) (cache : Cache) (word : WordLanguage)
    (tag : Tag) (valid : cache.Valid p) (stable : StableIdentity cache tag) :
    Aligned p (updateLanguage p cache (flushLanguage word) tag).2 tag := by
  refine ⟨?_, ?_, flushed_first_correct p cache word tag valid stable⟩
  · simp [updateLanguage, flushLanguage]
  · simp [updateLanguage, flushLanguage]

theorem update_cache_valid (p : Providers) (cache : Cache) (word : WordLanguage)
    (tag : Tag) (valid : cache.Valid p) :
    (updateLanguage p cache word tag).1.Valid p := by
  unfold updateLanguage
  split
  next _ => exact valid
  next _ =>
    split
    next _ => exact resolve_valid p cache tag valid
    next _ => exact valid

theorem same_update_aligned (p : Providers) (cache : Cache) (word : WordLanguage)
    (tag : Tag) (aligned : Aligned p word tag) :
    Aligned p (updateLanguage p cache word tag).2 tag := by
  rcases aligned with ⟨current, mixed, script⟩
  cases tag with
  | absent => simp [Aligned, updateLanguage, current, mixed, resolve, reference]
  | atom id text => simp [Aligned, updateLanguage, current, mixed, script]

structure TransportState where
  cache : Cache
  language : WordLanguage
  buffer : WordBuffer
  deriving DecidableEq, Repr

def appendTransport (p : Providers) (state : TransportState) (chunk : Chunk) : TransportState :=
  let updated := updateLanguage p state.cache state.language chunk.language
  ⟨updated.1, updated.2, appendPiece state.buffer (encodePiece chunk)⟩

def transportChunks (p : Providers) (state : TransportState) (chunks : List Chunk) : TransportState :=
  chunks.foldl (appendTransport p) state

def UniformChunks (tag : Tag) (chunks : List Chunk) : Prop :=
  ∀ chunk ∈ chunks, chunk.language = tag ∧ chunk.storage.decode ≠ []

theorem transport_preserves_alignment (p : Providers) (state : TransportState)
    (tag : Tag) (chunks : List Chunk)
    (aligned : Aligned p state.language tag) (valid : state.cache.Valid p)
    (uniform : UniformChunks tag chunks) :
    Aligned p (transportChunks p state chunks).language tag ∧
    (transportChunks p state chunks).cache.Valid p := by
  induction chunks generalizing state with
  | nil => exact ⟨aligned,valid⟩
  | cons chunk rest ih =>
    have same := (uniform chunk (by simp)).1
    have tail : UniformChunks tag rest := by
      intro next member
      exact uniform next (by simp [member])
    have nextAligned : Aligned p (appendTransport p state chunk).language tag := by
      simpa [appendTransport, same] using same_update_aligned p state.cache state.language tag aligned
    have nextValid : (appendTransport p state chunk).cache.Valid p :=
      update_cache_valid p state.cache state.language chunk.language valid
    exact ih (appendTransport p state chunk) nextAligned nextValid tail

theorem transport_units (p : Providers) (state : TransportState) (chunks : List Chunk) :
    (transportChunks p state chunks).buffer.units =
      state.buffer.units ++ chunks.flatMap (fun chunk => chunk.storage.decode) := by
  induction chunks generalizing state with
  | nil => simp [transportChunks]
  | cons chunk rest ih =>
    change (transportChunks p (appendTransport p state chunk) rest).buffer.units = _
    rw [ih]
    simp [appendTransport, appendPiece, encodePiece, List.append_assoc]

theorem transport_source_pieces (p : Providers) (state : TransportState) (chunks : List Chunk) :
    (transportChunks p state chunks).buffer.pieces = state.buffer.pieces ++ chunks.map encodePiece := by
  induction chunks generalizing state with
  | nil => simp [transportChunks]
  | cons chunk rest ih =>
    change (transportChunks p (appendTransport p state chunk) rest).buffer.pieces = _
    rw [ih]
    simp [appendTransport, appendPiece, List.append_assoc]

def startWord (p : Providers) (cache : Cache) (old : WordLanguage) (first : Chunk) : TransportState :=
  appendTransport p ⟨cache, flushLanguage old, {}⟩ first

theorem nonempty_word_transport (p : Providers) (cache : Cache) (old : WordLanguage)
    (first : Chunk) (rest : List Chunk)
    (valid : cache.Valid p) (stable : StableIdentity cache first.language)
    (uniform : UniformChunks first.language rest) :
    Aligned p (transportChunks p (startWord p cache old first) rest).language first.language ∧
    (transportChunks p (startWord p cache old first) rest).cache.Valid p ∧
    (transportChunks p (startWord p cache old first) rest).buffer.units =
      (first::rest).flatMap (fun chunk => chunk.storage.decode) ∧
    (transportChunks p (startWord p cache old first) rest).buffer.pieces =
      (first::rest).map encodePiece := by
  have firstAligned := first_update_aligned p cache old first.language valid stable
  have firstValid := update_cache_valid p cache (flushLanguage old) first.language valid
  have languageResult := transport_preserves_alignment p (startWord p cache old first)
    first.language rest firstAligned firstValid uniform
  refine ⟨languageResult.1,languageResult.2,?_,?_⟩
  · rw [transport_units]
    simp [startWord,appendTransport,appendPiece,encodePiece]
  · rw [transport_source_pieces]
    simp [startWord,appendTransport,appendPiece]

theorem immediate_current_language (p : Providers) (cache : Cache) (tag : Tag)
    (valid : cache.Valid p) (stable : StableIdentity cache tag) :
    (resolve p cache tag).1 = reference p tag := resolve_correct p cache tag valid stable

theorem all_four_storage_transitions (p : Providers) (state : TransportState)
    (left right : Chunk) :
    appendTransport p (appendTransport p state left.widen) right.widen =
      appendTransport p (appendTransport p state left) right := by
  rfl

theorem uniform_reset_reuse (p : Providers) (cache : Cache) (old : WordLanguage)
    (first : Chunk) (rest : List Chunk)
    (valid : cache.Valid p) (stable : StableIdentity cache first.language)
    (uniform : UniformChunks first.language rest) :
    (transportChunks p (startWord p cache (flushLanguage old) first) rest).language.script =
      reference p first.language :=
  (nonempty_word_transport p cache (flushLanguage old) first rest valid stable uniform).1.2.2

end LanguageBreak
