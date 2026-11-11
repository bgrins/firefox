import Lake.Check.Compare
import Lake.Check.Axioms

open Lean Lake.Check

def primitiveNames : Array Name := #[
  ``Nat.add, ``Nat.sub, ``Nat.mul, ``Nat.pow, ``Nat.gcd, ``Nat.div, ``Nat.mod,
  ``Nat.beq, ``Nat.ble, ``Nat.land, ``Nat.lor, ``Nat.xor, ``Nat.shiftLeft,
  ``Nat.shiftRight, ``String.ofList, ``Char.ofNat, ``List, ``eagerReduce,
  ``Nat, ``String, ``String.mk, ``Char, ``optParam, ``autoParam,
  ``semiOutParam, ``outParam]

def main (args : List String) : IO Unit := do
  let [challengePath, solutionPath] := args
    | throw <| IO.userError "expected two locally generated export paths"
  let challenge ← LeanExport.parseStream <| .ofHandle (← IO.FS.Handle.mk challengePath .read)
  let solution ← LeanExport.parseStream <| .ofHandle (← IO.FS.Handle.mk solutionPath .read)
  let axioms := #[``propext, ``Quot.sound, ``Classical.choice]
  let targets := #[`NumericDigits.scan_reference]
  match compareAt challenge solution (targets ++ axioms) #[] primitiveNames with
  | .ok _ => IO.println "comparison: match"
  | .error e => IO.println s!"comparison: {e}"
  match checkAxioms solution targets #[] axioms with
  | .ok _ => IO.println "axioms: permitted"
  | .error e => IO.println s!"axioms: {e}"
  IO.println s!"challenge declarations: {challenge.constOrder.size}"
  IO.println s!"solution declarations: {solution.constOrder.size}"
