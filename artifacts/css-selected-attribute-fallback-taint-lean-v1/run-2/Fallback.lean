import Taint
import CssSemantics.Variables

namespace SelectedAttributeFallback
open RetainedAggregateTaint CssSemantics

inductive Kind where
  | attr | other
  deriving DecidableEq, Repr

structure Value where
  bytes : List UInt8
  origins : List Nat
  deriving DecidableEq, Repr

def mark (kind : Kind) (origin : Nat) (value : Value) : Value :=
  { value with origins := if kind == .attr then origin :: value.origins else value.origins }

inductive Expr where
  | literal : List UInt8 → Expr
  | append : Expr → Expr → Expr
  | reference : Kind → Nat → String → Expr
  | fallback : Kind → Nat → String → Expr → Expr
  deriving DecidableEq, Repr

def erase : Expr → VariableExpr UInt8
  | .literal bytes => .literal bytes
  | .append left right => .append (erase left) (erase right)
  | .reference _ _ name => .reference name
  | .fallback _ _ name body => .fallback name (erase body)

def evaluate (env : String → Option Value) : Expr → Option Value
  | .literal bytes => some ⟨bytes, []⟩
  | .append left right => do
      let l ← evaluate env left
      let r ← evaluate env right
      pure ⟨l.bytes ++ r.bytes, l.origins ++ r.origins⟩
  | .reference kind origin name => (env name).map (mark kind origin)
  | .fallback kind origin name body =>
      (match env name with
       | some value => some value
       | none => evaluate env body).map (mark kind origin)

def chunk (value : Value) (origin : Nat) : Chunk :=
  ⟨value.bytes, [], !value.origins.isEmpty, origin⟩

theorem mark_bytes (kind : Kind) (origin : Nat) (value : Value) :
    (mark kind origin value).bytes = value.bytes := rfl

theorem evaluate_erasure (env : String → Option Value) (expression : Expr) :
    (evaluate env expression).map Value.bytes =
      (erase expression).substitute (fun name => (env name).map Value.bytes) := by
  induction expression with
  | literal bytes => rfl
  | append left right ihLeft ihRight =>
      simp only [evaluate, erase, VariableExpr.substitute, ← ihLeft, ← ihRight]
      cases evaluate env left <;> cases evaluate env right <;> rfl
  | reference kind origin name =>
      cases found : env name <;> simp [evaluate, erase, VariableExpr.substitute, found, mark]
  | fallback kind origin name body ih =>
      simp only [evaluate, erase, VariableExpr.substitute]
      cases found : env name with
      | some value => rfl
      | none => simpa [Option.map_map, Function.comp_def, mark] using ih

theorem selected_fallback (env : String → Option Value) (missing : env name = none)
    (success : evaluate env body = some value) :
    evaluate env (.fallback kind origin name body) = some (mark kind origin value) := by
  simp [evaluate, missing, success]

theorem failed_fallback (env : String → Option Value) (missing : env name = none)
    (failure : evaluate env body = none) :
    evaluate env (.fallback kind origin name body) = none := by
  simp [evaluate, missing, failure]

theorem discarded_fallback (env : String → Option Value) (found : env name = some value)
    (left right : Expr) :
    evaluate env (.fallback kind origin name left) = some (mark kind origin value) ∧
    evaluate env (.fallback kind origin name left) =
      evaluate env (.fallback kind origin name right) := by
  simp [evaluate, found]

theorem selected_attr_origin (env : String → Option Value) (missing : env name = none)
    (success : evaluate env body = some value) :
    evaluate env (.fallback .attr origin name body) =
      some ⟨value.bytes, origin :: value.origins⟩ := by
  simpa [mark] using selected_fallback env missing success (kind := .attr) (origin := origin)

theorem selected_other_preserves_only_child (env : String → Option Value)
    (missing : env name = none) (success : evaluate env body = some value) :
    evaluate env (.fallback .other origin name body) = some value := by
  simpa [mark] using selected_fallback env missing success (kind := .other) (origin := origin)

