import URLNativeLeading
import URLDispatch

def hexDigit (n : Nat) : Char := Char.ofNat (if n<10 then 48+n else 87+n)
def hex (xs : List CommentScan.Byte) : String := String.ofList (xs.flatMap fun b => [hexDigit (b.val/16),hexDigit (b.val%16)])
def digit (c : Char) : Nat := if c.toNat≤57 then c.toNat-48 else c.toNat-87
def decode : List Char → List CommentScan.Byte
 | a::b::rest => Escape.byte (digit a*16+digit b)::decode rest
 | _ => []
def fields (s : URLNativeState.State) : String := s!"{s.position}|{s.currentLineStart}|{s.packedLine}"
def emit (row : Nat) (xs : List CommentScan.Byte) : IO Unit := do
 let out ← IO.getStdout
 let name := Name.run false xs
 if URLDispatch.nativeURL name.output && name.rest.head?==some 40 then
   let offset := name.count+1
   let r := CommentObservers.nativeObserve (xs.take offset) ⟨0,0,1⟩
   let start : URLNativeState.State := ⟨offset,URLNativeState.wrap ((r.offset:Int)+1-r.column),4*r.line⟩
   out.putStrLn s!"{row}|enter|{fields start}"
   let body := xs.drop offset
   match URLNativeLeading.run body start with
   | .function s => out.putStrLn s!"{row}|exit|{fields s}|function|"
   | .emptyURL s => out.putStrLn s!"{row}|exit|{fields s}|url|"
   | .body entry =>
     let afterWhitespace := body.dropWhile URLScan.nativeWhitespace
     let value := URLScan.reference afterWhitespace
     let payload := match entry.result.rawEnd with
       | some finish => URLNativeSlice.slice xs entry.startPosition finish
       | none => value.output
     let kind := if value.kind==.bad then "bad-url" else "url"
     out.putStrLn s!"{row}|exit|{fields entry.result.state}|{kind}|{hex payload}"
 else out.putStrLn s!"{row}|skip"
def main : IO Unit := do
 let input ← IO.getStdin
 let mut row := 0
 repeat
   let line ← input.getLine
   if line.isEmpty then break
   emit row (decode line.trimAscii.toString.toList)
   row := row+1
