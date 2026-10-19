import Mutants
import Nonvacuity
open Rlh

def rat (s : String) : Rat :=
  let ps := s.splitOn "/"
  let n := (ps[0]!).toInt!
  let d := if ps.length = 1 then 1 else (ps[1]!).toNat!
  (n : Rat) / (d : Rat)
def form (tag : Nat) (value : Rat) : Form :=
  if tag = 1 then .numeric value else if tag = 3 then .percentageComputed value else .absolute value
def zoom (o : Owner) (v : Rat) : IO (Zoom o) := do
  if h : 0 < v then
    return ⟨v,h,by intro hz; rw [hz] at h; exact (by decide : ¬ (0:Rat) < 0) h⟩
  else throw (IO.userError "inadmissible zoom")
def provider (o : Owner) (z : Zoom o) (size : Rat) (f : Form) : Provider o :=
  ⟨size,f,⟨semanticLine size f * z.value⟩⟩
def owner (encoded epoch : Nat) : Owner := ⟨⟨encoded / 10000⟩,⟨encoded % 10000⟩,⟨epoch⟩⟩
def code (o : Owner) : Nat := o.document.value * 10000 + o.element.value
def sourceCode : Source → Nat × Nat
  | .current o => (0,code o)
  | .inherited o => (1,code o)
  | .initial o => (2,code o)
  | .cache o => (3,code o)
def rq (v : Rat) : String := s!"{v.num}/{v.den}"

def main (args : List String) : IO Unit := do
  let m := (args[0]!).toNat!
  let input ← IO.getStdin
  let output ← IO.getStdout
  let mut s := initial (sampleRoot (.absolute 20) 0)
  let mut schedule := false
  let mut count := 0
  let mut foreign : Rat := 64
  let mut foreignUsed := false
  repeat
    let line ← input.getLine
    if line.isEmpty then break
    let t := (line.trimAscii.toString.splitOn " ").toArray
    let n : Nat → Nat := fun i => (t[i]!).toNat!
    let v : Nat → Rat := fun i => rat (t[i]!)
    if t[0]! = "ROOT" then
      let o : Owner := ⟨⟨n 1⟩,⟨n 2⟩,⟨n 3⟩⟩
      let z ← zoom o (v 4)
      let p := provider o z (v 5) (form (n 6) (v 7))
      let root : RootRecord := ⟨o,z,p,rfl⟩
      s := commit s root
      schedule := false
    else if t[0]! = "PUBLISH" then
      s := mutantPublish m count s
      count := count + 1
      schedule := true
    else if t[0]! = "FOREIGN" then foreign := v 1
    else if t[0]! = "READ" then
      let role := if n 2 = 0 then Role.root else if n 2 = 1 then .media else .descendant
      let base := if n 4 = 0 then Base.current else .inherited
      let epoch := s.root.owner.epoch.value
      let consumer := if role = .root then s.root.owner else owner (n 6) epoch
      let parent := owner (n 8) epoch
      let initialOwner : Owner := ⟨consumer.document,0,0⟩
      let z ← zoom consumer (if role = .root then s.root.zoom.value else v 7)
      let pz ← zoom parent (v 9)
      let current := if role = .root then
          provider consumer z s.root.provider.font s.root.provider.form
        else provider consumer z (v 10) (form (n 11) (v 12))
      let inherited := provider parent pz (v 13) (form (n 14) (v 15))
      let initialForm := form (n 17) (v 18)
      let w : World :=
        {consumer,parent,root := s.root.owner,initial := initialOwner,consumerZoom := z,
         parentZoom := pz,inheritanceZoom := z.value / pz.value,current,inherited,
         initialFont := v 16,initialForm,initialStored := ⟨semanticLine (v 16) initialForm⟩,
         rootSemantic := s.root.value,cache := ⟨s.root.value⟩,role,base,coefficient := ⟨v 5⟩}
      if !validBool w then throw (IO.userError "world rejected")
      if role = .descendant && !schedule then throw (IO.userError "missing publication")
      let actual := {w with cache := ⟨(s.cache.map CacheRecord.value).getD 0⟩}
      let observed := mutantRead m actual ⟨2,10,0⟩ foreign
      let expected := reference w
      if m = 0 && observed != expected then throw (IO.userError "refinement failed")
      if m = 6 && role = .descendant then foreignUsed := true
      else s := {s with used := s.used || observed.cacheUsed}
      let used := if m = 6 && role = .descendant then foreignUsed else s.used
      let src := sourceCode observed.source
      output.putStrLn s!"{n 1} {rq observed.scaled} {rq observed.exposed} {src.1} {src.2} {rq ((s.cache.map CacheRecord.value).getD 0)} {observed.cacheUsed} {used} {rq expected.exposed}"
    else throw (IO.userError "bad protocol")
