import Lean

namespace LineModel

def bit (b : Bool) : Int := if b then 1 else 0
abbrev Trace := List (List Int)
structure Marker where
  width : Int := 0
  intrinsic : Int := 0
  style : Nat := 0
  overflow : Bool := false
  block : Int := -1
  initialized : Bool := false
  active : Bool := false
  edge : Bool := false
  deriving BEq, Repr, Inhabited, DecidableEq
structure Pair where
  start : Marker
  finish : Marker
  deriving BEq, Repr, Inhabited, DecidableEq
structure Style where
  kind : Nat
  width : Int
  length : Nat
  deriving Repr, Inhabited
structure Rect where
  i : Int := 0
  b : Int := 0
  w : Int := 0
  h : Int := 1
  deriving Repr, Inhabited
structure Frame where
  parent : Int
  role : Nat
  visible : Bool
  nonsuppressed : Bool
  start : Int
  size : Int
  overflowStart : Int
  overflowEnd : Int
  advances : List Int
  deriving Repr, Inhabited
structure Line where
  frames : Array Frame
  overflowStart : Int
  overflowEnd : Int
  floats : Option (Int × Int)
  clamp : Option Style
  deriving Repr, Inhabited
structure Config where
  id : Nat
  start : Int
  width : Int
  styles : Array Style
  seed : Bool
  ellipsisWidth : Int
  ellipsisFailure : Bool
  scroll : Option (Int × Int × Int)
  snap : Bool
  units : Int
  lines : List Line
  deriving Repr, Inhabited

def packed (m : Marker) : List Int :=
  [m.width,m.intrinsic,m.style,bit m.overflow,m.block,bit m.initialized,bit m.active,bit m.edge]
def markers (s : Pair) := packed s.start ++ packed s.finish
def reset (m : Marker) : Marker := { m with overflow := false, block := -1, edge := false }
def canonical (m : Marker) : Marker := { reset m with width := m.intrinsic }
def canonicalPair (s : Pair) : Pair := ⟨canonical s.start, canonical s.finish⟩
def rect (a b : Int) : Rect := ⟨a,0,b-a,1⟩
def rp (r : Rect) := [r.i,r.b,r.w,r.h]
def shrinkStart (r : Rect) (w : Int) : Rect := {r with i := r.i+w,w := max (r.w-w) 0}
def shrinkEnd (r : Rect) (w : Int) : Rect := {r with w := max (r.w-w) 0}
def intersect (a b : Rect) : Rect := Id.run do
  let i := max a.i b.i
  let j := max a.b b.b
  let w := min (a.i+a.w) (b.i+b.w)-i
  let h := min (a.b+a.h) (b.b+b.h)-j
  return if min w h < 0 then ⟨i,j,0,0⟩ else ⟨i,j,w,h⟩
def blockStyle (m : Marker) (l : Line) := if m.block >= 0 then l.clamp else none
def hasBlock (m : Marker) (l : Line) : Bool :=
  match blockStyle m l with
  | none => false
  | some s => s.kind != 0 && (s.kind != 2 || s.length != 0)
def needed (m : Marker) (l : Line) := m.overflow || hasBlock m l
def suppressed (m : Marker) (c : Config) (l : Line) :=
  if m.block >= 0 then !(hasBlock m l) else c.styles[m.style]!.kind == 0

def measure (m : Marker) (c : Config) (l : Line) : Marker × Trace := Id.run do
  if m.initialized then return (m,[])
  let block := blockStyle m l
  let s := block.getD c.styles[m.style]!
  let w := if s.kind == 1 then (if c.ellipsisFailure then 0 else c.ellipsisWidth) else s.width
  let event := if s.kind == 1 then [2,-1,w,bit c.ellipsisFailure]
    else [2,if block.isSome then m.block else m.style,w,0]
  return ({m with width := w,intrinsic := w,initialized := true},[event])
def initial (c : Config) : Pair := Id.run do
  let seed := fun (side : Nat) =>
    let m : Marker := {style := side}
    let s := c.styles[side]!
    let w := if s.kind == 0 then 0 else if s.kind == 1 then
      (if c.ellipsisFailure then 0 else c.ellipsisWidth) else s.width
    if c.seed then {m with width := w,intrinsic := w,initialized := true} else m
  return ⟨seed 0,seed 1⟩

