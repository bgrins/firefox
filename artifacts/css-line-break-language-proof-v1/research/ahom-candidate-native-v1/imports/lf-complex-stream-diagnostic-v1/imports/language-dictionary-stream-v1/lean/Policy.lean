import Words

namespace LanguageBreak

structure FlushRequest where
  owner : Nat
  language : WordLanguage
  buffer : WordBuffer
  wordPolicy : Fin 3
  linePolicy : Fin 5
  continuation : Bool
  deriving DecidableEq, Repr

structure PolicyState where
  owner : Nat
  transport : TransportState
  wordPolicy : Fin 3
  linePolicy : Fin 5
  breakHere : Bool
  afterSpace : Bool
  continuation : Bool
  mightBreak : Bool
  deriving DecidableEq, Repr

def PolicyState.request (state : PolicyState) : FlushRequest :=
  ⟨state.owner,state.transport.language,state.transport.buffer,state.wordPolicy,state.linePolicy,state.continuation⟩

def clearWord (state : PolicyState) : PolicyState :=
  let next : TransportState := ⟨state.transport.cache,flushLanguage state.transport.language,{}⟩
  {state with transport := next, continuation := false, mightBreak := false}

def setWordPolicy (state : PolicyState) (policy : Fin 3) : List FlushRequest × PolicyState :=
  if policy ≠ state.wordPolicy ∧ state.transport.buffer.units ≠ [] then
    ([state.request],{clearWord state with wordPolicy := policy,breakHere := state.breakHere || state.wordPolicy.val == 1})
  else ([],{state with wordPolicy := policy})

def setLinePolicy (state : PolicyState) (policy : Fin 5) : List FlushRequest × PolicyState :=
  if policy ≠ state.linePolicy ∧ state.transport.buffer.units ≠ [] then
    ([state.request],{clearWord state with linePolicy := policy,breakHere := state.breakHere || state.linePolicy.val == 4})
  else ([],{state with linePolicy := policy})

theorem word_change_flushes_prior_policy (state : PolicyState) (policy : Fin 3)
    (changed : policy ≠ state.wordPolicy) (pending : state.transport.buffer.units ≠ []) :
    (setWordPolicy state policy).1 = [state.request] ∧
    (setWordPolicy state policy).2.transport.buffer.units = [] ∧
    (setWordPolicy state policy).2.wordPolicy = policy := by
  simp [setWordPolicy,changed,pending,clearWord]

theorem line_change_flushes_prior_policy (state : PolicyState) (policy : Fin 5)
    (changed : policy ≠ state.linePolicy) (pending : state.transport.buffer.units ≠ []) :
    (setLinePolicy state policy).1 = [state.request] ∧
    (setLinePolicy state policy).2.transport.buffer.units = [] ∧
    (setLinePolicy state policy).2.linePolicy = policy := by
  simp [setLinePolicy,changed,pending,clearWord]

theorem same_word_policy_preserves (state : PolicyState) :
    setWordPolicy state state.wordPolicy = ([],state) := by simp [setWordPolicy]

theorem same_line_policy_preserves (state : PolicyState) :
    setLinePolicy state state.linePolicy = ([],state) := by simp [setLinePolicy]

theorem clear_retains_script_and_outer_context (state : PolicyState) :
    (clearWord state).transport.language.script = state.transport.language.script ∧
    (clearWord state).transport.cache = state.transport.cache ∧
    (clearWord state).afterSpace = state.afterSpace ∧
    (clearWord state).breakHere = state.breakHere := by simp [clearWord,flushLanguage]

theorem clear_resets_word_ownership (state : PolicyState) :
    (clearWord state).transport.language.current = .absent ∧
    (clearWord state).transport.language.mixed = false ∧
    (clearWord state).transport.buffer = {} ∧
    (clearWord state).continuation = false ∧
    (clearWord state).mightBreak = false := by simp [clearWord,flushLanguage]

end LanguageBreak
