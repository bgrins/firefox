import Std

namespace VariableOrigin

def byteLength : List Char → Nat
  | [] => 0
  | c :: cs => c.utf8Size + byteLength cs

@[simp] theorem byteLength_nil : byteLength [] = 0 := rfl
@[simp] theorem byteLength_append (a b : List Char) :
    byteLength (a ++ b) = byteLength a + byteLength b := by
  induction a with
  | nil => simp [byteLength]
  | cons c cs ih => simp [byteLength, ih, Nat.add_assoc]

def Boundary (text : List Char) (offset : Nat) : Prop :=
  ∃ front back, text = front ++ back ∧ byteLength front = offset

theorem boundary_zero (text : List Char) : Boundary text 0 :=
  ⟨[], text, by simp, rfl⟩

theorem boundary_end (text : List Char) : Boundary text (byteLength text) :=
  ⟨text, [], by simp, rfl⟩

theorem boundary_le {text : List Char} {offset : Nat}
    (h : Boundary text offset) : offset ≤ byteLength text := by
  obtain ⟨a, b, rfl, rfl⟩ := h
  simp

theorem boundary_left {a : List Char} {offset : Nat} (b : List Char)
    (h : Boundary a offset) : Boundary (a ++ b) offset := by
  obtain ⟨p, s, rfl, rfl⟩ := h
  exact ⟨p, s ++ b, by simp [List.append_assoc], rfl⟩

theorem boundary_right (a : List Char) {b : List Char} {offset : Nat}
    (h : Boundary b offset) : Boundary (a ++ b) (byteLength a + offset) := by
  obtain ⟨p, s, rfl, rfl⟩ := h
  exact ⟨a ++ p, s, by simp [List.append_assoc], by simp⟩

inductive Component where
  | text (chars : List Char)
  | pair (left right : Component)
  | block (opening : List Char) (body : Component) (closing : List Char)
  | leafReference (chars : List Char)
  | reference (header : List Char) (fallback : Component) (closing : List Char)
  deriving Repr

def render : Component → List Char
  | .text s | .leafReference s => s
  | .pair a b => render a ++ render b
  | .block a b c | .reference a b c => a ++ render b ++ c

inductive PointKind where
  | referenceStart | referenceEnd | fallbackStart
  deriving DecidableEq, Repr

structure Point where
  kind : PointKind
  offset : Nat
  deriving DecidableEq, Repr

def shift (delta : Nat) (p : Point) : Point := { p with offset := delta + p.offset }

def translated (delta : Nat) (points : List Point) : List Point := points.map (shift delta)

@[simp] theorem translated_zero (points : List Point) : translated 0 points = points := by
  induction points with
  | nil => rfl
  | cons p ps ih =>
      cases p
      simp_all [translated, shift]

@[simp] theorem translated_append (delta : Nat) (a b : List Point) :
    translated delta (a ++ b) = translated delta a ++ translated delta b := by
  simp [translated]

theorem translated_compose (a b : Nat) (points : List Point) :
    translated a (translated b points) = translated (a + b) points := by
  simp [translated, List.map_map, Function.comp_def, shift, Nat.add_assoc]

def layout : Component → List Point
  | .text _ => []
  | .leafReference s => [{ kind := .referenceStart, offset := 0 }, { kind := .referenceEnd, offset := byteLength s }]
  | .pair a b => layout a ++ translated (byteLength (render a)) (layout b)
  | .block a b _ => translated (byteLength a) (layout b)
  | .reference a b c =>
      [{ kind := .referenceStart, offset := 0 },
       { kind := .referenceEnd, offset := byteLength (a ++ render b ++ c) },
       { kind := .fallbackStart, offset := byteLength a }] ++
      translated (byteLength a) (layout b)

def collect (origin cursor : Nat) : Component → List Point
  | .text _ => []
  | .leafReference s => [{ kind := .referenceStart, offset := cursor - origin }, { kind := .referenceEnd, offset := cursor + byteLength s - origin }]
  | .pair a b => collect origin cursor a ++ collect origin (cursor + byteLength (render a)) b
  | .block a b _ => collect origin (cursor + byteLength a) b
  | .reference a b c =>
      [{ kind := .referenceStart, offset := cursor - origin },
       { kind := .referenceEnd, offset := cursor + byteLength (a ++ render b ++ c) - origin },
       { kind := .fallbackStart, offset := cursor + byteLength a - origin }] ++
      collect origin (cursor + byteLength a) b

theorem collector_layout (tree : Component) (origin cursor : Nat) (h : origin ≤ cursor) :
    collect origin cursor tree = translated (cursor - origin) (layout tree) := by
  induction tree generalizing cursor with
  | text s => rfl
  | leafReference s =>
      simp [collect, layout, translated, shift]
      omega
  | pair a b ia ib =>
      simp only [collect, layout, translated_append]
      rw [ia cursor h, ib (cursor + byteLength (render a)) (by omega), translated_compose]
      congr 1
      congr 1
      omega
  | block a b c ih =>
      simp only [collect, layout]
      rw [ih (cursor + byteLength a) (by omega), translated_compose]
      congr 1
      omega
  | reference a b c ih =>
      have ha : cursor + byteLength a - origin = cursor - origin + byteLength a := by omega
      simp only [collect, layout, translated_append]
      rw [ih (cursor + byteLength a) (by omega), translated_compose, ha]
      simp [translated, shift]
      omega


theorem translated_mem {delta : Nat} {p : Point} {ps : List Point}
    (h : p ∈ translated delta ps) : ∃ q ∈ ps, p = shift delta q := by
  obtain ⟨q, hq, heq⟩ := List.mem_map.mp h
  exact ⟨q, hq, heq.symm⟩

theorem layout_boundary (tree : Component) :
    ∀ p ∈ layout tree, Boundary (render tree) p.offset := by
  induction tree with
  | text chars => simp [layout]
  | leafReference chars =>
      intro p hp
      simp only [layout, List.mem_cons, List.not_mem_nil, or_false] at hp
      rcases hp with rfl | rfl
      · exact boundary_zero chars
      · exact boundary_end chars
  | pair a b ia ib =>
      intro p hp
      simp only [layout, List.mem_append] at hp
      rcases hp with hp | hp
      · exact boundary_left (render b) (ia p hp)
      · obtain ⟨q, hq, rfl⟩ := translated_mem hp
        exact boundary_right (render a) (ib q hq)
  | block a b c ih =>
      intro p hp
      obtain ⟨q, hq, rfl⟩ := translated_mem hp
      exact boundary_left c (boundary_right a (ih q hq))
  | reference a b c ih =>
      intro p hp
      simp only [layout, List.mem_append, List.mem_cons, List.not_mem_nil, or_false] at hp
      rcases hp with (rfl | rfl | rfl) | hp
      · exact boundary_zero _
      · exact boundary_end _
      · exact boundary_left c (boundary_left (render b) (boundary_end a))
      · obtain ⟨q, hq, rfl⟩ := translated_mem hp
        exact boundary_left c (boundary_right a (ih q hq))

theorem collected_common_origin (tree : Component) (origin : Nat) :
    collect origin origin tree = layout tree := by
  simpa using collector_layout tree origin origin (Nat.le_refl _)

theorem collected_safe (tree : Component) (origin : Nat) (p : Point)
    (h : p ∈ collect origin origin tree) :
    Boundary (render tree) p.offset ∧ p.offset ≤ byteLength (render tree) := by
  rw [collected_common_origin] at h
  have hb := layout_boundary tree p h
  exact ⟨hb, boundary_le hb⟩

end VariableOrigin
