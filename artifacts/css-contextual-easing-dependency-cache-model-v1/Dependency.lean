import Std

namespace ContextualEasing

inductive Field where
  | ownFont | parentFont | siblingIndex | siblingCount
  deriving DecidableEq, Repr

abbrev Context := Field → Nat

inductive Expr where
  | literal (n : Nat)
  | read (f : Field)
  | add (a b : Expr)
  | mul (a b : Expr)
  | min (a b : Expr)
  | divConst (a : Expr) (divisor : Nat)
  deriving Repr

def Expr.eval (c : Context) : Expr → Nat
  | .literal n => n
  | .read f => c f
  | .add a b => a.eval c + b.eval c
  | .mul a b => a.eval c * b.eval c
  | .min a b => Nat.min (a.eval c) (b.eval c)
  | .divConst a divisor => a.eval c / divisor

def Expr.support : Expr → List Field
  | .literal _ => []
  | .read f => [f]
  | .add a b | .mul a b | .min a b => a.support ++ b.support
  | .divConst a _ => a.support

def Agree (fields : List Field) (a b : Context) : Prop :=
  ∀ f, f ∈ fields → a f = b f

theorem expr_locality (e : Expr) (a b : Context)
    (h : Agree e.support a b) : e.eval a = e.eval b := by
  induction e with
  | literal n => rfl
  | read f => exact h f (by simp [Expr.support])
  | divConst x divisor hx => exact congrArg (fun n => n / divisor) (hx h)
  | add x y hx hy | mul x y hx hy | min x y hx hy =>
    have left : Agree x.support a b := fun f hf => h f (by simp [Expr.support, hf])
    have right : Agree y.support a b := fun f hf => h f (by simp [Expr.support, hf])
    simp only [Expr.eval, hx left, hy right]

def evaluate (parameters : List Expr) (c : Context) : List Nat :=
  parameters.map (Expr.eval c)

def support (parameters : List Expr) : List Field :=
  parameters.flatMap Expr.support

theorem parameters_locality (parameters : List Expr) (a b : Context)
    (h : Agree (support parameters) a b) : evaluate parameters a = evaluate parameters b := by
  induction parameters with
  | nil => rfl
  | cons e rest ih =>
    have he : Agree e.support a b := fun f hf => h f (by simp [support, hf])
    have hr : Agree (support rest) a b := fun f hf => h f (by simpa [support] using Or.inr hf)
    simp only [evaluate, List.map_cons]
    rw [expr_locality e a b he]
    exact congrArg (List.cons (e.eval b)) (ih hr)

def key (mask : List Field) (c : Context) : Field → Option Nat :=
  fun f => if f ∈ mask then some (c f) else none

theorem key_agreement (mask : List Field) (a b : Context)
    (h : key mask a = key mask b) : Agree mask a b := by
  intro f hf
  have eq := congrFun h f
  simpa [key, hf] using eq

def reuse (parameters : List Expr) (_mask : List Field) (old now : Context)
    (hit : Bool) : List Nat :=
  if hit then evaluate parameters old else evaluate parameters now

theorem cache_sound (parameters : List Expr) (mask : List Field) (old now : Context)
    (covered : ∀ f, f ∈ support parameters → f ∈ mask)
    (hit : Bool) (honest : hit = true → key mask old = key mask now) :
    reuse parameters mask old now hit = evaluate parameters now := by
  cases hit with
  | false => rfl
  | true =>
    apply parameters_locality
    exact fun f hf => key_agreement mask old now (honest rfl) f (covered f hf)

def before : Context
  | .ownFont => 32
  | .parentFont => 16
  | .siblingIndex => 2
  | .siblingCount => 3

def after : Context
  | .ownFont => 48
  | .parentFont => 16
  | .siblingIndex => 2
  | .siblingCount => 4

def linearStop : List Expr := [.literal 0, .literal 0, .read .ownFont]
def pseudoSteps : List Expr := [.add (.literal 1) (.divConst (.read .ownFont) 16)]
def countSteps : List Expr := [.read .siblingCount]

theorem omitted_second_position :
    key [] before = key [] after ∧
    evaluate linearStop before ≠ evaluate linearStop after := by
  constructor
  · funext f; simp [key]
  · decide

theorem parent_font_is_not_pseudo_font :
    key [.parentFont] before = key [.parentFont] after ∧
    evaluate pseudoSteps before = [3] ∧ evaluate pseudoSteps after = [4] := by
  constructor
  · funext f; cases f <;> rfl
  · decide

theorem pseudo_first_snapshot_wrong_binding :
    evaluate pseudoSteps before = [3] ∧
    evaluate [.add (.literal 1) (.divConst (.read .parentFont) 16)] before = [2] := by decide

theorem index_is_not_count :
    key [.siblingIndex] before = key [.siblingIndex] after ∧
    evaluate countSteps before ≠ evaluate countSteps after := by
  constructor
  · funext f; cases f <;> rfl
  · decide

theorem field_support_does_not_identify_rule :
    support [.read .siblingIndex] = support [.add (.literal 1) (.read .siblingIndex)] ∧
    evaluate [.read .siblingIndex] before ≠
      evaluate [.add (.literal 1) (.read .siblingIndex)] before := by decide

structure Transition where
  context : Context
  captured : Option (List Nat)

inductive Event where
  | contextChanged (c : Context)
  | start

def advance (parameters : List Expr) (s : Transition) : Event → Transition
  | .contextChanged c => { s with context := c }
  | .start => { s with captured := some (evaluate parameters s.context) }

def run (parameters : List Expr) (s : Transition) (events : List Event) : Transition :=
  events.foldl (advance parameters) s

theorem context_changes_retain_capture (parameters : List Expr) (s : Transition)
    (contexts : List Context) :
    (run parameters s (contexts.map Event.contextChanged)).captured = s.captured := by
  induction contexts generalizing s with
  | nil => rfl
  | cons c rest ih =>
    simpa [run, advance] using ih (advance parameters s (.contextChanged c))

theorem new_transition_captures_latest (parameters : List Expr) (s : Transition)
    (next : Context) :
    (run parameters s [.contextChanged next, .start]).captured =
      some (evaluate parameters next) := rfl

theorem property_refresh_is_not_effect_refresh :
    let started := advance countSteps { context := before, captured := none } .start
    let changed := advance countSteps started (.contextChanged after)
    evaluate countSteps changed.context = [4] ∧ changed.captured = some [3] ∧
      (advance countSteps changed .start).captured = some [4] := by decide

end ContextualEasing
