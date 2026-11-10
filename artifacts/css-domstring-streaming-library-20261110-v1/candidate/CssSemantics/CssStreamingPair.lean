import Lean

namespace CssSemantics.Streaming

structure Machine (Input Output : Type) where
  holds : Input → Bool
  combine : Input → Input → Option Output
  single : Input → Output
  unheld : ∀ first, holds first = false → ∀ second, combine first second = none

structure Emission (Input Output : Type) where
  output : List Output
  pending : Option Input
  deriving Repr

def buffered (pending : Option Input) : List Input := pending.toList

def batch (machine : Machine Input Output) : List Input → List Output
  | [] => []
  | [first] => [machine.single first]
  | first :: second :: rest =>
    match machine.combine first second with
    | some combined => combined :: batch machine rest
    | none => machine.single first :: batch machine (second :: rest)

def accept (machine : Machine Input Output) (pending : Option Input) (input : Input) :
    Emission Input Output :=
  let fresh : Emission Input Output :=
    if machine.holds input then ⟨[], some input⟩ else ⟨[machine.single input], none⟩
  match pending with
  | none => fresh
  | some previous =>
    match machine.combine previous input with
    | some combined => ⟨[combined], none⟩
    | none => ⟨machine.single previous :: fresh.output, fresh.pending⟩

def feed (machine : Machine Input Output) (pending : Option Input) : List Input → Emission Input Output
  | [] => ⟨[], pending⟩
  | input :: rest =>
    let first := accept machine pending input
    let later := feed machine first.pending rest
    ⟨first.output ++ later.output, later.pending⟩

def chunks (machine : Machine Input Output) (pending : Option Input) :
    List (List Input) → Emission Input Output
  | [] => ⟨[], pending⟩
  | input :: rest =>
    let first := feed machine pending input
    let later := chunks machine first.pending rest
    ⟨first.output ++ later.output, later.pending⟩

def flush (machine : Machine Input Output) (pending : Option Input) : List Output :=
  (buffered pending).map machine.single

def finish (machine : Machine Input Output) (result : Emission Input Output) : List Output :=
  result.output ++ flush machine result.pending

def stream (machine : Machine Input Output) (input : List (List Input)) : List Output :=
  finish machine (chunks machine none input)

end CssSemantics.Streaming
