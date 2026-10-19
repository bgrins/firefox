import Append

namespace LanguageBreak

def initialStream (cache : Cache := {}) : StreamState :=
  ⟨⟨0,⟨cache,{},{}⟩,⟨0,by decide⟩,⟨0,by decide⟩,false,false,false,false⟩,
   ⟨⟨0,by decide⟩,⟨0,by decide⟩,⟨0,by decide⟩⟩⟩

inductive Operation where
  | append (chunk : Chunk)
  | word (value : Fin 3)
  | line (value : Fin 5)
  | limits (value : AuxLimits)
  | continuation (value : Bool)
  | whitespace (suppressInside : Bool)
  | reset
  deriving DecidableEq, Repr

def wordStream (providers : StreamProviders) (state : StreamState) (word : Fin 3) : StreamResult :=
  if word ≠ state.policy.wordPolicy ∧ !state.policy.transport.buffer.units.isEmpty then
    let result := flushStream providers state
    ⟨{result.state with policy := {result.state.policy with wordPolicy := word, breakHere := result.state.policy.breakHere || state.policy.wordPolicy.val == 1}},result.events⟩
  else ⟨{state with policy := {state.policy with wordPolicy := word}},[]⟩

def lineStream (providers : StreamProviders) (state : StreamState) (line : Fin 5) : StreamResult :=
  if line ≠ state.policy.linePolicy ∧ !state.policy.transport.buffer.units.isEmpty then
    let result := flushStream providers state
    ⟨{result.state with policy := {result.state.policy with linePolicy := line, breakHere := result.state.policy.breakHere || state.policy.linePolicy.val == 4}},result.events⟩
  else ⟨{state with policy := {state.policy with linePolicy := line}},[]⟩

def whitespaceStream (providers : StreamProviders) (state : StreamState) (suppressInside : Bool) : StreamResult :=
  let result := flushStream providers state
  let policy := result.state.policy
  let space := !suppressInside
  ⟨{result.state with policy := {policy with afterSpace := space, breakHere := policy.breakHere || (policy.afterSpace && !space)}},result.events⟩

def resetStream (providers : StreamProviders) (state : StreamState) : StreamResult × Bool :=
  let result := flushStream providers state
  let trailing := result.state.policy.breakHere || result.state.policy.afterSpace
  (⟨{result.state with policy := {result.state.policy with breakHere := false,afterSpace := false}},result.events⟩,trailing)

def stepStream (providers : StreamProviders) (state : StreamState) : Operation → StreamResult
  | .append chunk => appendStream providers chunk state
  | .word word => wordStream providers state word
  | .line line => lineStream providers state line
  | .limits limits => ⟨{state with limits := limits},[]⟩
  | .continuation value => ⟨{state with policy := {state.policy with continuation := value}},[]⟩
  | .whitespace inside => whitespaceStream providers state inside
  | .reset => (resetStream providers state).1

def runStream (providers : StreamProviders) : StreamResult → List Operation → StreamResult
  | result,[] => result
  | result,op::rest =>
    let next := stepStream providers result.state op
    runStream providers ⟨next.state,result.events++next.events⟩ rest

theorem delegation_matches_widened (providers : StreamProviders) (chunk : Chunk) (state : StreamState)
    (bytes : List (Fin 256)) (stored : chunk.storage = .bytes bytes)
    (auxiliary : chunk.capitalization = true ∨ chunk.hyphenation = true) :
    appendStream providers chunk state = appendStream providers chunk.widen state := by
  rcases auxiliary with caps | hyphen
  · simp [appendStream,stored,caps,Chunk.widen,StoredUnits.widen]
  · simp [appendStream,stored,hyphen,Chunk.widen,StoredUnits.widen]

theorem reset_retains_script (providers : StreamProviders) (state : StreamState) :
    (resetStream providers state).1.state.policy.transport.language.script =
      state.policy.transport.language.script := by
  simp [resetStream,flushStream,flushBuffered,clearWord,flushLanguage]

theorem constructor_cache_owner (cache : Cache) :
    (initialStream cache).policy.transport.cache = cache := rfl

end LanguageBreak
