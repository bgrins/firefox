import MaskedSticky

namespace StickyComposition
open MaskedSticky

def autoCode : Int := 1073741823

def encodeInset : Option Int → Int
  | none => autoCode
  | some n => n

def ValidInset (v : Option Int) : Prop := ∀ n, v = some n → n ≠ autoCode

theorem encoding_active (v : Option Int) (h : ValidInset v) :
    encodeInset v ≠ autoCode ↔ v.isSome = true := by
  cases v <;> simp_all [encodeInset, ValidInset]

def semanticBounds (near far : Option Int) (l : Limits) : Option Int × Option Int :=
  (near.map (fun _ => lower l), far.map (fun _ => upper l))

theorem bounds_encoding (near far : Option Int) (l : Limits)
    (hn : ValidInset near) (hf : ValidInset far) :
    constraints autoCode (some ⟨encodeInset near, encodeInset far⟩) l =
      semanticBounds near far l := by
  cases near <;> cases far <;> simp_all [constraints, encodeInset, semanticBounds, ValidInset]

theorem semantic_refinement (near far : Option Int) (n : Int) (l : Limits)
    (hn : ValidInset near) (hf : ValidInset far) :
    native autoCode (some ⟨encodeInset near, encodeInset far⟩) n l =
      reference n (semanticBounds near far l) := by
  rw [reference_refinement, bounds_encoding near far l hn hf]

structure Point where
  x : Int
  y : Int
  deriving DecidableEq, Repr

def plus (a b : Point) : Point := ⟨a.x + b.x, a.y + b.y⟩
def minus (a b : Point) : Point := ⟨a.x - b.x, a.y - b.y⟩

structure Rect where
  x : Int
  y : Int
  width : Int
  height : Int
  deriving DecidableEq, Repr

def xMost (r : Rect) : Int := r.x + r.width
def yMost (r : Rect) : Int := r.y + r.height

def RectSafe (r : Rect) : Prop :=
  Representable r.x ∧ Representable r.y ∧ Representable r.width ∧
  Representable r.height ∧ Representable (xMost r) ∧ Representable (yMost r)

theorem rect_edges_exact (r : Rect) (h : RectSafe r) :
    signed32 (signed32 r.x + signed32 r.width) = xMost r ∧
    signed32 (signed32 r.y + signed32 r.height) = yMost r := by
  rcases h with ⟨hx,hy,hw,hh,hxm,hym⟩
  rw [signed32_identity _ hx, signed32_identity _ hy,
    signed32_identity _ hw, signed32_identity _ hh]
  exact ⟨signed32_identity _ hxm, signed32_identity _ hym⟩

def saturate32 (n : Int) : Int := min 2147483647 (max (-2147483648) n)

theorem saturation_exact (n : Int) (h : Representable n) : saturate32 n = n := by
  unfold saturate32 Representable at *
  omega

theorem saturated_rect_edges_exact (r : Rect) (h : RectSafe r) :
    saturate32 (r.x + r.width) = xMost r ∧
    saturate32 (r.y + r.height) = yMost r := by
  exact ⟨saturation_exact _ h.2.2.2.2.1, saturation_exact _ h.2.2.2.2.2⟩

structure Margin where
  top : Int
  right : Int
  bottom : Int
  left : Int
  deriving DecidableEq, Repr

def xLimits (s c : Rect) : Limits := ⟨s.x, xMost s, c.x, xMost c⟩
def yLimits (s c : Rect) : Limits := ⟨s.y, yMost s, c.y, yMost c⟩
def xOffsets (o : Option Margin) : Option Offsets := o.map (fun v => ⟨v.left,v.right⟩)
def yOffsets (o : Option Margin) : Option Offsets := o.map (fun v => ⟨v.top,v.bottom⟩)

def position (o : Option Margin) (normal : Point) (stick contain : Rect) : Point :=
  ⟨native autoCode (xOffsets o) normal.x (xLimits stick contain),
   native autoCode (yOffsets o) normal.y (yLimits stick contain)⟩

def orderedPosition (o : Option Margin) (n : Point) (s c : Rect) : Point :=
  match o with
  | none => n
  | some v =>
    let p := if v.top != autoCode then {n with y := max n.y (min s.y (yMost c))} else n
    let p := if v.bottom != autoCode then {p with y := min p.y (max (yMost s) c.y)} else p
    let p := if v.left != autoCode then {p with x := max p.x (min s.x (xMost c))} else p
    if v.right != autoCode then {p with x := min p.x (max (xMost s) c.x)} else p

theorem ordered_axes_refinement (o : Option Margin) (n : Point) (s c : Rect) :
    orderedPosition o n s c = position o n s c := by
  cases o with
  | none => cases n; rfl
  | some v =>
    by_cases ht : v.top = autoCode <;> by_cases hb : v.bottom = autoCode <;>
      by_cases hl : v.left = autoCode <;> by_cases hr : v.right = autoCode <;>
      simp [orderedPosition, position, xOffsets, yOffsets, native, xLimits, yLimits,
        lower, upper, ht, hb, hl, hr]

def referencePosition (o : Option Margin) (normal : Point) (stick contain : Rect) : Point :=
  ⟨reference normal.x (constraints autoCode (xOffsets o) (xLimits stick contain)),
   reference normal.y (constraints autoCode (yOffsets o) (yLimits stick contain))⟩

theorem position_refinement (o : Option Margin) (n : Point) (s c : Rect) :
    position o n s c = referencePosition o n s c := by
  simp only [position, referencePosition, reference_refinement]

theorem missing_property_identity (n : Point) (s c : Rect) :
    position none n s c = n := by cases n; rfl

