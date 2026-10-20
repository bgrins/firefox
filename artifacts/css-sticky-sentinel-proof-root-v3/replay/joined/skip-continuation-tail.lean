import StickyIndexed

namespace StickyMachineLifecycle
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed

def machinePoint (p : Point) : Point := ⟨signed32 p.x, signed32 p.y⟩
def machinePlus (a b : Point) : Point :=
  ⟨signed32 (signed32 a.x + signed32 b.x), signed32 (signed32 a.y + signed32 b.y)⟩
def machineMinus (a b : Point) : Point :=
  ⟨signed32 (signed32 a.x - signed32 b.x), signed32 (signed32 a.y - signed32 b.y)⟩
def machineXMost (r : Rect) : Int := saturate32 (signed32 r.x + signed32 r.width)
def machineYMost (r : Rect) : Int := saturate32 (signed32 r.y + signed32 r.height)

def machinePosition (o : Option Margin) (n : Point) (s c : Rect) : Point :=
  let n := machinePoint n
  match o with
  | none => n
  | some v =>
    let p := if v.top != autoCode then
      {n with y := max n.y (min (signed32 s.y) (machineYMost c))} else n
    let p := if v.bottom != autoCode then
      {p with y := min p.y (max (machineYMost s) (signed32 c.y))} else p
    let p := if v.left != autoCode then
      {p with x := max p.x (min (signed32 s.x) (machineXMost c))} else p
    if v.right != autoCode then
      {p with x := min p.x (max (machineXMost s) (signed32 c.x))} else p

def ComputeSafe (w : World) (i : Nat) (space : Space) : Prop :=
  let n := w.nodes[i]!
  let g := providedGeometry n space
  PointSafe (observedNormal n) ∧ RectSafe g.stick ∧ RectSafe g.contain

def machineStep (d : Point) (i : Nat) : StateM World (Option Nat) := do
  let n ← normal i
  setPosition i (machinePlus n d)
  next i

def machineMoveChain (d : Point) : Nat → Option Nat → StateM World Unit
  | _, none => pure ()
  | 0, some _ => modify fun w => {w with exhausted := true}
  | fuel + 1, some i => do
    let n ← normal i
    setPosition i (machinePlus n d)
    pure ()

def LoopSafe (w : World) (ids : List Nat) (d : Point) : Prop :=
  PointSafe d ∧ ∀ i ∈ ids,
    PointSafe (observedNormal w.nodes[i]!) ∧
    PointSafe (plus (observedNormal w.nodes[i]!) d)

def computedReference (w : World) (i : Nat) (space : Space) : Point :=
  let n := w.nodes[i]!
  let g := providedGeometry n space
  referencePosition n.offsets (observedNormal n) g.stick g.contain

def machineContinuations (repeatLookup : Bool) (i : Nat) : StateM World Unit := do
  let q ← normal i
  let f ← node i
  if f.hadNormal then
    let p ← StickyLifecycle.compute machinePosition repeatLookup i .current
    let fuel := (← get).nodes.size + 1
    machineMoveChain (machineMinus p q) fuel (some i)

def ContinuationSafe (w : World) (i : Nat) (ids : List Nat) : Prop :=
  w.nodes[i]!.hadNormal = true →
    ComputeSafe w i .current ∧ PointSafe (computedReference w i .current) ∧
    PointSafe (referenceDelta w i) ∧ LoopSafe w ids (referenceDelta w i)

def machineTranslation (repeatLookup : Bool) (i : Nat) : StateM World Point := do
  let first ← canonical i
  let p ← StickyLifecycle.compute machinePosition repeatLookup first .ignoreScroll
  let q ← normal first
  return machineMinus p q

def TranslationSafe (w : World) (i : Nat) : Prop :=
  let first := w.nodes[i]!.first
  ComputeSafe w first .ignoreScroll ∧ PointSafe (computedReference w first .ignoreScroll) ∧
    PointSafe (canonicalReference w i)

def machineFrame (repeatLookup : Bool) (i : Nat) : StateM World Point := do
  let f ← node i
  if f.sticky then emit s!"container:{i}"
  if f.sticky && f.hasContainer then
    let q ← normal i
    let delta ← machineTranslation repeatLookup i
    return machinePlus q delta
  else
    emit s!"fallback:{i}"
    return f.fallback

def FrameSafe (w : World) (i : Nat) : Prop :=
  (w.nodes[i]!.sticky && w.nodes[i]!.hasContainer) = true →
    TranslationSafe w i ∧ PointSafe (observedNormal w.nodes[i]!) ∧
    PointSafe (plus (observedNormal w.nodes[i]!) (canonicalReference w i))

def framePrefix (i : Nat) : StateM World Point := do
  emit s!"container:{i}"
  normal i

end StickyMachineLifecycle
