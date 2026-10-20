import Origin

namespace VariableOrigin

def cssWhitespace (c : Char) : Bool :=
  c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\x0c'

def stripLeading (text : List Char) := text.dropWhile cssWhitespace

theorem whitespace_partition (text : List Char) :
    text.takeWhile cssWhitespace ++ stripLeading text = text :=
  List.takeWhile_append_dropWhile

theorem strip_padding (padding text : List Char)
    (hp : ∀ c ∈ padding, cssWhitespace c = true) :
    stripLeading (padding ++ text) = stripLeading text := by
  induction padding with
  | nil => rfl
  | cons c cs ih =>
      have hc := hp c (by simp)
      have ht : ∀ x ∈ cs, cssWhitespace x = true := by
        intro x hx
        exact hp x (by simp [hx])
      simpa [stripLeading, List.dropWhile_cons, hc] using ih ht

def normalizedConstructor (base : Nat) (padding : List Char) (tree : Component) :=
  (render tree, collect (base + byteLength padding) (base + byteLength padding) tree)

def oldConstructor (base : Nat) (padding : List Char) (tree : Component) :=
  (render tree, collect base (base + byteLength padding) tree)

theorem normalized_matches_reference (base : Nat) (padding : List Char) (tree : Component) :
    normalizedConstructor base padding tree = (render tree, layout tree) := by
  simp [normalizedConstructor, collected_common_origin]

theorem normalized_text (base : Nat) (padding : List Char) (tree : Component)
    (hp : ∀ c ∈ padding, cssWhitespace c = true)
    (ht : stripLeading (render tree) = render tree) :
    (normalizedConstructor base padding tree).1 = stripLeading (padding ++ render tree) := by
  rw [strip_padding padding (render tree) hp, ht]
  rfl

theorem normalized_points_safe (base : Nat) (padding : List Char) (tree : Component)
    (point : Point) (h : point ∈ (normalizedConstructor base padding tree).2) :
    Boundary (normalizedConstructor base padding tree).1 point.offset ∧
    point.offset ≤ byteLength (normalizedConstructor base padding tree).1 := by
  exact collected_safe tree _ point h

theorem old_extra_shift (base : Nat) (padding : List Char) (tree : Component) :
    (oldConstructor base padding tree).2 = translated (byteLength padding) (layout tree) := by
  unfold oldConstructor
  simp only
  rw [collector_layout tree base (base + byteLength padding) (by omega)]
  congr 1
  omega

def witness : Component := .leafReference "var(--v)".toList

theorem old_out_of_bounds :
    ∃ p ∈ (oldConstructor 0 [' '] witness).2,
      byteLength (oldConstructor 0 [' '] witness).1 < p.offset := by
  exact ⟨⟨.referenceEnd, 9⟩, by decide, by decide⟩

theorem candidate_witness :
    (normalizedConstructor 0 [' '] witness).2 =
      [⟨.referenceStart, 0⟩, ⟨.referenceEnd, 8⟩] := by decide

theorem vertical_tab_retained : stripLeading ['\x0b', 'a'] = ['\x0b', 'a'] := by decide

theorem nbsp_retained : stripLeading ['\u00a0', 'a'] = ['\u00a0', 'a'] := by decide

theorem comment_prefix_retained : stripLeading " /**/x".toList = "/**/x".toList := by decide

end VariableOrigin
