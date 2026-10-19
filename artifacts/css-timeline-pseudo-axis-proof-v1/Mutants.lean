import Runner
open Timeline Lean

def changedObservation (w : World) (old : State) (snap : Snapshot) (fresh : Option TimeData) : Observation :=
  ⟨⟨some snap,fresh⟩,fresh != old.time,
    if notificationNeeded old.time fresh then noticeNative w.subscribers 0 else [],dataNative fresh⟩

def mutantSample (m : Nat) (w : World) (old : State) : Observation := Id.run do
  if m = 0 then return sampleNative false w old
  if m = 1 then return sampleNative true {w with axis := if w.axis < 2 then 1-w.axis else w.axis} old
  if m = 2 then return sampleNative true {w with axis := if w.axis = 2 then 1 else if w.axis = 3 then 0 else w.axis} old
  if m = 3 then return sampleNative true {w with pseudo := if w.sourceType = 3 then 0 else w.pseudo} old
  if m = 4 then return sampleNative true {w with sourceType := if w.sourceType = 2 then 1 else w.sourceType} old
  if m = 5 then return sampleNative true {w with frames := w.frames.map fun f => {f with target := f.id}} old
  let base := sampleNative true w old
  if m = 6 then
    if !((getSnapshot base.state).active && (getSnapshot base.state).available) then
      return {base with state := {base.state with time := old.time},data := dataNative old.time}
    return base
  if m = 7 then
    let snap := getSnapshot base.state
    let f := frame w (frameNative w snap.source)
    let time := base.state.time.map fun t => {t with position := if snap.axis = 0 then f.y else f.x}
    return changedObservation w old snap time
  if m = 8 then
    let snap := old.snapshot.getD (snapshotNative true w)
    let f := frame w (frameNative w snap.source)
    let time := if snap.active && snap.available then
      some (if snap.axis = 0 then ⟨f.x,f.width⟩ else ⟨f.y,f.height⟩ : TimeData) else none
    return changedObservation w old snap time
  if m = 9 then
    let extra := match old.time,base.state.time with
      | some prev,some fresh => prev.position != fresh.position
      | _,_ => false
    return {base with notifications := if extra then noticeNative w.subscribers 0 else base.notifications}
  return {base with data := base.data.map fun t => {t with start := 1}}

structure MutationCase where
  mutant : Nat
  scenario : Scenario
  deriving FromJson

def mutantMain (args : List String) : IO Unit := do
  let input ← IO.FS.readFile args[0]!
  let stdout ← IO.getStdout
  for line in input.splitOn "\n" do
    if line.isEmpty then continue
    let parsed ← IO.ofExcept (Json.parse line)
    let c : MutationCase ← IO.ofExcept (fromJson? parsed)
    let mut old : State := {}
    for (typed,i) in c.scenario.worlds.zipIdx do
      unless Timeline.Typed.rolesValid typed do throw (IO.userError "invalid typed owner/provider role")
      let w := typed.erase
      let o := mutantSample c.mutant w old
      let exposed := if c.mutant = 3 && w.sourceType = 3 then w.host
        else if c.mutant = 4 && w.sourceType = 2 then w.scrolling else (sourceNative w).1
      let notifications := o.notifications.map fun n =>
        (((3000+n/2 : Nat) : Int), (if n%2 = 0 then 23 else 24 : Int),0,0)
      stdout.putStrLn ((rowJson c.scenario.id i exposed o notifications).compress)
      old := o.state
