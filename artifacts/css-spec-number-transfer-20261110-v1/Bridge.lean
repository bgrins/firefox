import GeneratedEscape
import CssSemantics.CssEscape
import CssSemantics.CssInput

namespace CssDerivation

theorem hex_equivalent (c : Char) : isHex c = CssSemantics.CssEscape.hex c := rfl
theorem digit_equivalent (c : Char) : digitValue c = CssSemantics.CssEscape.digitValue c := rfl
theorem magnitude_equivalent (digits : List Char) : magnitude digits = CssSemantics.CssEscape.magnitude digits := rfl
theorem decode_equivalent (value : Nat) : decode value = CssSemantics.CssEscape.decode value := rfl

theorem whitespace_equivalent (c : Char) : isWhitespace c = CssSemantics.CssEscape.whitespace c := by
  change (c == '\n' || c == '\t' || c == ' ') = (c == ' ' || c == '\t' || c == '\n')
  simp [Bool.or_comm, Bool.or_left_comm, Bool.or_assoc]

theorem scan_equivalent (budget : Nat) (source : List Char) :
    scanPrefix isHex budget source = CssSemantics.CssEscape.scanHex budget source := by
  induction budget generalizing source with
  | zero => rfl
  | succ budget ih =>
      cases source with
      | nil => rfl
      | cons c rest => simp [scanPrefix, CssSemantics.CssEscape.scanHex, hex_equivalent, ih]

theorem terminator_equivalent (source : List Char) :
    (scanPrefix isWhitespace 1 source).2 = CssSemantics.CssEscape.skipWhitespace source := by
  cases source with
  | nil => rfl
  | cons c rest =>
      simp only [scanPrefix, whitespace_equivalent, CssSemantics.CssEscape.skipWhitespace]
      split <;> rfl

def toReference (result : Result) : CssSemantics.CssEscape.Result :=
  ⟨result.value, result.rest, result.error⟩

theorem escape_equivalent (source : List Char) :
    toReference (execute escape source) = CssSemantics.CssEscape.consume source := by
  cases source with
  | nil => rfl
  | cons c rest =>
      simp [execute, escape, run, toReference, CssSemantics.CssEscape.consume,
        hex_equivalent, scan_equivalent, terminator_equivalent, decode_equivalent, magnitude_equivalent]
      split <;> rfl

theorem escape_sound (source : List Char) :
    CssSemantics.CssEscape.Escaped source (toReference (execute escape source)) := by
  rw [escape_equivalent]
  exact CssSemantics.CssEscape.consume_sound source

theorem toReference_injective (a b : Result) (equal : toReference a = toReference b) : a = b := by
  cases a
  cases b
  cases equal
  rfl

theorem escape_spec (source : List Char) (result : Result) :
    execute escape source = result ↔ CssSemantics.CssEscape.Escaped source (toReference result) := by
  constructor
  · intro equal; rw [← equal]; exact escape_sound source
  · intro parsed
    apply toReference_injective
    exact (escape_equivalent source).trans parsed.result

theorem eof_exactly (source : List Char) :
    (execute escape source).error = true ↔ source = [] := by
  have equal := congrArg CssSemantics.CssEscape.Result.eofError (escape_equivalent source)
  change (execute escape source).error = (CssSemantics.CssEscape.consume source).eofError at equal
  rw [equal]
  exact CssSemantics.CssEscape.consume_eofError source

def CallerReady (source : List Char) : Prop :=
  CssSemantics.CssInput.Normalized source ∧ CssSemantics.CssEscape.ValidAfter source

theorem valid_call (source : List Char) (ready : CallerReady source) :
    CssSemantics.CssEscape.ValidEscaped source (toReference (execute escape source)) :=
  ⟨ready.2, escape_sound source⟩

theorem preprocessing_boundary (source : List Char)
    (valid : CssSemantics.CssEscape.ValidAfter (CssSemantics.CssInput.preprocess source)) :
    CallerReady (CssSemantics.CssInput.preprocess source) :=
  ⟨CssSemantics.CssInput.preprocess_normalized source, valid⟩

example : CallerReady [] := by simp [CallerReady, CssSemantics.CssInput.Normalized, CssSemantics.CssEscape.ValidAfter]
example : CallerReady ['0'] := by simp [CallerReady, CssSemantics.CssInput.Normalized, CssSemantics.CssEscape.ValidAfter]

#print axioms scan_equivalent
#print axioms escape_equivalent
#print axioms escape_spec
#print axioms eof_exactly
#print axioms valid_call
#print axioms preprocessing_boundary

end CssDerivation
