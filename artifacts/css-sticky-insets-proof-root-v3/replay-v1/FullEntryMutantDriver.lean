import Lean
import StickyFullChallenges
import FullEntryMutant
open Lean StickyNumeric StickyConsumers StickyEndpoints StickyFullEndpoint StickyFullChallenges RootCrossAxis

def frameFor (h : Nat) : Frame2 :=
  if h == 0 then ordinary else if h == 1 then shiftFrame else if h == 2 then coreFrame else boundedFrame

def scenario (h g : Nat) (axis : Bool) : Bool × List Frame2 :=
  let f := if axis then frameFor h else swapFrame (frameFor h)
  let frames := if g == 2 then [{f with sticky := false}] else if g == 3 then [f,f]
    else if g == 4 then [{f with hasOffsets := false}]
    else if g == 5 then [if axis then {f with x := {f.x with insets := ⟨none,none⟩}}
                        else {f with y := {f.y with insets := ⟨none,none⟩}}]
    else [f]
  (g != 1,frames)

def payload (early late : Int) (d : Option Displacement) : Json :=
  match d with
  | none => Json.null
  | some v => toJson ([v.shift,v.near.atScroll,v.near.maxOffset,v.far.atScroll,v.far.maxOffset,early,late] : List Int)

def main : IO Unit := do
  let mut id := 0
  for h in [0:4] do
    for g in [0:6] do
      for axis in [false,true] do
        let (container,frames) := scenario h g axis
        let safe := decide (FullEntryMutant.EntrySafe2 container axis frames)
        let m := machineEntry container axis frames
        let r := mathEntry container axis frames
        let early := machineEvaluate (fullCaller2 container axis true 50 frames)
        let late := machineEvaluate (fullCaller2 container axis false 50 frames)
        let re := expected container axis true 50 frames
        let rl := expected container axis false 50 frames
        IO.println (Json.mkObj [("id",toJson id),("safe",toJson safe),
          ("core",toJson m.core.isSome),("shift",toJson m.shift.isSome),
          ("machine",payload early late m.displacement),("reference",payload re rl r.displacement),
          ("complete_pair_equal",toJson (decide (m=r)))]).compress
        id := id+1
