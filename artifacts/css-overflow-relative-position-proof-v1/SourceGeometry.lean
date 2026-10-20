import Lean

namespace SourceGeometry

structure P where
  x : Int
  y : Int
  deriving DecidableEq, Repr

def plus (a b : P) : P := ⟨a.x + b.x, a.y + b.y⟩
def minus (a b : P) : P := ⟨a.x - b.x, a.y - b.y⟩

structure WM where
  vertical : Bool
  verticalLR : Bool
  inlineReversed : Bool
  deriving DecidableEq, Repr

def toPhysical (w : WM) (extent logical : P) : P :=
  if w.vertical then
    ⟨if w.verticalLR then logical.y else extent.x - logical.y,
     if w.inlineReversed then extent.y - logical.x else logical.x⟩
  else
    ⟨if w.inlineReversed then extent.x - logical.x else logical.x, logical.y⟩

def fromPhysical (w : WM) (extent physical : P) : P :=
  if w.vertical then
    ⟨if w.inlineReversed then extent.y - physical.y else physical.y,
     if w.verticalLR then physical.x else extent.x - physical.x⟩
  else
    ⟨if w.inlineReversed then extent.x - physical.x else physical.x, physical.y⟩

theorem physical_roundtrip (w : WM) (e p : P) :
    toPhysical w e (fromPhysical w e p) = p := by
  rcases w with ⟨v, lr, rev⟩
  rcases p with ⟨x, y⟩
  cases v <;> cases lr <;> cases rev <;>
    simp [toPhysical, fromPhysical] <;> omega

theorem logical_roundtrip (w : WM) (e p : P) :
    fromPhysical w e (toPhysical w e p) = p := by
  rcases w with ⟨v, lr, rev⟩
  rcases p with ⟨x, y⟩
  cases v <;> cases lr <;> cases rev <;>
    simp [toPhysical, fromPhysical] <;> omega

def rectPhysical (w : WM) (container size logical : P) : P :=
  if w.vertical then
    ⟨if w.verticalLR then logical.y else container.x - (logical.y + size.x),
     if w.inlineReversed then container.y - (logical.x + size.y) else logical.x⟩
  else
    ⟨if w.inlineReversed then container.x - (logical.x + size.x) else logical.x,
     logical.y⟩

theorem rect_point_equivalence (w : WM) (container size logical : P) :
    rectPhysical w container size logical = toPhysical w (minus container size) logical := by
  rcases w with ⟨v, lr, rev⟩
  cases v <;> cases lr <;> cases rev <;>
    simp [rectPhysical, toPhysical, minus] <;> omega

structure Frame where
  size : P
  position : P
  normalProperty : Option P
  deriving DecidableEq, Repr

def getNormal (f : Frame) : P := f.normalProperty.getD f.position

def getLogicalNormal (w : WM) (container : P) (f : Frame) : P :=
  fromPhysical w (minus container f.size) (getNormal f)

def normalInput (w : WM) (container : P) (previous : Frame) : P :=
  ⟨(getLogicalNormal w container previous).x, 0⟩

def normalTarget (w : WM) (container actualSize : P) (previous : Frame) : P :=
  toPhysical w (minus container actualSize) (normalInput w container previous)

-- The physical offset is the current ReflowInput's converted margin.
def sourceFinish (w : WM) (container logical actualSize offset : P) (f : Frame) : Frame :=
  let sized := { f with size := actualSize }
  let extent := minus container sized.size
  let normal := toPhysical w extent logical
  let stored := { sized with normalProperty := some normal }
  let used := plus normal offset
  let converted := fromPhysical w extent used
  { stored with position := rectPhysical w container actualSize converted }

def sourceHelper (w : WM) (container actualSize offset : P)
    (previous current : Frame) : Frame :=
  sourceFinish w container (normalInput w container previous) actualSize offset current

def intended (w : WM) (container actualSize offset : P)
    (previous current : Frame) : Frame :=
  { size := actualSize
    normalProperty := some (normalTarget w container actualSize previous)
    position := plus (normalTarget w container actualSize previous) offset }

theorem helper_commits_actual_size_and_offset (w : WM)
    (container actualSize offset : P) (previous current : Frame) :
    sourceHelper w container actualSize offset previous current =
      intended w container actualSize offset previous current := by
  simp [sourceHelper, sourceFinish, intended, normalTarget, rect_point_equivalence, physical_roundtrip]

theorem stored_normal_is_unshifted (w : WM) (container actualSize offset : P)
    (previous current : Frame) :
    (sourceHelper w container actualSize offset previous current).normalProperty =
      some (normalTarget w container actualSize previous) := rfl

theorem arbitrary_callback_size_used (w : WM) (container actualSize offset : P)
    (previous current : Frame) :
    (sourceHelper w container actualSize offset previous current).size = actualSize := rfl

def sourceUpdate (offset : P) (f : Frame) : Frame :=
  let normal := getNormal f
  let initialized := match f.normalProperty with
    | some _ => f
    | none => { f with normalProperty := some normal }
  { initialized with position := plus normal offset }

