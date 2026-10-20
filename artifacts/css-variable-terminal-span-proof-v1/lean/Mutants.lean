import Witnesses
open TerminalSpan

def badNoReset (s : State) (t : Token) : State :=
  { step s t with trailing := if white t then t.raw.length else s.trailing }
def badNormalized (s : State) (t : Token) : State :=
  { step s t with trailing := if white t then 1 else 0 }
def badBlock (s : State) (t : Token) : State :=
  { step s t with trailing := if t.kind == .function then 1 else (step s t).trailing }
def altered (mode : String) (ts : List Token) : List UInt8 × Option Kind :=
  if mode == "ascii" then (oldTrim (bytes ts), lastMetadata ts)
  else if mode == "metadata" then (stored ts, (scan {} ts).last)
  else if mode == "no-reset" || mode == "normalized" || mode == "inner" then
    let f := if mode == "no-reset" then badNoReset else if mode == "normalized" then badNormalized else badBlock
    let s := ts.foldl f {}
    ((bytes ts).take ((bytes ts).length - s.trailing), lastMetadata ts)
  else (stored ts, lastMetadata ts)

def challenges : List (String × List Token × (List UInt8 × Option Kind)) :=
  [("escaped", [escaped, ws], (escaped.raw, some .ident)),
   ("CRLF", [escaped, crlf], (escaped.raw, some .ident)),
   ("comment", [escaped, ws, comment], (bytes [escaped, ws, comment], some .delimSlash)),
   ("block", [escaped, ws, block], (bytes [escaped, ws, block], some .function))]

def main (args : List String) : IO UInt32 := do
  let mode := args.headD "candidate"
  for (name, ts, expected) in challenges do
    unless altered mode ts == expected do
      IO.println ("SEMANTIC_MISMATCH " ++ mode ++ " " ++ name)
      return 42
  IO.println "PASS 4 semantic challenges"
  return 0
