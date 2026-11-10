import StatefulIR

namespace CssDerivation.FirstOrder

inductive Ty where
  | nat | scalar | bool | chars | unit
  deriving DecidableEq, Repr

abbrev Ty.Value : Ty → Type
  | .nat => Nat
  | .scalar => Char
  | .bool => Bool
  | .chars => List Char
  | .unit => Unit

inductive Var : List Ty → Ty → Type where
  | here {Γ t} : Var (t :: Γ) t
  | there {Γ t u} : Var Γ t → Var (u :: Γ) t

inductive Env : List Ty → Type where
  | nil : Env []
  | cons {Γ t} : t.Value → Env Γ → Env (t :: Γ)

def lookup : Var Γ t → Env Γ → t.Value
  | .here, .cons value _ => value
  | .there index, .cons _ rest => lookup index rest

inductive Expr : List Ty → Ty → Type where
  | nat {Γ} : Nat → Expr Γ .nat
  | scalar {Γ} : Char → Expr Γ .scalar
  | bool {Γ} : Bool → Expr Γ .bool
  | nil {Γ} : Expr Γ .chars
  | unit {Γ} : Expr Γ .unit
  | var {Γ t} : Var Γ t → Expr Γ t
  | code {Γ} : Expr Γ .scalar → Expr Γ .nat
  | scalarOf {Γ} : Expr Γ .nat → Expr Γ .scalar
  | add {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .nat
  | sub {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .nat
  | mul {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .nat
  | leNat {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .bool
  | ltNat {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .bool
  | eqNat {Γ} : Expr Γ .nat → Expr Γ .nat → Expr Γ .bool
  | leChar {Γ} : Expr Γ .scalar → Expr Γ .scalar → Expr Γ .bool
  | eqChar {Γ} : Expr Γ .scalar → Expr Γ .scalar → Expr Γ .bool
  | and {Γ} : Expr Γ .bool → Expr Γ .bool → Expr Γ .bool
  | or {Γ} : Expr Γ .bool → Expr Γ .bool → Expr Γ .bool
  | ite {Γ t} : Expr Γ .bool → Expr Γ t → Expr Γ t → Expr Γ t
  | cons {Γ} : Expr Γ .scalar → Expr Γ .chars → Expr Γ .chars
  | foldNat {Γ} : Expr Γ .chars → Expr Γ .nat → Expr (.scalar :: .nat :: Γ) .nat → Expr Γ .nat

def eval : Expr Γ t → Env Γ → t.Value
  | .nat value, _ => value
  | .scalar value, _ => value
  | .bool value, _ => value
  | .nil, _ => []
  | .unit, _ => ()
  | .var index, env => lookup index env
  | .code value, env => (eval value env).toNat
  | .scalarOf value, env => Char.ofNat (eval value env)
  | .add left right, env => eval left env + eval right env
  | .sub left right, env => eval left env - eval right env
  | .mul left right, env => eval left env * eval right env
  | .leNat left right, env => decide (eval left env ≤ eval right env)
  | .ltNat left right, env => decide (eval left env < eval right env)
  | .eqNat left right, env => eval left env == eval right env
  | .leChar left right, env => decide (eval left env ≤ eval right env)
  | .eqChar left right, env => eval left env == eval right env
  | .and left right, env => eval left env && eval right env
  | .or left right, env => eval left env || eval right env
  | .ite condition yes no, env => if eval condition env = true then eval yes env else eval no env
  | .cons first rest, env => eval first env :: eval rest env
  | .foldNat input initial step, env =>
      (eval input env).foldl (fun acc c => eval step (.cons c (.cons acc env))) (eval initial env)

inductive Stmt : List Ty → Ty → Type where
  | ret {Γ t} : Expr Γ t → Stmt Γ t
  | letE {Γ t u} : Expr Γ u → Stmt (u :: Γ) t → Stmt Γ t
  | read {Γ t} : Stmt Γ t → Stmt (.scalar :: Γ) t → Stmt Γ t
  | scan {Γ t} : Nat → Expr (.scalar :: Γ) .bool → Stmt (.chars :: Γ) t → Stmt Γ t
  | raiseError {Γ t} : Stmt Γ t → Stmt Γ t
  | branch {Γ t} : Expr Γ .bool → Stmt Γ t → Stmt Γ t → Stmt Γ t

def scanData (predicate : Expr (.scalar :: Γ) .bool) (env : Env Γ) :
    Nat → List Char → List Char × List Char
  | 0, input => ([], input)
  | _ + 1, [] => ([], [])
  | budget + 1, c :: rest =>
      if eval predicate (.cons c env) = true then
        let later := scanData predicate env budget rest
        (c :: later.1, later.2)
      else ([], c :: rest)

def interpret : Stmt Γ t → Env Γ → State → t.Value × State
  | .ret value, env, state => (eval value env, state)
  | .letE value next, env, state => interpret next (.cons (eval value env) env) state
  | .read eof present, env, state =>
      match state.input with
      | [] => interpret eof env state
      | c :: rest => interpret present (.cons c env) { state with input := rest }
  | .scan budget predicate next, env, state =>
      let scanned := scanData predicate env budget state.input
      interpret next (.cons scanned.1 env) { state with input := scanned.2 }
  | .raiseError next, env, state => interpret next env { state with error := true }
  | .branch condition yes no, env, state =>
      if eval condition env = true then interpret yes env state else interpret no env state

def lower : Stmt Γ t → Env Γ → Program t.Value
  | .ret value, env => .pure (eval value env)
  | .letE value next, env => .bind (.pure (eval value env)) fun value => lower next (.cons value env)
  | .read eof present, env => .bind .read fun value =>
      match value with
      | none => lower eof env
      | some c => lower present (.cons c env)
  | .scan budget predicate next, env =>
      .bind (.scan budget (fun c => eval predicate (.cons c env))) fun chars => lower next (.cons chars env)
  | .raiseError next, env => .bind .raiseError fun _ => lower next env
  | .branch condition yes no, env => .branch (eval condition env) (lower yes env) (lower no env)

def execute (program : Stmt [] .scalar) (input : List Char) : Result :=
  let result := interpret program .nil ⟨input, false⟩
  ⟨result.1, result.2.input, result.2.error⟩

end CssDerivation.FirstOrder