theorem update_uses_committed_normal (w : WM) (container actualSize initial next : P)
    (previous current : Frame) :
    sourceUpdate next (sourceHelper w container actualSize initial previous current) =
      sourceHelper w container actualSize next previous current := by
  rw [helper_commits_actual_size_and_offset, helper_commits_actual_size_and_offset]
  simp [sourceUpdate, intended, getNormal]

theorem repeated_update_idempotent (w : WM) (container actualSize initial next : P)
    (previous current : Frame) :
    sourceUpdate next (sourceUpdate next (sourceHelper w container actualSize initial previous current)) =
      sourceUpdate next (sourceHelper w container actualSize initial previous current) := by
  rw [update_uses_committed_normal, update_uses_committed_normal]

theorem callback_old_frame_irrelevant (w : WM) (container actualSize offset : P)
    (previous current other : Frame) :
    sourceHelper w container actualSize offset previous current =
      sourceHelper w container actualSize offset previous other := by
  rw [helper_commits_actual_size_and_offset, helper_commits_actual_size_and_offset]
  rfl

theorem predecessor_used_irrelevant_when_property_exists
    (w : WM) (container actualSize offset normal : P) (previous current : Frame)
    (different : P) :
    sourceHelper w container actualSize offset
      { previous with normalProperty := some normal } current =
    sourceHelper w container actualSize offset
      { previous with normalProperty := some normal, position := different } current := by
  simp [sourceHelper, normalInput, getLogicalNormal, getNormal]

theorem absent_property_falls_back (f : Frame) (h : f.normalProperty = none) :
    getNormal f = f.position := by simp [getNormal, h]

