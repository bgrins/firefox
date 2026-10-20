import Boundaries
open TypeInvalidation

def members (mask : Nat) : List Nat :=
  (List.range 2).filter (fun n => mask / (2 ^ n) % 2 == 1)
def subjects (mask : Nat) : List Subject :=
  ([Subject.root, .descendant 0, .pseudo 0, .pseudo 1, .pseudo 2].zipIdx.filter
    (fun pair => mask / (2 ^ pair.2) % 2 == 1)).map Prod.fst

def bits (xs : List Nat) : Nat :=
  (if 0 ∈ xs then 1 else 0) + (if 1 ∈ xs then 2 else 0)

def snapshot (s : State) : String :=
  "|" ++ String.intercalate "," ([bits (s.types 0), bits (s.types 1), s.helperCalls,
    s.requests, if s.pending then 1 else 0, s.cache .root,
    s.cache (.descendant 0), s.cache (.pseudo 0), s.cache (.pseudo 1), s.cache (.pseudo 2)].map toString)

def parseActions : List Nat → List Action
  | tag :: actor :: name :: stage :: rest =>
    (if tag == 3 then Action.delivery (subjects name) else
      Action.mutation actor (match tag with | 0 => .add name | 1 => .delete name | _ => .clear)
        (stage == 0)) :: parseActions rest
  | _ => []

def history (e : Environment) (s : State) : List Action → String
  | [] => ""
  | a :: rest => let next := step e s a; snapshot next ++ history e next rest

def calibrationEnvironment : Environment :=
  { fixture with
    subjects := [.root, .descendant 0, .pseudo 0, .pseudo 1, .pseudo 2]
    base := fun subject => match subject with
      | .root => 10 | .descendant _ => 17 | .pseudo 0 => 20 | .pseudo 1 => 25 | .pseudo _ => 30
    rules := [⟨.root, .activeType 0, 100⟩, ⟨.descendant 0, .activeType 0, 43⟩,
      ⟨.pseudo 0, .activeType 0, 80⟩, ⟨.pseudo 1, .activeType 0, 75⟩, ⟨.pseudo 2, .activeType 0, 70⟩,
      ⟨.root, .activeType 1, 200⟩, ⟨.descendant 0, .activeType 1, 61⟩] }

def line : List Nat → String
  | id :: owner :: root :: composed :: pres :: m0 :: m1 :: _count :: rest =>
    let e : Environment := { calibrationEnvironment with
      owner := (if owner < 2 then some owner else none)
      rootPresent := root == 1
      composedDocument := composed == 1
      presContext := pres == 1 }
    let s := freshState e (fun id => if id == 0 then members m0 else members m1)
    toString id ++ snapshot s ++ history e s (parseActions rest)
  | _ => "bad input"

def main (args : List String) : IO Unit := do
  let text ← IO.FS.readFile args.head!
  for row in text.splitOn "\n" do
    if row != "" then IO.println (line ((row.splitOn " ").map String.toNat!))
