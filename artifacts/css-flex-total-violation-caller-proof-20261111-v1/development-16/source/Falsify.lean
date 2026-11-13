import FlexViolationCaller.Target

open FlexViolationCaller

private def values : Nat → List (List Int)
  | 0 => [[]]
  | n + 1 => [-1,0,1,3].flatMap fun x => (values n).map (x :: ·)

private def seeds : List Seed :=
  [strutSeed 0, normalSeed 7 (-1) 0 1, normalSeed 7 0 0 1,
   normalSeed 7 2 0 1, normalSeed 7 0 1 2,
   normalSeed 7 1 0 2 true false, normalSeed 7 1 0 2 false true]

private def seedLists : List (List Seed) :=
  [[]] ++ seeds.map (fun x => [x]) ++ seeds.flatMap (fun x => seeds.map (fun y => [x,y]))

private def stateOK (original : List Seed) (s : LoopState) : Bool :=
  s.line.frozenCount == countedFrozen s.line.items &&
  s.line.items.map ItemState.fields == original.map Seed.fields &&
  s.line.items.length == original.length &&
  decide (remaining s.line ≤ original.length - s.iteration) &&
  decide (s.iteration ≤ original.length) &&
  (!s.finished || remaining s.line == 0) &&
  s.line.items.all (fun x =>
    decide (x.fields.minimum ≤ x.current ∧ x.current ≤ x.fields.maximum) &&
    !(x.minFlag && x.maxFlag) && (x.frozen || (!x.minFlag && !x.maxFlag)))

private def passOK (old : LoopState) (p : Pass) : Bool :=
  p.clamped.left == 0 && p.helper.left == 0 && !p.helper.fallback &&
  FlexViolation.wideFold ((active p.prepared.items).map asItem) == some p.clamped.violation &&
  newlySelected p.prepared.items p.after.items == FlexViolation.frozen ((active p.prepared.items).map asItem) &&
  ((old.line.items.zip p.after.items).all fun (a,b) => a.fields == b.fields && (!a.frozen || a == b)) &&
  (remaining old.line == 0 || decide (remaining p.after < remaining old.line))

private def checkHistory (original : List Seed) : Nat → LoopState → Bool
  | 0, s => stateOK original s && s.finished
  | n + 1, s =>
    stateOK original s && (s.finished ||
      (values original.length).all fun vs =>
        match runPass s.iteration s.line vs with
        | none => false
        | some p => passOK s p && checkHistory original n (advance s p))

#eval (seedLists.length,
  seedLists.all fun xs => [false,true].all fun grow => [false,true].all fun info =>
    checkHistory xs xs.length (start xs grow info))