theorem all_auto_position_identity (n : Point) (s c : Rect) :
    position (some ⟨autoCode,autoCode,autoCode,autoCode⟩) n s c = n := by
  cases n
  simp [position, xOffsets, yOffsets, all_auto_identity]

theorem horizontal_auto_preserves_x (top bottom : Int) (n : Point) (s c : Rect) :
    (position (some ⟨top,autoCode,bottom,autoCode⟩) n s c).x = n.x := by
  simp [position, xOffsets, all_auto_identity]

theorem vertical_auto_preserves_y (left right : Int) (n : Point) (s c : Rect) :
    (position (some ⟨autoCode,right,autoCode,left⟩) n s c).y = n.y := by
  simp [position, yOffsets, all_auto_identity]

inductive Space where
  | current
  | ignoreScroll
  deriving DecidableEq, Repr

structure Geometry where
  stick : Rect
  contain : Rect
  deriving DecidableEq, Repr

def compute (space : Space) (provider : Space → Geometry) (o : Option Margin) (n : Point) : Point :=
  let g := provider space
  position o n g.stick g.contain

theorem compute_refinement (space : Space) (provider : Space → Geometry)
    (o : Option Margin) (n : Point) :
    compute space provider o n =
      referencePosition o n (provider space).stick (provider space).contain := by
  exact position_refinement o n _ _

structure Frame where
  id : Nat
  normal : Point
  current : Point
  deriving DecidableEq, Repr

def move (delta : Point) (f : Frame) : Frame := {f with current := plus f.normal delta}

def loop (delta : Point) : List Frame → List Frame
  | [] => []
  | f :: rest => move delta f :: loop delta rest

theorem loop_map (delta : Point) (frames : List Frame) :
    loop delta frames = frames.map (move delta) := by
  induction frames with
  | nil => rfl
  | cons f rest ih => simp only [loop, List.map_cons, ih]

def updateContinuations (hadNormal : Bool) (provider : Space → Geometry)
    (o : Option Margin) (frames : List Frame) : List Frame :=
  match frames with
  | [] => []
  | first :: _ =>
    if hadNormal then
      loop (minus (compute .current provider o first.normal) first.normal) frames
    else frames

def referenceContinuations (hadNormal : Bool) (provider : Space → Geometry)
    (o : Option Margin) (frames : List Frame) : List Frame :=
  match frames with
  | [] => []
  | first :: _ =>
    if hadNormal then
      let g := provider .current
      frames.map (move (minus (referencePosition o first.normal g.stick g.contain) first.normal))
    else frames

theorem continuations_refinement (hadNormal : Bool) (provider : Space → Geometry)
    (o : Option Margin) (frames : List Frame) :
    updateContinuations hadNormal provider o frames =
      referenceContinuations hadNormal provider o frames := by
  cases frames with
  | nil => rfl
  | cons f rest =>
    simp only [updateContinuations, referenceContinuations]
    cases hadNormal <;> simp [loop_map, compute_refinement]

theorem missing_normal_preserves_current (provider : Space → Geometry)
    (o : Option Margin) (frames : List Frame) :
    updateContinuations false provider o frames = frames := by cases frames <;> rfl

theorem move_preserves_relative_displacement (a b : Frame) (delta : Point) :
    minus (move delta a).current (move delta b).current = minus a.normal b.normal := by
  simp only [move, minus, plus, Point.mk.injEq]
  omega

theorem move_first_to_computed (f : Frame) (p : Point) :
    (move (minus p f.normal) f).current = p := by
  cases p
  simp only [move, minus, plus, Point.mk.injEq]
  omega

def translationIgnoringScroll (first : Frame) (provider : Space → Geometry)
    (o : Option Margin) : Point :=
  minus (compute .ignoreScroll provider o first.normal) first.normal

theorem translation_canonical (first : Frame) (provider : Space → Geometry)
    (o : Option Margin) :
    translationIgnoringScroll first provider o =
      minus (referencePosition o first.normal (provider .ignoreScroll).stick
        (provider .ignoreScroll).contain) first.normal := by
  simp only [translationIgnoringScroll, compute_refinement]

def PointSafe (p : Point) : Prop := Representable p.x ∧ Representable p.y

theorem translation_machine_exact (a b : Point) (ha : PointSafe a) (hb : PointSafe b)
    (hd : PointSafe (minus a b)) :
    Point.mk (signed32 (signed32 a.x - signed32 b.x))
      (signed32 (signed32 a.y - signed32 b.y)) = minus a b := by
  rcases ha with ⟨hax,hay⟩
  rcases hb with ⟨hbx,hby⟩
  rcases hd with ⟨hdx,hdy⟩
  rw [signed32_identity _ hax, signed32_identity _ hay,
    signed32_identity _ hbx, signed32_identity _ hby]
  simp only [minus] at *
  rw [signed32_identity _ hdx, signed32_identity _ hdy]

theorem addition_machine_exact (a b : Point) (ha : PointSafe a) (hb : PointSafe b)
    (hs : PointSafe (plus a b)) :
    Point.mk (signed32 (signed32 a.x + signed32 b.x))
      (signed32 (signed32 a.y + signed32 b.y)) = plus a b := by
  rcases ha with ⟨hax,hay⟩
  rcases hb with ⟨hbx,hby⟩
  rcases hs with ⟨hsx,hsy⟩
  rw [signed32_identity _ hax, signed32_identity _ hay,
    signed32_identity _ hbx, signed32_identity _ hby]
  simp only [plus] at *
  rw [signed32_identity _ hsx, signed32_identity _ hsy]

end StickyComposition