structure Align where
  left : Int := 0
  right : Int := 0
  outer : Int := 0
  assigned : Bool := false
  deriving Repr, Inhabited
structure Clips where
  left : Int := 0
  right : Int := 0
  hasLeft : Bool := false
  hasRight : Bool := false
  deriving Repr, Inhabited
structure Analysis where
  state : Pair
  align : Align := {}
  hidden : List Nat := []
  clips : Clips := {}
  visible : Bool := false
  deriving Repr, Inhabited

def addInner (a : Align) (left right : Int) : Align :=
  {a with left := if a.assigned then min a.left left else left,     right := if a.assigned then max a.right right else right,assigned := true}
def insertHidden (xs : List Nat) (n : Nat) := (if xs.contains n then xs else n::xs).mergeSort (· ≤ ·)
def analysis (l : Line) (content inside : Rect) (s : Pair) (align : Align) (hidden : List Nat) : Analysis := Id.run do
  let mut result : Analysis := {state := s,align := align,hidden := hidden}
  let mut reachable : List Nat := []
  for index in [:l.frames.size] do
    let f := l.frames[index]!
    if f.parent >= 0 then
      let p := f.parent.toNat
      if !reachable.contains p || [2,3,4].contains l.frames[p]!.role then continue
    reachable := index :: reachable
    if [3,4].contains f.role || !f.visible then continue
    let a := f.start
    let b := a+f.size
    let ovStart := f.overflowStart < content.i
    let ovEnd := f.overflowEnd > content.i+content.w
    result := {result with state :=       ⟨{result.state.start with overflow := result.state.start.overflow || ovStart},        {result.state.finish with overflow := result.state.finish.overflow || ovEnd}⟩}
    if f.role == 2 && ((s.start.active && ovStart) || (s.finish.active && ovEnd)) then
      result := {result with hidden := insertHidden result.hidden index}
      continue
    if f.role != 1 && f.role != 2 then continue
    let overlapStart := max (inside.i-a) 0
    let overlapEnd := max (b-inside.i-inside.w) 0
    if overlapStart > 0 then
      result := {result with clips := {result.clips with hasLeft := true,         left := if result.clips.hasLeft then max result.clips.left a else a}}
    if overlapEnd > 0 then
      result := {result with clips := {result.clips with hasRight := true,         right := if result.clips.hasRight then min result.clips.right b else b}}
    let cutStart := if s.start.active then overlapStart else 0
    let cutEnd := if s.finish.active then overlapEnd else 0
    let crossing := (cutStart > 0 && inside.i <= b) || (cutEnd > 0 && a <= inside.i+inside.w)
    if crossing then
      if f.role == 2 then result := {result with hidden := insertHidden result.hidden index}
      else if inside.w > 0 && f.nonsuppressed then
        let mut position := 0
        let mut clusters : List (Int × Int) := []
        for advance in f.advances do
          let endPos := position+advance
          if position >= cutStart && endPos <= f.size-cutEnd then clusters := clusters ++ [(position,endPos)]
          position := endPos
        if let some first := clusters.head? then
          let last := clusters.getLast!
          result := {result with visible := true,align := addInner result.align             (if cutStart > 0 then a+first.1 else a)             (if cutEnd > 0 then a+last.2 else b)}
    else if inside.i > b || a > inside.i+inside.w then
      if inside.i > b then result := {result with align := {result.align with outer := max result.align.outer b}}
      if f.role == 2 then result := {result with hidden := insertHidden result.hidden index}
    else
      result := {result with align := addInner result.align a b,         visible := result.visible || f.role == 2 || f.nonsuppressed}
  return result

structure Loop where
  state : Pair
  align : Align := {}
  hidden : List Nat := []
  guessStart : Bool
  guessEnd : Bool
  clippedStart : Bool := false
  clippedEnd : Bool := false
  retry : Bool := true
  pass : Nat := 0
  events : Trace := []
  deriving Repr, Inhabited

