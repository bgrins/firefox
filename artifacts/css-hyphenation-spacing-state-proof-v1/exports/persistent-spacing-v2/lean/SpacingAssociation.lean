import PropertySession

namespace SpacingAssociation
open HyphenSpacingValues HyphenSpacingPhases HyphenTabValues HyphenSpacingTabComposition

structure Environment (Value : Type) where
  numeric : Numeric Value
  singletonQueries : Nat → Input Value
  providers : Providers Value
  start : Nat
  reflowing : Bool
  lineContainer : Bool

def enabled (input : Input Value) : Bool :=
  !(input.textCombined || input.ignoreTabs || !input.tabWidthPositive)

def request (environment : Environment Value) (input : Input Value) : PropertySession.Request :=
  ⟨environment.start,input.queryEnd,enabled input,environment.reflowing,environment.lineContainer⟩

def advance (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) : PropertySession.Session Value :=
  PropertySession.query environment.numeric (joinedProviders environment.singletonQueries environment.providers)
    (request environment input) session

def applied (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) : Input Value :=
  if enabled input then
    {input with tabCache := (advance environment input session).tab.cache.map fun cache => selectedEntries cache input.tabFirst}
  else input

def query (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) : PropertySession.Session Value × Result Value :=
  (advance environment input session,native (applied environment input session))

theorem query_refines_complete_values (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) :
    ((query environment input session).1.tab,(query environment input session).2) =
      calculateAndApply environment.numeric environment.singletonQueries environment.providers
        ⟨environment.reflowing,environment.lineContainer,environment.start,input.queryEnd,session.property⟩ session.tab input := by
  simp only [query,advance,PropertySession.query_tab,request,applied]
  cases combined : input.textCombined <;> cases ignored : input.ignoreTabs <;>
    cases positive : input.tabWidthPositive <;>
    simp [enabled,combined,ignored,positive,calculateAndApply]

theorem query_preserves_association (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) (associated : PropertySession.Associated session) :
    PropertySession.Associated (query environment input session).1 :=
  PropertySession.query_associated _ _ _ _ associated

theorem exact_ordered_values (environment : Environment Value) (input : Input Value)
    (session : PropertySession.Session Value) (index : Nat) (side : Side) :
    (query environment input session).2.store index side =
      (valuesAt (trace (applied environment input session)) index side).foldl
        input.config.arithmetic.add input.config.arithmetic.zero := by
  have result := complete_pointwise (applied environment input session) index side
  cases active : enabled input <;> simpa [query,applied,active] using result

def history (environment : Environment Value) (session : PropertySession.Session Value) :
    List (Input Value) → PropertySession.Session Value × List (Result Value)
  | [] => (session,[])
  | input::rest =>
    let answer := query environment input session
    let later := history environment answer.1 rest
    (later.1,answer.2::later.2)

theorem history_preserves_association (environment : Environment Value)
    (session : PropertySession.Session Value) (inputs : List (Input Value))
    (associated : PropertySession.Associated session) :
    PropertySession.Associated (history environment session inputs).1 := by
  induction inputs generalizing session with
  | nil => exact associated
  | cons input rest ih => exact ih _ (query_preserves_association _ _ _ associated)

theorem history_answer_count (environment : Environment Value)
    (session : PropertySession.Session Value) (inputs : List (Input Value)) :
    (history environment session inputs).2.length = inputs.length := by
  induction inputs generalizing session with
  | nil => rfl
  | cons input rest ih => simpa [history] using congrArg Nat.succ (ih (query environment input session).1)

end SpacingAssociation
