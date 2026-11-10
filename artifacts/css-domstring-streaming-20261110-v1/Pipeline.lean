import PairStream

namespace CssStreaming

structure PipeResult (Input Middle Output : Type) where
  output : List Output
  inputPending : Option Input
  middlePending : Option Middle
  deriving Repr

def pipeChunks (first : Machine Input Middle) (second : Machine Middle Output)
    (inputPending : Option Input) (middlePending : Option Middle) :
    List (List Input) → PipeResult Input Middle Output
  | [] => ⟨[], inputPending, middlePending⟩
  | input :: rest =>
    let decoded := feed first inputPending input
    let prepared := feed second middlePending decoded.output
    let later := pipeChunks first second decoded.pending prepared.pending rest
    ⟨prepared.output ++ later.output, later.inputPending, later.middlePending⟩

def pipeFinish (first : Machine Input Middle) (second : Machine Middle Output)
    (result : PipeResult Input Middle Output) : List Output :=
  let lastInput := flush first result.inputPending
  let lastOutput := feed second result.middlePending lastInput
  result.output ++ lastOutput.output ++ flush second lastOutput.pending

def pipeline (first : Machine Input Middle) (second : Machine Middle Output)
    (input : List (List Input)) : List Output :=
  pipeFinish first second (pipeChunks first second none none input)

end CssStreaming