def attemptEvent (content inside : Rect) (a : Analysis) : List Int :=
  [1] ++ rp content ++ rp inside ++ markers a.state ++
    [bit a.visible,a.align.left,a.align.right,a.align.outer,bit a.align.assigned,
      a.clips.left,a.clips.right,bit a.clips.hasLeft,bit a.clips.hasRight,a.hidden.length] ++ a.hidden.map Int.ofNat

def retryLoop (fuel : Nat) (c : Config) (l : Line) (area content : Rect)
    (wantStart wantEnd : Bool) (v : Loop) : Except String Loop := do
  match fuel with
  | 0 => throw "attempt bound"
  | fuel+1 =>
    let (start,se) := if v.guessStart then measure v.state.start c l else (v.state.start,[])
    let (finish,ee) := if v.guessEnd then measure v.state.finish c l else (v.state.finish,[])
    let reservationEnd := if finish.active then finish.width else 0
    let rawStart := if start.active then start.width else 0
    let reservationStart := if rawStart != 0 && reservationEnd != 0 && rawStart+reservationEnd > content.w then 0 else rawStart
    let inside := if v.guessStart then shrinkStart area reservationStart else area
    let inside := if v.guessEnd then shrinkEnd inside reservationEnd else inside
    let a := analysis l content inside ⟨start,finish⟩ v.align v.hidden
    let mut v := {v with state := a.state,align := a.align,hidden := a.hidden,       events := v.events ++ se ++ ee ++ [attemptEvent content inside a]}
    if !a.visible && v.retry then
      v := {v with align := {v.align with outer := 0,assigned := false},hidden := [],pass := 0}
      if needed v.state.start l && v.state.start.active && !v.clippedStart then
        let available := a.clips.left-area.i
        if a.clips.hasLeft && available > 0 then
          if available >= v.state.start.intrinsic then throw "start width invariant"
          v := {v with state := {v.state with start := {v.state.start with width := available}},clippedStart := true}
        else v := {v with state := {v.state with start := {v.state.start with active := false}},guessStart := false}
      else if needed v.state.finish l && v.state.finish.active && !v.clippedEnd then
        let available := area.i+area.w-a.clips.right
        if a.clips.hasRight && available > 0 then
          if available >= v.state.finish.intrinsic then throw "end width invariant"
          v := {v with state := {v.state with finish := {v.state.finish with width := available}},clippedEnd := true}
        else v := {v with state := {v.state with finish := {v.state.finish with active := false}},guessEnd := false}
      else
        v := {v with retry := false,guessStart := wantStart,guessEnd := wantEnd,           state := ⟨{v.state.start with width := v.state.start.intrinsic,active := wantStart},             {v.state.finish with width := v.state.finish.intrinsic,active := wantEnd}⟩}
        if needed v.state.finish l && v.state.finish.active && hasBlock v.state.finish l then
          if area.i <= v.align.outer then throw "clamp out of view invariant"
          v := {v with state := {v.state with finish := {v.state.finish with             width := max (v.state.finish.intrinsic-area.i+v.align.outer) 0}}}
      retryLoop fuel c l area content wantStart wantEnd v
    else
      let actualStart := v.state.start.active && needed v.state.start l
      let actualEnd := v.state.finish.active && needed v.state.finish l
      if v.guessStart == actualStart && v.guessEnd == actualEnd then return v
      if v.pass != 0 then throw "retry pass invariant"
      v := {v with guessStart := actualStart,guessEnd := actualEnd,pass := v.pass+1,hidden := [],         state := ⟨reset v.state.start,{reset v.state.finish with block := v.state.finish.block}⟩}
      retryLoop fuel c l area content wantStart wantEnd v

structure KernelResult where
  state : Pair
  area : Rect
  align : Align
  hidden : List Nat
  events : Trace
  deriving Repr