theorem nested_attr_marks_survive (outer inner : Nat) (value : Value) :
    (mark .attr outer (mark .attr inner value)).origins = outer :: inner :: value.origins := by
  simp [mark]

theorem mark_keeps_child_origin (kind : Kind) (origin child : Nat) (value : Value)
    (member : child ∈ value.origins) : child ∈ (mark kind origin value).origins := by
  cases kind <;> simp [mark, member]

theorem run_preserves_true (state : Retained) (tail : List Chunk)
    (tainted : state.aggregate = true) : (run state tail).aggregate = true := by
  induction tail generalizing state with
  | nil => exact tainted
  | cons c cs ih => apply ih; simp [append, tainted]

theorem attr_publication_survives_tail (state : Retained) (tail : List Chunk)
    (origin occurrence : Nat) (value : Value) :
    (publish (run (append state (chunk (mark .attr origin value) occurrence)) tail)).tainted = true := by
  apply run_preserves_true
  simp [append, chunk, mark]

theorem selected_fallback_publication (env : String → Option Value)
    (missing : env name = none) (success : evaluate env body = some value)
    (resolved : evaluate env (.fallback .attr origin name body) = some output)
    (state : Retained) (tail : List Chunk) (occurrence : Nat) :
    (publish (run (append state (chunk output occurrence)) tail)).tainted = true := by
  have selected := selected_fallback env missing success (kind := .attr) (origin := origin)
  rw [selected] at resolved
  cases Option.some.inj resolved
  exact attr_publication_survives_tail state tail origin occurrence value

theorem selected_fallback_alias (env : String → Option Value)
    (missing : env name = none) (success : evaluate env body = some value)
    (resolved : evaluate env (.fallback .attr origin name body) = some output)
    (state : Retained) (tail : List Chunk) (occurrence aliasOrigin : Nat) :
    (alias (publish (run (append state (chunk output occurrence)) tail)) aliasOrigin).tainted = true :=
  selected_fallback_publication env missing success resolved state tail occurrence

def absent : String → Option Value := fun _ => none
def clean : Value := ⟨[102, 111, 111], []⟩
def literalFallback : Expr := .fallback .attr 7 "missing" (.literal clean.bytes)
def omittedOuter : Option Value := evaluate absent (.literal clean.bytes)
def fallbackValue : Value := mark .attr 7 clean
def emptyFallback : Value := mark .attr 8 ⟨[], []⟩
def mixed := run initial [chunk emptyFallback 8, literal]

theorem omitted_outer_counterexample :
    evaluate absent literalFallback = some fallbackValue ∧
    (evaluate absent literalFallback).map Value.bytes = omittedOuter.map Value.bytes ∧
    (publish (append initial (chunk fallbackValue 7))).tainted = true ∧
    (publish (append initial (chunk clean 7))).tainted = false := by decide

theorem empty_fallback_custom_only :
    mixed.ranges = [] ∧ (publish mixed).tainted = true ∧
    directBlocked mixed ⟨0, 3⟩ = false := by decide

theorem nonempty_fallback_interval :
    (append initial (chunk fallbackValue 7)).ranges = [⟨0, 3⟩] ∧
    directBlocked (append initial (chunk fallbackValue 7)) ⟨0, 3⟩ = true := by decide

def primaryEnv : String → Option Value := fun _ => some clean
def dirtyUnused : Expr := .fallback .attr 99 "missing" (.literal [])

theorem discarded_attr_body_does_not_taint_var :
    evaluate primaryEnv (.fallback .other 2 "valid" dirtyUnused) = some clean := by decide

theorem attr_primary_still_has_own_origin :
    evaluate primaryEnv (.fallback .attr 7 "valid" dirtyUnused) = some fallbackValue := by decide

end SelectedAttributeFallback
