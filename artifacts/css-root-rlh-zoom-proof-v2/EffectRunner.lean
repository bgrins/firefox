import Effects
open Rlh
open Rlh.Effects

def formFor (tag : Nat) (font absolute zoom : Rat) : Form :=
  if tag = 1 then .numeric (5/4)
  else if tag = 2 then .normal (font + 3 / zoom) ⟨1,0,1⟩
  else if tag = 3 then .percentageComputed (5/4)
  else .absolute absolute

def makeWorld (role : Role) (base : Base) (current parent : Nat) : World :=
  let consumer := if role = .root then rootOwner 1 else ⟨1,20,1⟩
  let z : Zoom consumer := if role = .root then ⟨2,by decide,by decide⟩
    else if role = .media then ⟨1,by decide,by decide⟩ else ⟨4,by decide,by decide⟩
  let cf := formFor current 16 20 z.value
  let pf := formFor parent 20 24 1
  let inf := formFor current 16 19 1
  let rootValue := semanticLine 16 (formFor current 16 20 2)
  {consumer, parent := parentOwner 1, root := rootOwner 1, initial := initialOwner,
   consumerZoom := z, parentZoom := zOne (parentOwner 1), inheritanceZoom := z.value,
   current := ⟨16,cf,⟨semanticLine 16 cf * z.value⟩⟩,
   inherited := ⟨20,pf,⟨semanticLine 20 pf⟩⟩,
   initialFont := 16, initialForm := inf, initialStored := ⟨semanticLine 16 inf⟩,
   rootSemantic := rootValue, cache := ⟨rootValue⟩, role, base, coefficient := ⟨3/2⟩}

def parseRat (s : String) : Rat :=
  let t := (s.splitOn "/").toArray
  let n := (t[0]!).toInt!
  let d := if t.size = 1 then 1 else (t[1]!).toNat!
  (n : Rat) / (d : Rat)
def rq (v : Rat) : String := s!"{v.num}/{v.den}"
def encode (f : Flags) : Nat :=
  (if f.fontRelative then 1 else 0) + (if f.selfMetrics then 2 else 0) +
  (if f.inheritedMetrics then 4 else 0) + f.other

def main (args : List String) : IO Unit := do
  let kind := (args[0]!).toNat!
  let input ← IO.getStdin
  let output ← IO.getStdout
  repeat
    let line ← input.getLine
    if line.isEmpty then break
    let t := (line.trimAscii.toString.splitOn " ").toArray
    let n : Nat → Nat := fun i => (t[i]!).toNat!
    let role := if n 1 = 0 then Role.root else if n 1 = 1 then .media else .descendant
    let base := if n 2 = 0 then Base.current else .inherited
    let w := makeWorld role base (n 3) (n 4)
    if !validBool w then throw (IO.userError "inadmissible effect world")
    let flags := n 5
    let seed : Rlh.Effects.State :=
      ⟨⟨flags % 2 = 1, flags / 2 % 2 = 1, flags / 4 % 2 = 1, flags / 8 * 8⟩,
       ⟨if n 6 = 1 then some (parseRat t[7]!) else none,
        if n 8 = 1 then some (parseRat t[9]!) else none, 0⟩⟩
    let observed := if kind = 4 then Rlh.Effects.original w seed else mutated kind w seed
    let intended := Rlh.Effects.reference w seed
    if kind = 0 && observed != intended then throw (IO.userError "effect refinement failed")
    if kind != 4 && observed.numeric != (candidate w seed).numeric then
      throw (IO.userError "flag mutant changed numerics")
    let c := observed.after.conditions
    output.putStrLn s!"{n 0} {rq observed.numeric.scaled} {rq observed.numeric.exposed} {encode observed.after.flags} {c.fontSize.isSome} {rq (c.fontSize.getD 0)} {c.lineHeight.isSome} {rq (c.lineHeight.getD 0)}"
