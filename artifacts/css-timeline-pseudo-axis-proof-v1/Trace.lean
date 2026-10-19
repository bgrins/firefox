import Timeline

namespace Timeline
abbrev Event := Int × Int × Int × Int
abbrev TraceM := StateM (List Event)

def query (id op arg result : Int) : TraceM Int := do
  modify fun xs => xs ++ [(id,op,arg,result)]
  return result

def primaryQ (w : World) (e : Nat) : TraceM Nat := do
  return (← query e 1 0 (element w e).primary).toNat
def ownerQ (e : Nat) : TraceM Unit := do
  let _ ← query e 12 0 2000
  pure ()
def scrollingQ (w : World) : TraceM Nat := do
  return (← query 2000 18 0 w.scrolling).toNat
def rootQ (w : World) : TraceM Nat := do
  return (← query 2000 19 0 w.root).toNat
def shellQ (w : World) : TraceM Bool := do
  return (← query 2000 11 0 (if w.shell then 2001 else 0)) != 0
def rootFrameQ (w : World) : TraceM Nat := do
  return (← query 2001 17 0 w.rootFrame).toNat
def pseudoQ (w : World) (e p : Nat) : TraceM Nat := do
  return (← query e 2 p (pseudo w e p)).toNat
def parentQ (w : World) (f : Nat) : TraceM Nat := do
  return (← query f 3 0 (frame w f).parent).toNat

def pairQ (w : World) (e : Nat) : TraceM (Nat × Nat) := do
  let k := (element w e).kind
  if 1 ≤ k && k ≤ 6 then
    return ((← query e 14 0 (element w e).parent).toNat,k)
  if k = 7 then
    ownerQ e
    return (← rootQ w, k)
  return (e,0)

def chooseQ (w : World) (root : Nat) : Nat → Nat → TraceM (Nat × Nat)
  | 0, _ => pure (root,0)
  | n+1, f => do
    if f = 0 then return (root,0)
    let content := (← query f 15 0 (frame w f).content).toNat
    if content = 0 then return ← chooseQ w root n (← parentQ w f)
    let isElement ← query content 13 0 (if (element w content).isElement then 1 else 0)
    if isElement = 0 then return ← chooseQ w root n (← parentQ w f)
    if content = root then return (root,0)
    let scroll ← query f 4 0 (if (frame w f).scroll then 1 else 0)
    if scroll != 0 then return ← pairQ w content
    chooseQ w root n (← parentQ w f)

def nearestQ (w : World) : TraceM (Nat × Nat) := do
  if (← primaryQ w w.host) = 0 then return (0,0)
  let subject ← pseudoQ w w.host w.pseudo
  if subject = 0 then return (0,0)
  ownerQ subject
  let root ← scrollingQ w
  if root = subject then return (root,0)
  let primary ← primaryQ w subject
  if primary = 0 then return (0,0)
  chooseQ w root (w.frames.length + 1) (← parentQ w primary)

def sourceQ (w : World) : TraceM (Nat × Nat) := do
  if w.sourceType = 3 then return (w.host,w.pseudo)
  if w.sourceType = 2 then return ← nearestQ w
  if w.sourceType = 0 || w.sourceType = 4 then return (w.host,w.pseudo)
  ownerQ w.host
  return (← scrollingQ w,0)

def resolveQ (w : World) (source : Nat × Nat) (root : Bool) : TraceM Nat := do
  let (host,p) := source
  if host = 0 then return 0
  if root then
    ownerQ host
    if (← shellQ w) then return ← rootFrameQ w
    return 0
  let e ← pseudoQ w host p
  if e = 0 then return 0
  let mut f ← primaryQ w e
  ownerQ e
  if (← rootQ w) = e then
    let mut shell := false
    if f != 0 then
      shell := (← query f 9 0 (if (frame w f).shell then 2001 else 0)) != 0
    if !shell then
      ownerQ e
      shell ← shellQ w
    let mut rootFrame := 0
    if shell then rootFrame ← rootFrameQ w
    if rootFrame != 0 then f := rootFrame
  if f = 0 then return 0
  return (← query f 16 0 (frame w f).target).toNat

def snapshotQ (r : Bool) (w : World) : TraceM Snapshot := do
  let source ← sourceQ w
  let mut root := false
  if source.1 != 0 then
    ownerQ source.1
    root := (← scrollingQ w) == source.1
  if source.1 = 0 then return {source,root}
  if (← primaryQ w source.1) = 0 then return {source,root}
  let f ← resolveQ w source root
  if f = 0 then return {source,root}
  let mut modeFrame := f
  if !r then
    let _ ← primaryQ w source.1
    modeFrame ← primaryQ w source.1
  let vertical := (← query modeFrame 5 (if (frame w modeFrame).reversed then 1 else 0) (if (frame w modeFrame).vertical then 1 else 0)) != 0
  let axis := axisNative w.axis vertical
  let bits := (if (frame w f).availableX then 1 else 0) + (if (frame w f).availableY then 2 else 0)
  let _ ← query f 6 0 bits
  let available := if axis = 0 then (frame w f).availableX else (frame w f).availableY
  let _ ← query f 7 (frame w f).overflowX (frame w f).overflowY
  let mut apz := false
  if (← query 0 21 0 (if w.apz then 1 else 0)) != 0 then
    if (← query source.1 20 0 (if (element w source.1).apzDisabled then 1 else 0)) = 0 then
      apz := (← query source.1 22 0 (if (element w source.1).displayport then 1 else 0)) != 0
  return ⟨source, root, true, axis, available,
    (if axis = 0 then (frame w f).overflowX else (frame w f).overflowY), apz⟩

def sampleQ (r : Bool) (w : World) (old : State) : TraceM (Observation × Nat) := do
  let snap ← snapshotQ r w
  let mut time := none
  let mut notifications := []
  if snap.active && snap.available then
    let f ← resolveQ w snap.source snap.root
    let _ ← query f 8 (frame w f).x (frame w f).y
    let _ ← query f 10 (frame w f).width (frame w f).height
    let fresh : TimeData := ⟨if snap.axis = 0 then (frame w f).x else (frame w f).y,
                             if snap.axis = 0 then (frame w f).width else (frame w f).height⟩
    time := some fresh
    let notify := match old.time with
      | none => true
      | some prev => fresh.extent != prev.extent
    if notify then
      for i in List.range w.subscribers do
        let _ ← query (3000+i) 23 0 0
        let _ ← query (3000+i) 24 0 0
        notifications := notifications ++ [2*i,2*i+1]
  let exposed ← sourceQ w
  return (⟨⟨some snap,time⟩,time != old.time,notifications,dataNative time⟩,exposed.1)
end Timeline
