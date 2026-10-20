import Origin

namespace VariableOrigin

structure ReferenceSpan where
  start : Nat
  stop : Nat
  fallback : Option Nat
  deriving DecidableEq, Repr

def spanShift (delta : Nat) (s : ReferenceSpan) : ReferenceSpan :=
  ⟨delta + s.start, delta + s.stop, s.fallback.map (delta + ·)⟩

def referenceSpans : Component → List ReferenceSpan
  | .text _ => []
  | .leafReference s => [⟨0, byteLength s, none⟩]
  | .pair a b => referenceSpans a ++ (referenceSpans b).map (spanShift (byteLength (render a)))
  | .block a b _ => (referenceSpans b).map (spanShift (byteLength a))
  | .reference a b c =>
      ⟨0, byteLength (a ++ render b ++ c), some (byteLength a)⟩ ::
      (referenceSpans b).map (spanShift (byteLength a))

def spanPoints (s : ReferenceSpan) : List Point :=
  [⟨.referenceStart, s.start⟩, ⟨.referenceEnd, s.stop⟩] ++
    (s.fallback.toList.map fun p => ⟨.fallbackStart, p⟩)

theorem spanPoints_shift (delta : Nat) (s : ReferenceSpan) :
    spanPoints (spanShift delta s) = translated delta (spanPoints s) := by
  cases s with
  | mk a b f => cases f <;> simp [spanPoints, spanShift, translated, shift]

theorem flatMap_shift (delta : Nat) (rs : List ReferenceSpan) :
    (rs.map (spanShift delta)).flatMap spanPoints = translated delta (rs.flatMap spanPoints) := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
      simp only [List.map_cons, List.flatMap_cons, translated_append, spanPoints_shift]
      rw [ih]

theorem spans_layout (tree : Component) :
    (referenceSpans tree).flatMap spanPoints = layout tree := by
  induction tree with
  | text _ => rfl
  | leafReference _ => rfl
  | pair a b ia ib =>
      simp only [referenceSpans, layout, List.flatMap_append, flatMap_shift, ia, ib]
  | block a b c ih =>
      simp only [referenceSpans, layout, flatMap_shift, ih]
  | reference a b c ih =>
      simp only [referenceSpans, layout, List.flatMap_cons, flatMap_shift, ih]
      rfl

def ValidHeaders : Component → Prop
  | .text _ => True
  | .leafReference s => 0 < byteLength s
  | .pair a b => ValidHeaders a ∧ ValidHeaders b
  | .block _ b _ => ValidHeaders b
  | .reference a b c => 0 < byteLength a ∧ c = [')'] ∧ ValidHeaders b

def SpanOrdered (s : ReferenceSpan) : Prop :=
  s.start < s.stop ∧ ∀ p, s.fallback = some p → s.start < p ∧ p < s.stop

theorem shift_ordered (delta : Nat) (s : ReferenceSpan) (h : SpanOrdered s) :
    SpanOrdered (spanShift delta s) := by
  rcases s with ⟨a,b,f⟩
  cases f with
  | none => simpa [SpanOrdered, spanShift] using h
  | some p =>
      simp only [SpanOrdered, spanShift, Option.map_some, Option.some.injEq] at *
      constructor
      · omega
      · intro x hx
        obtain ⟨h1,h2⟩ := h.2 p rfl
        constructor <;> omega

theorem spans_ordered (tree : Component) (valid : ValidHeaders tree) :
    ∀ s ∈ referenceSpans tree, SpanOrdered s := by
  induction tree with
  | text _ => simp [referenceSpans]
  | leafReference chars =>
      intro s hs
      simp only [referenceSpans, List.mem_singleton] at hs
      subst s
      simpa [SpanOrdered, ValidHeaders] using valid
  | pair a b ia ib =>
      intro s hs
      simp only [referenceSpans, List.mem_append] at hs
      rcases hs with hs | hs
      · exact ia valid.1 s hs
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hs
        exact shift_ordered _ q (ib valid.2 q hq)
  | block a b c ih =>
      intro s hs
      obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hs
      exact shift_ordered _ q (ih valid q hq)
  | reference a b c ih =>
      intro s hs
      simp only [referenceSpans, List.mem_cons] at hs
      rcases hs with rfl | hs
      · obtain ⟨ha,hclose,_⟩ := valid
        have hc : 0 < byteLength c := by rw [hclose]; decide
        simp only [SpanOrdered, byteLength_append, Option.some.injEq]
        constructor
        · omega
        · intro p hp
          constructor <;> omega
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hs
        exact shift_ordered _ q (ih valid.2.2 q hq)

theorem span_boundaries (tree : Component) (s : ReferenceSpan)
    (hs : s ∈ referenceSpans tree) :
    Boundary (render tree) s.start ∧ Boundary (render tree) s.stop ∧
    ∀ p, s.fallback = some p → Boundary (render tree) p := by
  have hp : ∀ p ∈ spanPoints s, Boundary (render tree) p.offset := by
    intro p h
    apply layout_boundary tree p
    rw [← spans_layout]
    exact List.mem_flatMap.mpr ⟨s,hs,h⟩
  constructor
  · exact hp ⟨.referenceStart, s.start⟩ (by simp [spanPoints])
  constructor
  · exact hp ⟨.referenceEnd, s.stop⟩ (by simp [spanPoints])
  · intro p h
    exact hp ⟨.fallbackStart,p⟩ (by simp [spanPoints,h])

end VariableOrigin
