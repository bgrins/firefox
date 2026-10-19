import FromStrGrammar
namespace NumericCapture
open NumericDigits

def endPosition (before xs : List Byte) : Nat := before.length + (NumericLexical.native xs).text.length

def slice (whole : List Byte) (start finish : Nat) : List Byte := (whole.drop start).take (finish-start)

theorem forward (before xs : List Byte) : before.length ≤ endPosition before xs := by
  simp [endPosition]

theorem subtraction (before xs : List Byte) :
    endPosition before xs - before.length = (NumericLexical.native xs).text.length := by
  simp [endPosition]

theorem bounded (before xs : List Byte) : endPosition before xs ≤ (before++xs).length := by
  have h := NumericLexical.count_bound xs
  simp [endPosition]
  omega

theorem native_bounds (before xs : List Byte) (maximum : Nat)
    (h : (before++xs).length ≤ maximum) :
    before.length ≤ endPosition before xs ∧ endPosition before xs ≤ maximum ∧
      endPosition before xs - before.length ≤ maximum := by
  have hf := forward before xs
  have hb := bounded before xs
  omega

theorem captured_prefix (before xs : List Byte) :
    slice (before++xs) before.length (endPosition before xs) = (NumericLexical.native xs).text := by
  simp only [slice,subtraction,List.drop_left]
  have hc := NumericLexical.cover xs
  calc xs.take (NumericLexical.native xs).text.length =
      ((NumericLexical.native xs).text ++ (NumericLexical.native xs).rest).take (NumericLexical.native xs).text.length := congrArg (fun ys => ys.take (NumericLexical.native xs).text.length) hc.symm
    _ = _ := by simp

theorem captured_ascii (before xs : List Byte) :
    ∀ b ∈ slice (before++xs) before.length (endPosition before xs), b.val < 128 := by
  rw [captured_prefix]
  exact NumericLexical.consumed_ascii xs

theorem captured_grammar (before xs : List Byte) (h : NumericEntry.nativeStart xs = true) :
    FromStrGrammar.RustFiniteNumber (slice (before++xs) before.length (endPosition before xs)) := by
  rw [captured_prefix]
  exact FromStrGrammar.rust_grammar xs h

theorem captured_end_boundary (before xs : List Byte) (units : List Boundary.Unit)
    (h : Boundary.bytes units = xs) : Boundary.marker (before++xs) (endPosition before xs) :=
  NumericBoundary.lift_marker before xs _ (NumericBoundary.lexical_boundary units xs h)

theorem captured_start_boundary (before xs : List Byte) (units : List Boundary.Unit)
    (h : Boundary.bytes units = xs) : Boundary.marker (before++xs) before.length := by
  have hm := NumericBoundary.zero_marker units
  rw [h] at hm
  have ht := NumericBoundary.lift_marker before xs 0 hm
  simpa using ht

#print axioms captured_start_boundary

#print axioms forward
#print axioms subtraction
#print axioms bounded
#print axioms native_bounds
#print axioms captured_prefix
#print axioms captured_ascii
#print axioms captured_grammar
#print axioms captured_end_boundary
end NumericCapture