def kernel (c : Config) (l : Line) (s : Pair) : Except String KernelResult := do
  let mut suppressStart := suppressed s.start c l
  let mut suppressEnd := suppressed s.finish c l
  if let some (pos,lo,hi) := c.scroll then
    suppressStart := suppressStart || pos <= lo
    suppressEnd := suppressEnd || (pos >= hi && !hasBlock s.finish l)
  let mut area := rect c.start (c.start+c.width)
  let mut snapStart := true
  let mut snapEnd := true
  if let some (lo,hi) := l.floats then
    if hi < area.i+area.w then
      area := {area with w := max (hi-area.i) 0}
      snapEnd := false
    if lo > area.i then
      area := shrinkStart area (lo-area.i)
      snapStart := false
  let mut content := area
  if c.snap then
    if snapStart then content := shrinkStart content (-c.units)
    if snapEnd then content := shrinkEnd content (-c.units)
  let wantStart := !suppressStart && l.overflowStart < content.i
  let wantEnd := !suppressEnd && (l.overflowEnd > content.i+content.w || hasBlock s.finish l)
  if !wantStart && !wantEnd then return ⟨s,area,{},[],[]⟩
  let s : Pair := ⟨{s.start with active := wantStart,edge := c.scroll.isSome && wantStart},
    {s.finish with active := wantEnd,edge := c.scroll.isSome && !suppressEnd && l.overflowEnd > content.i+content.w}⟩
  let v ← retryLoop 12 c l area content wantStart wantEnd {state := s,guessStart := wantStart,guessEnd := wantEnd}
  let s := ⟨if !wantStart || !v.state.start.active then reset v.state.start else v.state.start,
    if !wantEnd || !v.state.finish.active then reset v.state.finish else v.state.finish⟩
  return ⟨s,area,v.align,v.hidden,v.events⟩

def entry (c : Config) (s : Pair) (candidate : Bool) : Pair :=
  ⟨{reset s.start with width := if candidate then s.start.intrinsic else s.start.width,       active := c.styles[0]!.kind != 0},
    {reset s.finish with width := if candidate then s.finish.intrinsic else s.finish.width}⟩

def prepare (c : Config) (l : Line) (number : Nat) (s : Pair)
    (candidate : Bool) : Pair × Option Marker := Id.run do
  let mut s := entry c s candidate
  let previous := if l.clamp.isSome then some s.finish else none
  if l.clamp.isSome then s := {s with finish := {s.finish with block := number+2,initialized := false}}
  s := {s with finish := {s.finish with active := !suppressed s.finish c l}}
  return (s,previous)

def process (c : Config) (l : Line) (number : Nat) (s : Pair)
    (candidate : Bool := true) : Except String (Pair × Trace) := do
  let mut events : Trace := [[0] ++ markers s]
  if c.styles.all (fun s => s.kind == 0) && l.clamp.isNone then
    return (s,events ++ [[9] ++ markers s])
  let (prepared,previous) := prepare c l number s candidate
  let mut s := prepared
  let k ← kernel c l s
  s := k.state
  events := events ++ k.events
  let mut needStart := needed s.start l
  let needEnd := needed s.finish l
  if needStart || needEnd then
    if (suppressed s.start c l && needStart) || (suppressed s.finish c l && needEnd) then throw "suppression invariant"
    if needStart && needEnd && s.start.width+s.finish.width > k.area.w then needStart := false
    let mut inside := if needStart then shrinkStart k.area s.start.width else k.area
    if needEnd then inside := shrinkEnd inside s.finish.width
    if k.align.assigned then
      let left := if s.start.edge then inside.i else k.align.left
      let right := if s.finish.edge then inside.i+inside.w else k.align.right
      inside := intersect inside (rect left right)
    else if hasBlock s.finish l then inside := rect k.align.outer k.align.outer
    for listId in ([0,1] : List Int) do
      events := events ++ [[3,listId] ++ rp inside ++ markers s ++ [Int.ofNat k.hidden.length] ++ k.hidden.map Int.ofNat]
    events := events ++ [[4,bit needStart,bit needEnd,number] ++ rp inside ++ rp k.area ++ markers s]
    if let some old := previous then s := {s with finish := old}
  return (s,events ++ [[9] ++ markers s])

def run (c : Config) (candidate : Bool := true) : Except String (List (Nat × String × Trace)) := do
  let mut s := initial c
  let mut rows := []
  for (line,number) in c.lines.zipIdx do
    let fresh := canonicalPair s
    let (next,events) ← process c line number s candidate
    let (_,freshEvents) ← process c line number fresh candidate
    rows := rows ++ [(number,"reuse",events),(number,"fresh",freshEvents)]
    s := next
  return rows
end LineModel
