import NumericCapture
namespace NumericRepair
open NumericDigits

def LibraryAccepts {V : Type} (parse : List Byte → Option V) : Prop :=
  ∀ text, FromStrGrammar.RustFiniteNumber text → ∃ value, parse text = some value

def fallback (before xs : List Byte) (finite : Bool) : Bool :=
  decide (NumericCapture.endPosition before xs - before.length ≥ 256) || !finite

def candidate {V : Type} (before xs : List Byte) (original : V) (finite : Bool)
    (parse : List Byte → Option V) : Option (NumericToken.Result × V) :=
  if fallback before xs finite then
    (parse (NumericCapture.slice (before++xs) before.length (NumericCapture.endPosition before xs))).map
      (fun value => (NumericToken.native xs,value))
  else some (NumericToken.native xs,original)

theorem guard_length (before xs : List Byte) (finite : Bool) :
    fallback before xs finite = (decide ((NumericLexical.native xs).text.length ≥ 256) || !finite) := by
  simp [fallback,NumericCapture.subtraction]

theorem parse_admitted {V : Type} (before xs : List Byte) (parse : List Byte → Option V)
    (entry : NumericEntry.nativeStart xs = true) (library : LibraryAccepts parse) :
    ∃ value, parse (NumericCapture.slice (before++xs) before.length (NumericCapture.endPosition before xs)) = some value :=
  library _ (NumericCapture.captured_grammar before xs entry)

theorem normal_completion {V : Type} (before xs : List Byte) (original : V) (finite : Bool)
    (parse : List Byte → Option V) (entry : NumericEntry.nativeStart xs = true)
    (library : LibraryAccepts parse) :
    ∃ value, candidate before xs original finite parse = some (NumericToken.native xs,value) := by
  unfold candidate
  split
  · obtain ⟨value,hv⟩ := parse_admitted before xs parse entry library
    exact ⟨value,by simp [hv]⟩
  · exact ⟨original,rfl⟩

theorem projection {V : Type} (before xs : List Byte) (original value : V) (finite : Bool)
    (parse : List Byte → Option V) (token : NumericToken.Result)
    (h : candidate before xs original finite parse = some (token,value)) :
    token = NumericToken.native xs := by
  unfold candidate at h
  split at h
  · cases hp : parse (NumericCapture.slice (before++xs) before.length (NumericCapture.endPosition before xs)) with
    | none => simp [hp] at h
    | some v => simpa [hp] using (congrArg (Option.map Prod.fst) h).symm
  · exact (congrArg Prod.fst (Option.some.inj h)).symm

theorem reference_projection {V : Type} (before xs : List Byte) (original value : V) (finite : Bool)
    (parse : List Byte → Option V) (token : NumericToken.Result)
    (h : candidate before xs original finite parse = some (token,value)) :
    token = NumericToken.reference xs := by
  rw [projection before xs original value finite parse token h,NumericToken.native_reference]

theorem unchanged_suffix {V : Type} (before xs : List Byte) (original value : V) (finite : Bool)
    (parse : List Byte → Option V) (token : NumericToken.Result)
    (h : candidate before xs original finite parse = some (token,value)) :
    token.rest = xs.drop token.count := by
  rw [projection before xs original value finite parse token h]
  exact NumericToken.exact_suffix xs

theorem payload_can_change : candidate [] [49] (7:Nat) false (fun _ => some 42) =
    some (NumericToken.native [49],42) := by simp [candidate,fallback]

theorem rejected_library_not_normal : candidate [] [49] (7:Nat) false (fun _ => none) = none := by
  simp [candidate,fallback]

theorem short_finite_no_parse {V : Type} (before xs : List Byte) (original : V)
    (parse : List Byte → Option V) (short : (NumericLexical.native xs).text.length < 256) :
    candidate before xs original true parse = some (NumericToken.native xs,original) := by
  simp [candidate,guard_length,Nat.not_le.mpr short]

#print axioms guard_length
#print axioms parse_admitted
#print axioms normal_completion
#print axioms projection
#print axioms reference_projection
#print axioms unchanged_suffix
#print axioms payload_can_change
#print axioms rejected_library_not_normal
#print axioms short_finite_no_parse
end NumericRepair