def s32 (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647

def fits (p : P) : Prop := s32 p.x ∧ s32 p.y

def toSafe (w : WM) (e p : P) : Prop :=
  fits p ∧ fits e ∧
  (if w.vertical then
    (if w.verticalLR then True else s32 (e.x - p.y)) ∧
    (if w.inlineReversed then s32 (e.y - p.x) else True)
   else if w.inlineReversed then s32 (e.x - p.x) else True)

def fromSafe (w : WM) (e p : P) : Prop :=
  fits p ∧ fits e ∧
  (if w.vertical then
    (if w.inlineReversed then s32 (e.y - p.y) else True) ∧
    (if w.verticalLR then True else s32 (e.x - p.x))
   else if w.inlineReversed then s32 (e.x - p.x) else True)

theorem toSafe_result (w : WM) (e p : P) (h : toSafe w e p) : fits (toPhysical w e p) := by
  rcases w with ⟨v, lr, rev⟩
  cases v <;> cases lr <;> cases rev <;>
    simp_all [toSafe, toPhysical, fits]

theorem fromSafe_result (w : WM) (e p : P) (h : fromSafe w e p) : fits (fromPhysical w e p) := by
  rcases w with ⟨v, lr, rev⟩
  cases v <;> cases lr <;> cases rev <;>
    simp_all [fromSafe, fromPhysical, fits]

def rectSafe (w : WM) (container size logical : P) : Prop :=
  fits container ∧ fits size ∧ fits logical ∧
  (if w.vertical then
    (if w.verticalLR then True else
      s32 (logical.y + size.x) ∧ s32 (container.x - (logical.y + size.x))) ∧
    (if w.inlineReversed then
      s32 (logical.x + size.y) ∧ s32 (container.y - (logical.x + size.y)) else True)
  else if w.inlineReversed then
    s32 (logical.x + size.x) ∧ s32 (container.x - (logical.x + size.x)) else True)

structure ExecutedDomain (w : WM) (container actualSize offset : P) (previous : Frame) : Prop where
  containerFits : fits container
  previousSizeFits : fits previous.size
  actualSizeFits : fits actualSize
  offsetFits : fits offset
  previousExtent : fits (minus container previous.size)
  actualExtent : fits (minus container actualSize)
  previousConversion : fromSafe w (minus container previous.size) (getNormal previous)
  normalConversion : toSafe w (minus container actualSize) (normalInput w container previous)
  addition : fits (plus (normalTarget w container actualSize previous) offset)
  inverseConversion : fromSafe w (minus container actualSize)
    (plus (normalTarget w container actualSize previous) offset)
  commitConversion : toSafe w (minus container actualSize)
    (fromPhysical w (minus container actualSize)
      (plus (normalTarget w container actualSize previous) offset))
  rectCommit : rectSafe w container actualSize
    (fromPhysical w (minus container actualSize)
      (plus (normalTarget w container actualSize previous) offset))

def smallSize (p : P) : Prop :=
  0 ≤ p.x ∧ p.x ≤ 1000000 ∧ 0 ≤ p.y ∧ p.y ≤ 1000000

def smallPoint (p : P) : Prop :=
  -1000000 ≤ p.x ∧ p.x ≤ 1000000 ∧ -1000000 ≤ p.y ∧ p.y ≤ 1000000

theorem small_inputs_derive_executed_domain (w : WM) (container actualSize offset : P)
    (previous : Frame) (hc : smallSize container) (hp : smallSize previous.size)
    (hs : smallSize actualSize) (hn : smallPoint (getNormal previous))
    (ho : smallPoint offset) : ExecutedDomain w container actualSize offset previous := by
  rcases w with ⟨v, lr, rev⟩
  cases v <;> cases lr <;> cases rev <;> constructor <;>
    simp_all [fits, s32, smallSize, smallPoint, minus, plus, fromSafe, toSafe,
      rectSafe, normalInput, getLogicalNormal, normalTarget, fromPhysical, toPhysical] <;> omega

theorem domain_committed_position_fits (w : WM) (container actualSize offset : P)
    (previous current : Frame) (h : ExecutedDomain w container actualSize offset previous) :
    fits (sourceHelper w container actualSize offset previous current).position := by
  rw [helper_commits_actual_size_and_offset]
  exact h.addition

inductive PositionStyle where
  | staticPosition | relative | sticky
  deriving DecidableEq, Repr

def isRelative (style : PositionStyle) (inSVGText : Bool) : Bool :=
  style == .relative && !inSVGText

def isPositioned (style : PositionStyle) (inSVGText : Bool) : Bool :=
  (style == .relative || style == .sticky) && !inSVGText

theorem actual_guard_implies_apply_guard (style : PositionStyle) (svg : Bool)
    (h : isRelative style svg = true) :
    isPositioned style svg = true ∧ style = .relative := by
  cases style <;> cases svg <;> simp_all [isRelative, isPositioned]

def defaultHelper (style : PositionStyle) (svg : Bool) (w : WM)
    (container actualSize offset : P) (previous current : Frame) : Frame :=
  if isRelative style svg then sourceHelper w container actualSize offset previous current
  else
    let i := (fromPhysical w (minus container previous.size) previous.position).x
    { size := actualSize
      normalProperty := current.normalProperty
      position := toPhysical w (minus container actualSize) ⟨i, 0⟩ }

def oldDefaultHelper (w : WM) (container actualSize : P)
    (previous current : Frame) : Frame :=
  let i := (fromPhysical w (minus container previous.size) previous.position).x
  { size := actualSize
    normalProperty := current.normalProperty
    position := toPhysical w (minus container actualSize) ⟨i, 0⟩ }

theorem nonrelative_default_preserved (style : PositionStyle) (svg : Bool)
    (w : WM) (container actualSize offset : P) (previous current : Frame)
    (h : isRelative style svg = false) :
    defaultHelper style svg w container actualSize offset previous current =
      oldDefaultHelper w container actualSize previous current := by
  simp [defaultHelper, oldDefaultHelper, h]

theorem dynamic_normal_property_preserved (f : Frame) (normal offset : P)
    (h : f.normalProperty = some normal) :
    (sourceUpdate offset f).normalProperty = some normal := by
  simp [sourceUpdate, getNormal, h]

structure Step where
  wm : WM
  container : P
  size : P
  offset : P

def continueFrame (step : Step) (previous : Frame) : Frame :=
  sourceHelper step.wm step.container step.size step.offset previous previous

def chain (steps : List Step) (initial : Frame) : Frame :=
  steps.foldl (fun previous step => continueFrame step previous) initial

theorem continuation_always_initializes (step : Step) (previous : Frame) :
    ∃ normal, (continueFrame step previous).normalProperty = some normal := by
  exact ⟨_, rfl⟩

theorem nonempty_chain_has_normal (first : Step) (rest : List Step) (initial : Frame) :
    ∃ normal, (chain (first :: rest) initial).normalProperty = some normal := by
  simp only [chain, List.foldl_cons]
  generalize h : continueFrame first initial = start
  have base : ∃ normal, start.normalProperty = some normal := by
    rw [← h]; exact continuation_always_initializes first initial
  clear h
  induction rest generalizing start with
  | nil => exact base
  | cons next tail ih =>
    simp only [List.foldl_cons]
    apply ih
    exact continuation_always_initializes next start

theorem final_fit_does_not_bound_rect_end :
    s32 ((2147483647 : Int) - 1 - 2147483647) ∧
    ¬ s32 ((2147483647 : Int) + 1) := by
  unfold s32
  decide


#print axioms small_inputs_derive_executed_domain
#print axioms final_fit_does_not_bound_rect_end
#print axioms rect_point_equivalence
#print axioms physical_roundtrip
#print axioms logical_roundtrip
#print axioms helper_commits_actual_size_and_offset
#print axioms stored_normal_is_unshifted
#print axioms arbitrary_callback_size_used
#print axioms update_uses_committed_normal
#print axioms repeated_update_idempotent
#print axioms callback_old_frame_irrelevant
#print axioms predecessor_used_irrelevant_when_property_exists
#print axioms absent_property_falls_back
#print axioms toSafe_result
#print axioms fromSafe_result
#print axioms domain_committed_position_fits

#print axioms actual_guard_implies_apply_guard
#print axioms nonrelative_default_preserved
#print axioms dynamic_normal_property_preserved
#print axioms continuation_always_initializes
#print axioms nonempty_chain_has_normal

end SourceGeometry
