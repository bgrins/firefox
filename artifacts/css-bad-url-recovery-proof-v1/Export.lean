import Recovery

namespace BadUrlExport

def digit (c : Char) : Nat :=
  if c ≤ '9' then c.toNat - '0'.toNat else c.toNat - 'a'.toNat + 10

def bytes : List Char → List UInt8
  | a :: b :: cs => UInt8.ofNat (16 * digit a + digit b) :: bytes cs
  | _ => []

def hexDigit (n : Nat) : Char :=
  Char.ofNat (if n < 10 then '0'.toNat + n else 'a'.toNat + n - 10)

def hex (cs : List Char) : String :=
  let bs := (String.ofList cs).toUTF8.data.toList
  String.ofList (bs.flatMap fun b => [hexDigit (b.toNat / 16), hexDigit (b.toNat % 16)])

end BadUrlExport

def main : IO Unit := do
  let input ← IO.getStdin
  let output ← IO.getStdout
  repeat
    let line ← input.getLine
    if line.isEmpty then break
    let raw := String.fromUTF8! (ByteArray.mk (BadUrlExport.bytes line.trimAscii.toString.toList).toArray)
    let filtered := BadUrl.normalize raw.toList
    let spec := BadUrlExport.hex (BadUrl.specification filtered)
    let candidate := BadUrlExport.hex (BadUrl.optimized filtered)
    let handoff := BadUrlExport.hex (BadUrl.candidateHandoff filtered)
    let expectedHandoff := BadUrlExport.hex (BadUrl.specificationHandoff filtered)
    output.putStrLn (String.intercalate " " [spec, candidate, handoff, expectedHandoff])
