import StickyComposition

namespace StickyLifecycle
open MaskedSticky StickyComposition

instance : Inhabited Point := ⟨⟨0, 0⟩⟩
instance : Inhabited Rect := ⟨⟨0, 0, 0, 0⟩⟩
instance : Inhabited Geometry := ⟨⟨default, default⟩⟩

structure Node where
  first : Nat := 0
  next : Option Nat := none
  parent : Option Nat := none
  hadNormal : Bool := false
  sticky : Bool := false
  hasContainer : Bool := false
  normal : Point := default
  current : Point := default
  fallback : Point := default
  offsets : Option Margin := none
  recomputed : Option Margin := none
  currentLimits : Geometry := default
  ignoreLimits : Geometry := default
  deriving Inhabited, Repr

structure World where
  nodes : Array Node
  trace : Array String := #[]
  exhausted : Bool := false
  deriving Inhabited, Repr

structure Input where
  action : Nat
  target : Nat
  reflow : Bool
  primaries : List Nat
  nodes : Array Node
  deriving Repr

abbrev Projection := Option Margin → Point → Rect → Rect → Point

def oldProjection (_ : Option Margin) (n : Point) (s c : Rect) : Point :=
  ⟨original n.x (xLimits s c), original n.y (yLimits s c)⟩

def emit (message : String) : StateM World Unit :=
  modify fun w => {w with trace := w.trace.push message}

def node (i : Nat) : StateM World Node := return (← get).nodes[i]!

def normal (i : Nat) : StateM World Point := do
  let f ← node i
  emit s!"normal:{i}:{if f.hadNormal then 1 else 0}"
  return if f.hadNormal then f.normal else f.current

def offsets (i : Nat) : StateM World (Option Margin) := do
  let f ← node i
  emit s!"offset:{i}:{if f.offsets.isSome then 1 else 0}"
  return f.offsets

def canonical (i : Nat) : StateM World Nat := do
  let f ← node i
  emit s!"first:{i}:{f.first}"
  return f.first

def unbounded : Rect := ⟨-536870911, -536870911, 1073741823, 1073741823⟩

def compute (project : Projection) (repeatLookup : Bool) (i : Nat)
    (space : Space) : StateM World Point := do
  emit s!"limits:{i}:{if space == .current then "current" else "ignore"}"
  let o ← offsets i
  let f ← node i
  let geometry := if o.isNone then Geometry.mk unbounded unbounded
    else if space == .current then f.currentLimits else f.ignoreLimits
  let n ← normal i
  let o ← if repeatLookup then offsets i else pure o
  return project o n geometry.stick geometry.contain

def translation (project : Projection) (repeatLookup : Bool) (i : Nat) :
    StateM World Point := do
  let first ← canonical i
  let p ← compute project repeatLookup first .ignoreScroll
  let q ← normal first
  return minus p q

def setPosition (i : Nat) (p : Point) : StateM World Unit := do
  let f ← node i
  if p != f.current then
    modify fun w => {w with nodes := w.nodes.modify i fun n => {n with current := p}}
    emit s!"set:{i}:{p.x}:{p.y}"

def next (i : Nat) : StateM World (Option Nat) := do
  let f ← node i
  emit s!"next:{i}:{f.next.map Int.ofNat |>.getD (-1)}"
  return f.next

def moveChain (delta : Point) : Nat → Option Nat → StateM World Unit
  | _, none => pure ()
  | 0, some _ => modify fun w => {w with exhausted := true}
  | fuel + 1, some i => do
    let n ← normal i
    setPosition i (plus n delta)
    moveChain delta fuel (← next i)

def continuations (project : Projection) (repeatLookup : Bool) (i : Nat) :
    StateM World Unit := do
  let q ← normal i
  let f ← node i
  if true then
    let p ← compute project repeatLookup i .current
    let fuel := (← get).nodes.size + 1
    moveChain (minus p q) fuel (some i)

def overflowChain (root : Nat) : Nat → Option Nat → StateM World Unit
  | _, none => pure ()
  | 0, some _ => modify fun w => {w with exhausted := true}
  | fuel + 1, some i => do
    emit s!"overflow:{i}"
    let following ← if i == root then do
        emit s!"next:{i}:-1"
        pure none
      else next i
    overflowChain root fuel following

def update (project : Projection) (repeatLookup : Bool) (reflow : Bool)
    (primaries : List Nat) : StateM World Unit := do
  let root := (← get).nodes.size
  let subtree := if reflow then some root else none
  emit s!"subtree:{subtree.map Int.ofNat |>.getD (-1)}"
  emit (primaries.foldl (fun s i => s ++ ":" ++ toString i) "order")
  for i in primaries do
    if reflow then
      emit s!"recompute:{i}"
      modify fun w => {w with nodes := w.nodes.modify i fun f => {f with offsets := f.recomputed}}
    continuations project repeatLookup i
    let parent := (← node i).parent
    if parent != subtree then
      overflowChain root (root + 1) parent
  emit "flush"

def ignoringScrollAndSticky (project : Projection) (repeatLookup : Bool)
    (i : Nat) : StateM World Point := do
  let f ← node i
  if f.sticky then emit s!"container:{i}"
  if f.sticky && f.hasContainer then
    let q ← normal i
    let delta ← translation project repeatLookup i
    return plus q delta
  else
    emit s!"fallback:{i}"
    return f.fallback

def action (project : Projection) (repeatLookup : Bool) (input : Input) :
    StateM World (Option Point) := do
  match input.action with
  | 0 => return some (← compute project repeatLookup input.target .current)
  | 1 => return some (← compute project repeatLookup input.target .ignoreScroll)
  | 2 => return some (← translation project repeatLookup input.target)
  | 3 =>
    continuations project repeatLookup input.target
    return none
  | 4 =>
    update project repeatLookup input.reflow input.primaries
    return none
  | 5 => return some (← ignoringScrollAndSticky project repeatLookup input.target)
  | _ =>
    let p ← compute project repeatLookup input.target .current
    let q ← normal input.target
    return some ⟨if p.y != q.y then 1 else 0, 0⟩

def run (project : Projection) (repeatLookup : Bool) (input : Input) :
    Option Point × World :=
  (action project repeatLookup input).run ⟨input.nodes, #[], false⟩

def observedNormal (n : Node) : Point := if n.hadNormal then n.normal else n.current

def providedGeometry (n : Node) (space : Space) : Geometry :=
  if n.offsets.isNone then ⟨unbounded, unbounded⟩
  else if space == .current then n.currentLimits else n.ignoreLimits

end StickyLifecycle
