import CssSemantics.CssScopeImportSingleRun
import CssSemantics.CssScopeImportInputs

namespace CssSemantics.CssScopeImportRun

open CssScopeImportInputs
abbrev Rules := CssScopeImportSingleRun.Rules

structure Attempt where
  userAgent : CssScopeImportSingleRun.Attempt
  user : CssScopeImportSingleRun.Attempt
  author : CssScopeImportSingleRun.Attempt
  rules : Option Rules
  deriving Repr

def count (attempt : CssScopeImportSingleRun.Attempt) : Nat :=
  (attempt.rules.map List.length).getD 0

def combine (userAgent user author : CssScopeImportSingleRun.Attempt) : Option Rules := do
  let first ← userAgent.rules
  let middle ← user.rules
  let last ← author.rules
  pure (first ++ middle ++ last)

def run (medium : CssGlobalMedia.Medium) (inputs : Inputs) : Attempt :=
  let first := CssScopeImportSingleRun.run .userAgent 0 medium inputs.userAgent.environment inputs.userAgent.roots
  let middle := CssScopeImportSingleRun.run .user (count first) medium inputs.user.environment inputs.user.roots
  let last := CssScopeImportSingleRun.run .author (count first + count middle) medium inputs.author.environment inputs.author.roots
  ⟨first, middle, last, combine first middle last⟩

def Attempted (medium : CssGlobalMedia.Medium) (inputs : Inputs) (attempt : Attempt) : Prop :=
  CssScopeImportSingleRun.Attempted .userAgent 0 medium inputs.userAgent.environment inputs.userAgent.roots attempt.userAgent ∧
  CssScopeImportSingleRun.Attempted .user (count attempt.userAgent) medium inputs.user.environment inputs.user.roots attempt.user ∧
  CssScopeImportSingleRun.Attempted .author (count attempt.userAgent + count attempt.user) medium inputs.author.environment inputs.author.roots attempt.author ∧
  attempt.rules = combine attempt.userAgent attempt.user attempt.author

theorem run_sound (medium inputs) : Attempted medium inputs (run medium inputs) :=
  ⟨CssScopeImportSingleRun.run_sound .., CssScopeImportSingleRun.run_sound .., CssScopeImportSingleRun.run_sound .., rfl⟩

theorem Attempted.result {medium inputs attempt}
    (known : Attempted medium inputs attempt) : run medium inputs = attempt := by
  rcases known with ⟨first, middle, last, rules⟩
  cases attempt
  simp_all [run, first.result, middle.result, last.result]

theorem run_iff (medium inputs attempt) : run medium inputs = attempt ↔
    Attempted medium inputs attempt :=
  ⟨fun same => same ▸ run_sound medium inputs, Attempted.result⟩

def Attempt.at (attempt : Attempt) : CascadeOrigin → CssScopeImportSingleRun.Attempt
  | .userAgent => attempt.userAgent
  | .user => attempt.user
  | .author => attempt.author

def Attempt.offset (attempt : Attempt) : CascadeOrigin → Nat
  | .userAgent => 0
  | .user => count attempt.userAgent
  | .author => count attempt.userAgent + count attempt.user

theorem Attempted.at {medium inputs attempt}
    (known : Attempted medium inputs attempt) (origin : CascadeOrigin) :
    CssScopeImportSingleRun.Attempted origin (attempt.offset origin) medium (inputs.at origin).environment
      (inputs.at origin).roots (attempt.at origin) := by
  cases origin
  · exact known.1
  · exact known.2.1
  · exact known.2.2.1

theorem Attempted.no_partial {medium inputs attempt}
    (known : Attempted medium inputs attempt) {origin}
    (absent : (attempt.at origin).rules = none) : attempt.rules = none := by
  rw [known.2.2.2]
  cases origin <;> simp_all [Attempt.at, combine]

theorem Attempted.completed {medium inputs attempt rules}
    (known : Attempted medium inputs attempt) (present : attempt.rules = some rules) :
    ∃ first middle last, attempt.userAgent.rules = some first ∧ attempt.user.rules = some middle ∧
      attempt.author.rules = some last ∧ rules = first ++ middle ++ last := by
  rw [known.2.2.2] at present
  simp only [combine, bind, pure, Option.bind_eq_some_iff, Option.some.injEq] at present
  obtain ⟨first, hFirst, middle, hMiddle, last, hLast, same⟩ := present
  exact ⟨first, middle, last, hFirst, hMiddle, hLast, same.symm⟩

end CssSemantics.CssScopeImportRun
