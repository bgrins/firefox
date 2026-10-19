import Transport

namespace LanguageBreak

structure WordJob where
  owner : Nat
  first : Chunk
  rest : List Chunk
  wordPolicy : Nat
  linePolicy : Nat
  deriving DecidableEq, Repr

def WordJob.chunks (job : WordJob) : List Chunk := job.first :: job.rest

structure WordCall where
  owner : Nat
  units : List CodeUnit
  script : Bool
  wordPolicy : Nat
  linePolicy : Nat
  pieces : List BufferedPiece
  deriving DecidableEq, Repr

def wordReference (p : Providers) (job : WordJob) : WordCall :=
  ⟨job.owner,job.chunks.flatMap (fun chunk => chunk.storage.decode),
   reference p job.first.language,job.wordPolicy,job.linePolicy,job.chunks.map encodePiece⟩

def runWord (p : Providers) (cache : Cache) (old : WordLanguage) (job : WordJob) : WordCall × TransportState :=
  let result := transportChunks p (startWord p cache old job.first) job.rest
  (⟨job.owner,result.buffer.units,result.language.script,job.wordPolicy,job.linePolicy,result.buffer.pieces⟩,
   { result with language := flushLanguage result.language, buffer := {} })

def WordJob.Admitted (_p : Providers) (cache : Cache) (job : WordJob) : Prop :=
  job.first.storage.decode ≠ [] ∧ UniformChunks job.first.language job.rest ∧
  StableIdentity cache job.first.language

theorem completed_word_reference (p : Providers) (cache : Cache) (old : WordLanguage)
    (job : WordJob) (valid : cache.Valid p) (admitted : job.Admitted p cache) :
    (runWord p cache old job).1 = wordReference p job ∧
    (runWord p cache old job).2.cache.Valid p := by
  have result := nonempty_word_transport p cache old job.first job.rest valid admitted.2.2 admitted.2.1
  constructor
  · simp only [runWord,wordReference,WordJob.chunks]
    rw [result.2.2.1,result.1.2.2,result.2.2.2]
  · exact result.2.1

theorem completed_word_retains_script (p : Providers) (cache : Cache) (old : WordLanguage)
    (job : WordJob) :
    (runWord p cache old job).2.language.script = (runWord p cache old job).1.script := rfl

inductive WordEvent where
  | word (job : WordJob)
  | foreign (request : Request)
  | reset
  deriving DecidableEq, Repr

structure EventState where
  cache : Cache := {}
  language : WordLanguage := {}
  deriving DecidableEq, Repr

def stepWordEvent (p : Providers) (state : EventState) : WordEvent → List WordCall × EventState
  | .word job =>
    let result := runWord p state.cache state.language job
    ([result.1],⟨result.2.cache,result.2.language⟩)
  | .foreign request => ([],{state with cache := (resolve p state.cache request.tag).2})
  | .reset => ([],{state with language := flushLanguage state.language})

def runWordEvents (p : Providers) (state : EventState) : List WordEvent → List WordCall × EventState
  | [] => ([],state)
  | event::rest =>
    let next := stepWordEvent p state event
    let tail := runWordEvents p next.2 rest
    (next.1++tail.1,tail.2)

def eventReference (p : Providers) : WordEvent → List WordCall
  | .word job => [wordReference p job]
  | _ => []

def AdmittedEvents (p : Providers) (state : EventState) : List WordEvent → Prop
  | [] => True
  | event::rest =>
    (match event with
      | .word job => job.Admitted p state.cache
      | .foreign request => StableIdentity state.cache request.tag
      | .reset => True) ∧
    AdmittedEvents p (stepWordEvent p state event).2 rest

theorem word_event_correct (p : Providers) (state : EventState) (event : WordEvent)
    (valid : state.cache.Valid p)
    (admitted : match event with
      | .word job => job.Admitted p state.cache
      | .foreign request => StableIdentity state.cache request.tag
      | .reset => True) :
    (stepWordEvent p state event).1 = eventReference p event ∧
    (stepWordEvent p state event).2.cache.Valid p := by
  cases event with
  | word job =>
    have result := completed_word_reference p state.cache state.language job valid admitted
    exact ⟨by simp only [stepWordEvent,eventReference,result.1],result.2⟩
  | foreign request => exact ⟨rfl,resolve_valid p state.cache request.tag valid⟩
  | reset => exact ⟨rfl,valid⟩

theorem arbitrary_completed_words (p : Providers) (state : EventState) (events : List WordEvent)
    (valid : state.cache.Valid p) (admitted : AdmittedEvents p state events) :
    (runWordEvents p state events).1 = events.flatMap (eventReference p) ∧
    (runWordEvents p state events).2.cache.Valid p := by
  induction events generalizing state with
  | nil => exact ⟨rfl,valid⟩
  | cons event rest ih =>
    have step := word_event_correct p state event valid admitted.1
    have tail := ih (stepWordEvent p state event).2 step.2 admitted.2
    exact ⟨by simp only [runWordEvents,List.flatMap_cons,step.1,tail.1],tail.2⟩

theorem constructor_events (p : Providers) (events : List WordEvent)
    (admitted : AdmittedEvents p {} events) :
    (runWordEvents p {} events).1 = events.flatMap (eventReference p) ∧
    (runWordEvents p {} events).2.cache.Valid p :=
  arbitrary_completed_words p {} events (empty_valid p) admitted

end LanguageBreak
