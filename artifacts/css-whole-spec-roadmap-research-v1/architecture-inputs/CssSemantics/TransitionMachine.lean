import Std

namespace CssSemantics.TransitionMachine

variable {State Token : Type}

def run (advance : State → Token → Option State) (state : State) : List Token → Option State
  | [] => some state
  | token :: rest => (advance state token).bind fun next => run advance next rest

inductive Runs (Step : State → Token → State → Prop) : State → List Token → State → Prop where
  | nil (state) : Runs Step state [] state
  | cons {before middle after token rest} : Step before token middle → Runs Step middle rest after →
      Runs Step before (token :: rest) after

theorem run_iff (advance : State → Token → Option State) (Step : State → Token → State → Prop)
    (correspondence : ∀ before token after, advance before token = some after ↔ Step before token after)
    (tokens : List Token) (before after : State) :
    run advance before tokens = some after ↔ Runs Step before tokens after := by
  induction tokens generalizing before with
  | nil =>
      constructor
      · intro h; cases h; exact .nil _
      · intro h; cases h; rfl
  | cons token rest ih =>
      simp only [run, Option.bind_eq_some_iff, correspondence, ih]
      constructor
      · rintro ⟨middle, first, tail⟩; exact .cons first tail
      · intro h; cases h with | cons first tail => exact ⟨_, first, tail⟩

theorem Runs.preserves (Step : State → Token → State → Prop)
    (ValidState : State → Prop) (ValidToken : Token → Prop)
    (advance : ∀ before token after, Step before token after →
      ValidState before → ValidToken token → ValidState after)
    {before after : State} {tokens : List Token} (h : Runs Step before tokens after)
    (initial : ValidState before) (valid : ∀ token ∈ tokens, ValidToken token) : ValidState after := by
  induction h with
  | nil => exact initial
  | @cons before middle after token rest step _ ih =>
      exact ih (advance before token middle step initial (valid token (by simp)))
        (fun t member => valid t (List.mem_cons_of_mem _ member))

end CssSemantics.TransitionMachine
