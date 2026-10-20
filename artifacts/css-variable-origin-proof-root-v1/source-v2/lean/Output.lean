import Origin

namespace VariableOrigin

structure Range where
  start : Nat
  stop : Nat
  deriving DecidableEq, Repr

structure Piece where
  text : List Char
  tainted : Bool
  separator : Bool
  deriving Repr

structure Output where
  text : List Char
  ranges : List Range
  aggregate : Bool
  deriving Repr

def separatorText (p : Piece) : List Char := if p.separator then "/**/".toList else []
def emitted (p : Piece) : List Char := if p.text.isEmpty then [] else separatorText p ++ p.text

def localRanges (base : Nat) (p : Piece) : List Range :=
  if p.text.isEmpty || !p.tainted then [] else
    [⟨base + byteLength (separatorText p), base + byteLength (separatorText p ++ p.text)⟩]

def appendPiece (s : Output) (p : Piece) : Output :=
  if p.text.isEmpty then { s with aggregate := s.aggregate || p.tainted } else
    let separated := s.text ++ separatorText p
    let text := separated ++ p.text
    let ranges := if p.tainted then s.ranges ++ [⟨byteLength separated, byteLength text⟩] else s.ranges
    ⟨text, ranges, s.aggregate || p.tainted⟩

def referenceText (pieces : List Piece) := pieces.flatMap emitted

def referenceRanges (base : Nat) : List Piece → List Range
  | [] => []
  | p :: ps => localRanges base p ++ referenceRanges (base + byteLength (emitted p)) ps

def anyTaint (pieces : List Piece) := pieces.any (·.tainted)

theorem append_projection (s : Output) (p : Piece) :
    (appendPiece s p).text = s.text ++ emitted p ∧
    (appendPiece s p).ranges = s.ranges ++ localRanges (byteLength s.text) p ∧
    (appendPiece s p).aggregate = (s.aggregate || p.tainted) := by
  cases he : p.text.isEmpty <;> cases ht : p.tainted <;>
    simp [appendPiece, emitted, localRanges, he, ht, List.append_assoc]

theorem output_history_refinement (pieces : List Piece) (s : Output) :
    (pieces.foldl appendPiece s).text = s.text ++ referenceText pieces ∧
    (pieces.foldl appendPiece s).ranges = s.ranges ++ referenceRanges (byteLength s.text) pieces ∧
    (pieces.foldl appendPiece s).aggregate = (s.aggregate || anyTaint pieces) := by
  induction pieces generalizing s with
  | nil => simp [referenceText, referenceRanges, anyTaint]
  | cons p ps ih =>
      obtain ⟨ht,hr,ha⟩ := append_projection s p
      obtain ⟨iht,ihr,iha⟩ := ih (appendPiece s p)
      simp only [List.foldl_cons]
      constructor
      · simpa [ht, referenceText, List.flatMap_cons, List.append_assoc] using iht
      constructor
      · simpa [ht, hr, referenceRanges, List.append_assoc] using ihr
      · simpa [ha, anyTaint, Bool.or_assoc] using iha

def RangeSafe (text : List Char) (r : Range) : Prop :=
  r.start ≤ r.stop ∧ Boundary text r.start ∧ Boundary text r.stop

def OutputSafe (s : Output) := ∀ r ∈ s.ranges, RangeSafe s.text r

theorem range_extend {text : List Char} (suffix : List Char) {r : Range}
    (h : RangeSafe text r) : RangeSafe (text ++ suffix) r :=
  ⟨h.1, boundary_left suffix h.2.1, boundary_left suffix h.2.2⟩

theorem append_safe (s : Output) (p : Piece) (h : OutputSafe s) : OutputSafe (appendPiece s p) := by
  intro r hr
  cases he : p.text.isEmpty with
  | true => simpa [appendPiece, he, RangeSafe] using h r (by simpa [appendPiece, he] using hr)
  | false =>
      cases ht : p.tainted with
      | false =>
          have old : r ∈ s.ranges := by simpa [appendPiece, he, ht] using hr
          simpa [appendPiece, he, ht] using range_extend p.text (range_extend (separatorText p) (h r old))
      | true =>
          have hm : r ∈ s.ranges ∨ r = ⟨byteLength (s.text ++ separatorText p),
              byteLength ((s.text ++ separatorText p) ++ p.text)⟩ := by
            simpa [appendPiece, he, ht] using hr
          rcases hm with old | rfl
          · simpa [appendPiece, he, ht] using range_extend p.text (range_extend (separatorText p) (h r old))
          · simp only [appendPiece, he, ht, Bool.false_eq_true, ↓reduceIte]
            exact ⟨by simp, boundary_left p.text (boundary_end _), boundary_end _⟩

theorem output_history_safe (pieces : List Piece) (s : Output) (h : OutputSafe s) :
    OutputSafe (pieces.foldl appendPiece s) := by
  induction pieces generalizing s with
  | nil => exact h
  | cons p ps ih => exact ih (appendPiece s p) (append_safe s p h)

theorem fresh_tainted_range (s : Output) (p : Piece)
    (nonempty : p.text.isEmpty = false) (tainted : p.tainted = true) :
    ⟨byteLength (s.text ++ separatorText p), byteLength ((s.text ++ separatorText p) ++ p.text)⟩
      ∈ (appendPiece s p).ranges := by
  simp [appendPiece, nonempty, tainted]

theorem empty_keeps_provenance (s : Output) (p : Piece)
    (empty : p.text.isEmpty = true) (tainted : p.tainted = true) :
    (appendPiece s p).text = s.text ∧ (appendPiece s p).ranges = s.ranges ∧
    (appendPiece s p).aggregate = true := by
  simp [appendPiece, empty, tainted]

theorem nonempty_tainted_covered_after_suffix (s : Output) (p : Piece) (suffix : List Piece)
    (nonempty : p.text.isEmpty = false) (tainted : p.tainted = true) :
    ⟨byteLength (s.text ++ separatorText p), byteLength ((s.text ++ separatorText p) ++ p.text)⟩
      ∈ (suffix.foldl appendPiece (appendPiece s p)).ranges := by
  have now := fresh_tainted_range s p nonempty tainted
  rw [(output_history_refinement suffix (appendPiece s p)).2.1]
  exact List.mem_append_left _ now


def checkedAppend (limit : Nat) (s : Output) (p : Piece) : Except Unit Output :=
  if byteLength s.text + byteLength p.text > limit then .error () else .ok (appendPiece s p)

theorem checked_success_safe (limit : Nat) (s : Output) (p : Piece) (result : Output)
    (h : OutputSafe s) (ok : checkedAppend limit s p = .ok result) : OutputSafe result := by
  unfold checkedAppend at ok
  split at ok
  · contradiction
  · cases ok
    exact append_safe s p h

end VariableOrigin
