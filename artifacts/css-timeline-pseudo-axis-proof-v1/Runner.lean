import Lean
import Trace
import Typed
open Lean Timeline

deriving instance FromJson for Element, Frame, World
structure Scenario where
  id : Nat
  worlds : List Timeline.Typed.World
  deriving FromJson

def num (n : Int) : Json := toJson n
def arr (xs : List Json) : Json := Json.arr xs.toArray
def optJson (f : α → Json) : Option α → Json
  | none => Json.null
  | some a => f a

def snapshotJson (s : Snapshot) : Json := arr
  [toJson s.source.1,toJson s.source.2,toJson (if s.root then 1 else 0 : Nat),
   toJson (if s.active then 1 else 0 : Nat),num (if s.active then s.axis else -1),
   toJson (if s.available then 1 else 0 : Nat),num (if s.active then s.style else -1),
   toJson (if s.apz then 1 else 0 : Nat)]

def rowJson (id sample exposed : Nat) (o : Observation) (trace : List Event) : Json :=
  Json.mkObj [
    ("case",toJson id),("sample",toJson sample),
    ("snapshot",snapshotJson (getSnapshot o.state)),
    ("raw_axis_style",arr [num (getSnapshot o.state).axis,num (getSnapshot o.state).style]),
    ("exposed",toJson exposed),
    ("cache",optJson (fun t => arr [num t.position,num t.extent]) o.state.time),
    ("data",optJson (fun t => arr [num t.position,num t.start,num t.finish]) o.data),
    ("changed",toJson (if o.changed then 1 else 0 : Nat)),
    ("trace",arr (trace.map fun (a,b,c,d) => arr [num a,num b,num c,num d]))]

def runnerMain (args : List String) : IO Unit := do
  let input ← IO.FS.readFile args[0]!
  let repaired := args[1]! == "candidate"
  let stdout ← IO.getStdout
  for line in input.splitOn "\n" do
    if line.isEmpty then continue
    let parsed ← IO.ofExcept (Json.parse line)
    let c : Scenario ← IO.ofExcept (fromJson? parsed)
    let mut state : State := {}
    for (typed,i) in c.worlds.zipIdx do
      unless Timeline.Typed.rolesValid typed do throw (IO.userError "invalid typed owner/provider role")
      let w := typed.erase
      let expected := sampleSpec repaired w state
      let native := sampleNative repaired w state
      let ((traced,exposed),trace) := (sampleQ repaired w state).run []
      unless native == expected && traced == native do
        throw (IO.userError s!"Lean semantics/trace mismatch {c.id}/{i}")
      stdout.putStrLn ((rowJson c.id i exposed native trace).compress)
      state := native.state
