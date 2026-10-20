import CalibrationCases
import ProtectedWitnesses
namespace ProtectedCalibration
open ProtectedSpan

def hex (raw : List UInt8) : String := String.ofList (raw.flatMap fun b =>
  [Char.ofNat (if b.toNat/16<10 then 48+b.toNat/16 else 87+b.toNat/16),
   Char.ofNat (if b.toNat%16<10 then 48+b.toNat%16 else 87+b.toNat%16)])
def erased (ts : List Token) : List TerminalSpan.Token :=
  ts.map fun t => ⟨t.kind,t.raw⟩

def main : IO Unit := do
  let out ← IO.getStdout
  for (ts,index) in cases.zipIdx do
    out.putStrLn (toString index++"|"++hex (stored ts)++"|"++
      hex (Witnesses.standaloneStored ts)++"|"++hex (TerminalSpan.stored (erased ts)))
end ProtectedCalibration

def main := ProtectedCalibration.main
