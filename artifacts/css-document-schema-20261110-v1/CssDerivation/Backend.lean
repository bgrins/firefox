import Lean

namespace CssDerivation

structure State where
  input : List Char
  error : Bool
  deriving DecidableEq, Repr

inductive Program : Type → Type 1 where
  | pure {α : Type} : α → Program α
  | read : Program (Option Char)
  | scan : Nat → (Char → Bool) → Program (List Char)
  | skip : (Char → Bool) → Program Unit
  | raiseError : Program Unit
  | branch {α : Type} : Bool → Program α → Program α → Program α
  | bind {α β : Type} : Program α → (α → Program β) → Program β

def scanPrefix (predicate : Char → Bool) : Nat → List Char → List Char × List Char
  | 0, input => ([], input)
  | _ + 1, [] => ([], [])
  | budget + 1, c :: rest =>
      if predicate c then
        let later := scanPrefix predicate budget rest
        (c :: later.1, later.2)
      else ([], c :: rest)

def skipOne (predicate : Char → Bool) : List Char → List Char
  | [] => []
  | c :: rest => if predicate c then rest else c :: rest

def run : {α : Type} → Program α → State → α × State
  | _, .pure value, state => (value, state)
  | _, .read, state =>
      match state.input with
      | [] => (none, state)
      | c :: rest => (some c, { state with input := rest })
  | _, .scan budget predicate, state =>
      let scanned := scanPrefix predicate budget state.input
      (scanned.1, { state with input := scanned.2 })
  | _, .skip predicate, state => ((), { state with input := skipOne predicate state.input })
  | _, .raiseError, state => ((), { state with error := true })
  | _, .branch condition yes no, state => if condition then run yes state else run no state
  | _, .bind first next, state =>
      let result := run first state
      run (next result.1) result.2

structure Result where
  value : Char
  rest : List Char
  error : Bool
  deriving DecidableEq, Repr

def execute (program : Program Char) (input : List Char) : Result :=
  let result := run program ⟨input, false⟩
  ⟨result.1, result.2.input, result.2.error⟩

end CssDerivation
