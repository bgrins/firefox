import TypeObservation
open OrderedTypes TypeMutations TypeObservation

def listText (xs : List Nat) : String := String.intercalate "," (xs.map toString)
def valid (x : Nat) : Bool := !(x == 5 || x == 6)
def flags (xs : List Nat) : String := String.ofList ((List.range 12).map
  (fun x => if nativeQuery xs [x] valid then '1' else '0'))
def parseOps : List Nat → List (Op Nat)
  | tag :: x :: rest =>
      (match tag with | 0 => Op.add x | 1 => Op.delete x | 2 => Op.clear | _ => Op.observe) :: parseOps rest
  | _ => []
def replyText : Reply → String
  | .self _ => "2"
  | .deleted b => if b then "1" else "0"
  | .undefined => "-1"
  | .observed => "3"
def steps (s : State Nat) : List (Op Nat) → String
  | [] => ""
  | op :: ops =>
      let next := operation s op
      "|" ++ listText next.1.native ++ "|" ++ listText (observed next.1) ++ "|" ++
        replyText next.2 ++ "|" ++ flags next.1.native ++ steps next.1 ops

def line (nums : List Nat) : String :=
  match nums with
  | id :: kind :: n :: rest =>
    let input := if kind == 0 then rest.take n else []
    let s := materialize (start input 7 9)
    let ops := parseOps ((rest.drop n).drop 1)
    toString id ++ "|" ++ listText s.native ++ "|" ++ listText (observed s) ++ steps s ops
  | _ => "bad input"

def main (args : List String) : IO Unit := do
  let path := args.head!
  let text ← IO.FS.readFile path
  for row in text.splitOn "\n" do
    if row != "" then
      let nums := (row.splitOn " ").map (fun token => token.toNat!)
      IO.println (line nums)
