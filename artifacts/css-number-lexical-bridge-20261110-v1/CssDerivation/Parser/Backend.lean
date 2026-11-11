import CssDerivation.Backend

namespace CssParserLowering

open CssDerivation

inductive Program : Type → Type 1 where
  | legacy {α : Type} : CssDerivation.Program α → Program α
  | getState : Program State
  | putState : State → Program Unit
  | bind {α β : Type} : Program α → (α → Program β) → Program β

def pure (value : α) : Program α := .legacy (.pure value)

def run : Program α → State → α × State
  | .legacy program, state => CssDerivation.run program state
  | .getState, state => (state, state)
  | .putState next, _ => ((), next)
  | .bind first next, state =>
    let result := run first state
    run (next result.1) result.2

def transaction (program : Program (Option α)) : Program (Option α) :=
  .bind .getState fun before =>
  .bind program fun result =>
    match result with
    | some value => pure (some value)
    | none => .bind (.putState before) fun _ => pure none

def observed (initial : State) : Option (α × State) → Option α × State
  | none => (none, initial)
  | some (value, final) => (some value, final)

end CssParserLowering
