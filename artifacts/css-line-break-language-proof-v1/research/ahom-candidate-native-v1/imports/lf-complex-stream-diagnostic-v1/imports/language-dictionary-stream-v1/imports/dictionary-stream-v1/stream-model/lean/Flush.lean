import Policy
import Projection

namespace LanguageBreak

structure AuxLimits where
  word : Fin 256
  start : Fin 256
  finish : Fin 256
  deriving DecidableEq, Repr

structure BreakProviders where
  hasHyphenator : Tag → Bool
  segment : List CodeUnit → Fin 3 → Fin 5 → Bool → List BreakKind
  hyphenate : Tag → List CodeUnit → AuxLimits → List BreakKind → List BreakKind
  capitalize : List CodeUnit → List Bool

inductive FlushEvent where
  | segmentation (units : List CodeUnit) (word : Fin 3) (line : Fin 5) (script : Bool)
  | hyphenatorLookup (tag : Tag)
  | hyphenation (tag : Tag) (units : List CodeUnit) (limits : AuxLimits) (previous : List BreakKind)
  | capitalization (units : List CodeUnit)
  | breaks (sinkIdentity : Nat) (owner : Nat) (offset : Nat) (values : List BreakKind)
  | capitals (sinkIdentity : Nat) (owner : Nat) (offset : Nat) (values : List Bool)
  deriving DecidableEq, Repr

structure FlushResult where
  events : List FlushEvent
  state : PolicyState
  deriving DecidableEq, Repr

def segmentBuffered (providers : BreakProviders) (state : PolicyState) : List BreakKind × List FlushEvent :=
  let units := state.transport.buffer.units
  if state.linePolicy.val = 4 then (List.replicate units.length .normal,[])
  else if !state.mightBreak && state.wordPolicy.val != 1 then (List.replicate units.length .none,[])
  else (providers.segment units state.wordPolicy state.linePolicy state.transport.language.script,
    [.segmentation units state.wordPolicy state.linePolicy state.transport.language.script])

def hyphenateBuffered (providers : BreakProviders) (state : PolicyState) (limits : AuxLimits)
    (breaks : List BreakKind) : List BreakKind × List FlushEvent :=
  if state.transport.language.current ≠ .absent ∧ state.transport.language.mixed = false ∧
      state.transport.buffer.pieces.all (fun piece => piece.hyphenation) then
    let lookup := FlushEvent.hyphenatorLookup state.transport.language.current
    if providers.hasHyphenator state.transport.language.current then
      (providers.hyphenate state.transport.language.current state.transport.buffer.units limits breaks,
       [lookup,.hyphenation state.transport.language.current state.transport.buffer.units limits breaks])
    else (breaks,[lookup])
  else (breaks,[])

def emitBuffered (providers : BreakProviders) (units : List CodeUnit) (continuation : Bool)
    (breaks : List BreakKind) (offset : Nat) (first : Bool) (capitalized : Option (List Bool)) :
    List BufferedPiece → List FlushEvent
  | [] => []
  | piece::rest =>
    let next := offset+piece.units.length
    match piece.sinkOwner with
    | none => emitBuffered providers units continuation breaks next false capitalized rest
    | some owner =>
      let skip := if first then 1 else 0
      let masked := ((List.range piece.units.length).map fun i =>
        bufferedMask piece i (breaks[offset+i]?.getD .none)).drop skip
      let write := FlushEvent.breaks piece.sinkIdentity owner (piece.sinkOffset+skip) masked
      if !continuation && piece.capitalization then
        let values := capitalized.getD (providers.capitalize units)
        let event := FlushEvent.capitals piece.sinkIdentity owner piece.sinkOffset ((values.drop offset).take piece.units.length)
        let called := if capitalized.isNone then [FlushEvent.capitalization units] else []
        [write] ++ called ++ [event] ++ emitBuffered providers units continuation breaks next false (some values) rest
      else write :: emitBuffered providers units continuation breaks next false capitalized rest

def flushBuffered (providers : BreakProviders) (state : PolicyState) (limits : AuxLimits) : FlushResult :=
  let segmented := segmentBuffered providers state
  let hyphenated := hyphenateBuffered providers state limits segmented.1
  ⟨segmented.2 ++ hyphenated.2 ++ emitBuffered providers state.transport.buffer.units state.continuation
    hyphenated.1 0 true none state.transport.buffer.pieces,clearWord state⟩

theorem flush_clears_word (providers : BreakProviders) (state : PolicyState) (limits : AuxLimits) :
    (flushBuffered providers state limits).state.transport.buffer = {} ∧
    (flushBuffered providers state limits).state.transport.language.current = .absent ∧
    (flushBuffered providers state limits).state.transport.language.mixed = false := by
  simp [flushBuffered,clearWord,flushLanguage]

theorem flush_preserves_script_cache_context (providers : BreakProviders) (state : PolicyState) (limits : AuxLimits) :
    (flushBuffered providers state limits).state.transport.language.script = state.transport.language.script ∧
    (flushBuffered providers state limits).state.transport.cache = state.transport.cache ∧
    (flushBuffered providers state limits).state.breakHere = state.breakHere ∧
    (flushBuffered providers state limits).state.afterSpace = state.afterSpace := by
  simp [flushBuffered,clearWord,flushLanguage]

theorem uniform_buffer_segmentation_language (providers : BreakProviders) (state : PolicyState) (p : Providers)
    (tag : Tag) (aligned : Aligned p state.transport.language tag)
    (ordinary : state.linePolicy.val ≠ 4)
    (needed : state.mightBreak = true ∨ state.wordPolicy.val = 1) :
    (segmentBuffered providers state).2 =
      [.segmentation state.transport.buffer.units state.wordPolicy state.linePolicy (reference p tag)] := by
  rcases aligned with ⟨current,mixed,script⟩
  cases needed with
  | inl might => simp [segmentBuffered,ordinary,might,script]
  | inr breakAll => simp [segmentBuffered,ordinary,breakAll,script]

end LanguageBreak
