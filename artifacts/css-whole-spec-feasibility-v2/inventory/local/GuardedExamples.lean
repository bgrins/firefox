import CssSemantics.GuardedNormalization
import CssSemantics.VariablesSolver

namespace CssSemantics.GuardedExamples

def unused : VariableBindings Nat := ⟨[
  ("--a", .fallback "--b" (.reference "--a")), ("--b", .literal [1])], by decide⟩

def self : VariableBindings Nat := ⟨[("--a", .fallback "--a" (.literal [1]))], by decide⟩

def pair : VariableBindings Nat := ⟨[
  ("--a", .fallback "--b" (.literal [1])), ("--b", .reference "--a"),
  ("--c", .fallback "--a" (.literal [2]))], by decide⟩

def missingFirst : VariableBindings Nat := ⟨[
  ("--a", .append (.reference "--missing") (.reference "--b")),
  ("--b", .fallback "--a" (.literal [1]))], by decide⟩

def missingLast : VariableBindings Nat := ⟨[
  ("--a", .append (.reference "--b") (.reference "--missing")),
  ("--b", .fallback "--a" (.literal [1]))], by decide⟩

def markedFirst : VariableBindings Nat := ⟨[
  ("--a", .append (.reference "--a") (.reference "--b")),
  ("--b", .fallback "--a" (.literal [1]))], by decide⟩

def shared : VariableBindings Nat := ⟨[
  ("--base", .literal [3]), ("--empty", .literal []),
  ("--twice", .append (.reference "--base") (.reference "--base")),
  ("--choice", .fallback "--empty" (.reference "--choice")),
  ("--fallback", .fallback "--missing" (.literal [4])),
  ("--failed", .append (.reference "--missing") (.literal [5]))], by decide⟩

structure Case where
  name : String
  bindings : VariableBindings Nat
  property : String
  expected : Option (List Nat)
  base : String → Option (List Nat) := fun _ => none

def cases : List Case := [
  ⟨"guarded literal", shared, "--base", some [3], fun _ => none⟩,
  ⟨"guarded missing", shared, "--missing", none, fun _ => none⟩,
  ⟨"guarded inherited base", shared, "--missing", some [8], fun _ => some [8]⟩,
  ⟨"guarded empty", shared, "--empty", some [], fun _ => none⟩,
  ⟨"guarded empty skips cyclic fallback", shared, "--choice", some [], fun _ => none⟩,
  ⟨"guarded unused fallback cycle", unused, "--a", some [1], fun _ => none⟩,
  ⟨"guarded self fallback cannot rescue owner", self, "--a", none, fun _ => none⟩,
  ⟨"guarded first cycle owner", pair, "--a", none, fun _ => none⟩,
  ⟨"guarded second cycle owner", pair, "--b", none, fun _ => none⟩,
  ⟨"guarded outside consumer recovers", pair, "--c", some [2], fun _ => none⟩,
  ⟨"guarded missing first starting a", missingFirst, "--a", none, fun _ => none⟩,
  ⟨"guarded missing first starting b", missingFirst, "--b", none, fun _ => none⟩,
  ⟨"guarded missing last starting a", missingLast, "--a", none, fun _ => none⟩,
  ⟨"guarded missing last starting b", missingLast, "--b", none, fun _ => none⟩,
  ⟨"guarded marked first starting a", markedFirst, "--a", none, fun _ => none⟩,
  ⟨"guarded marked first starting b", markedFirst, "--b", none, fun _ => none⟩,
  ⟨"guarded repeated shared dependency", shared, "--twice", some [3, 3], fun _ => none⟩,
  ⟨"guarded missing fallback", shared, "--fallback", some [4], fun _ => none⟩,
  ⟨"guarded invalid concatenation", shared, "--failed", none, fun _ => none⟩,
  ⟨"guarded case sensitive names", shared, "--Base", none, fun _ => none⟩,
  ⟨"guarded cycle blocks base", self, "--a", none, fun _ => some [8]⟩,
  ⟨"guarded local literal overrides base", shared, "--base", some [3], fun _ => some [8]⟩]

def checks : Bool := cases.all fun test =>
  GuardedSolver.compute test.bindings test.base test.property == test.expected

theorem checks_pass : checks = true := by
  unfold checks
  simp only [GuardedSolver.compute_eq_expand]
  decide

theorem snapshot_draft_difference : unused.compute "--a" = none ∧
    GuardedSolver.compute unused (fun _ => none) "--a" = some [1] := by
  constructor
  · exact unused.compute_cyclic _ ((unused.cyclicBool_iff _).mp (by decide))
  · rw [GuardedSolver.compute_eq_expand]
    decide

def stateCases : List (String × List String × List String × String × List String) := [
  ("guarded exact repeated interval", ["b", "a", "c"], [], "a", ["b", "a"]),
  ("guarded old mark survives interval", ["b", "a", "c"], ["c"], "a", ["c", "b", "a"]),
  ("guarded self interval excludes callers", ["b", "a", "c"], [], "b", ["b"])]

def stateChecks : Bool := stateCases.all fun (_, active, marks, name, expected) =>
  (GuardedSolver.resolve (fun _ => (none : Option (List Nat))) [] active marks name).2 == expected

theorem stateChecks_pass : stateChecks = true := by
  unfold stateChecks
  have normalized : ∀ active marks name,
      GuardedSolver.resolve (fun _ => (none : Option (List Nat))) [] active marks name =
        GuardedSolver.expand (fun _ => none) 0 [] (by decide) active marks name :=
    fun active marks name => (GuardedSolver.expand_eq_resolve 0 [] (by decide) _ active marks name).symm
  simp only [normalized]
  decide

end CssSemantics.GuardedExamples
