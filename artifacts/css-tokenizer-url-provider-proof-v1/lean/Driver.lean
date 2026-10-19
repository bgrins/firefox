import URLDispatch
open URLDispatch

def hexDigit (n : Nat) : Char := Char.ofNat (if n<10 then 48+n else 87+n)
def hex (xs : List Byte) : String := String.ofList (xs.flatMap fun b => [hexDigit (b.val/16),hexDigit (b.val%16)])
def digit (c : Char) : Nat := if c.toNat≤57 then c.toNat-48 else c.toNat-87
def decode : List Char → List Byte
 | a::b::rest => Escape.byte (digit a*16+digit b)::decode rest
 | _ => []
def kindName : Kind → String
 | .ident => "ident"
 | .function => "function"
 | .url => "url"
 | .bad => "bad-url"

def emit (row : Nat) (xs : List Byte) : IO Unit := do
 let out ← IO.getStdout
 let r := native xs false
 let st := CommentObservers.nativeObserve (xs.take r.count) ⟨0,0,1⟩
 let name := Name.run false xs
 let afterOpen := name.rest.drop 1
 let body := afterOpen.dropWhile URLScan.nativeWhitespace
 let payload := if r.kind==.bad then URLTrace.rawPayload (URLTrace.run body) else r.payload
 out.putStrLn s!"{row}|first|{kindName r.kind}|{hex payload}|{r.count}|{st.line}|{st.column}|{r.pending}|{r.seen}"
 if r.kind==.function then
   match body with
   | q::tail =>
     if URLLeading.quote q then
       let ws := afterOpen.take (afterOpen.length-body.length)
       let s := URLDelegation.nativeCombined (q==39) ws tail st ⟨none,none⟩
       let k := if s.value.ending==.bad then "bad-string" else "string"
       out.putStrLn s!"{row}|string|{k}|{hex s.value.output}|{s.state.offset}|{s.state.line}|{s.state.column}|false|{r.seen}"
   | [] => pure ()

def main : IO Unit := do
 let input ← IO.getStdin
 let mut row := 0
 repeat
   let line ← input.getLine
   if line.isEmpty then break
   let bytes := decode line.trimAscii.toString.toList
   emit row bytes
   row := row+1
