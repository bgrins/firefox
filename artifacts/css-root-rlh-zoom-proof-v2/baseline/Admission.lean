import Nonvacuity
open Rlh

def main : IO Unit := do
  let sampleWorld := sample .root .current (.absolute 20) 1
  let staleProvider := {sampleWorld with current := ⟨16,.absolute 20,⟨20⟩⟩}
  let badCache := {sampleWorld with cache := ⟨99⟩}
  let badOwner := {sampleWorld with root := ⟨2,10,1⟩,cache := ⟨20⟩}
  let badRole := {sample .descendant .current (.absolute 20) 1 with role := .root}
  let r := sampleRoot (.absolute 20) 1
  let initialState := initial r
  let q := sampleRequest .descendant .current (.absolute 20) 1
  let wrongVersion := sampleRequest .descendant .current (.absolute 20) 2
  let published := publishReference initialState
  let failures := [validBool staleProvider,validBool badCache,validBool badOwner,validBool badRole,
    requestBool initialState q,requestBool published wrongVersion]
  if failures.any id then throw (IO.userError "invalid admission accepted")
  let forms := [Form.absolute 20,.numeric (5/4),.percentageComputed (5/4),.normal 19 ⟨1,0,3⟩]
  let mut count := 0
  for role in [Role.root,.media,.descendant] do
    for base in [Base.current,.inherited] do
      for f in forms do
        let world := sample role base f 1
        if !validBool world then throw (IO.userError "valid witness rejected")
        if implementation world != reference world then throw (IO.userError "witness refinement failed")
        count := count + 1
  if !requestBool initialState (sampleRequest .root .current (.absolute 20) 1) then
    throw (IO.userError "direct prepublication read rejected")
  if !requestBool initialState (sampleRequest .media .current (.absolute 20) 1) then
    throw (IO.userError "media prepublication read rejected")
  if !requestBool published q then throw (IO.userError "fresh read rejected")
  IO.println s!"{count} {failures.length} 2"
