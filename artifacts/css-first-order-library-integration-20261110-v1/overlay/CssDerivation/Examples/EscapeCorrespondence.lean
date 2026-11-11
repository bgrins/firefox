import CssDerivation.Examples.EscapeTree
import CssDerivation.Examples.EscapeBackendCorrespondence

namespace CssDerivation.FirstOrder

theorem hex_meaning (c : Char) (env : Env Γ) :
    eval hexExpr (.cons c env) = CssDerivation.isHex c := rfl

theorem whitespace_meaning (c : Char) (env : Env Γ) :
    eval whitespaceExpr (.cons c env) = CssDerivation.isWhitespace c := rfl

theorem magnitude_meaning (digits : List Char) (env : Env Γ) :
    eval magnitudeExpr (.cons digits env) = CssDerivation.magnitude digits := by
  simp [magnitudeExpr, eval, lookup, CssDerivation.magnitude, CssDerivation.digitValue]

theorem decode_meaning (value : Nat) (env : Env Γ) :
    eval decodeExpr (.cons value env) = CssDerivation.decode value := by
  simp [decodeExpr, eval, lookup, CssDerivation.decode, or_assoc]

theorem scan_hex (env : Env Γ) (budget : Nat) (source : List Char) :
    scanData hexExpr env budget source = scanPrefix CssDerivation.isHex budget source := by
  rw [scan_lowering]
  rfl

theorem scan_whitespace (env : Env Γ) (budget : Nat) (source : List Char) :
    scanData whitespaceExpr env budget source = scanPrefix CssDerivation.isWhitespace budget source := by
  rw [scan_lowering]
  rfl

theorem escape_matches_prior (source : List Char) :
    execute escapeTree source = CssDerivation.execute CssDerivation.escape source := by
  cases source with
  | nil => rfl
  | cons c rest =>
      simp only [execute, escapeTree, interpret, CssDerivation.execute, CssDerivation.escape, run,
        hex_meaning, scan_hex, scan_whitespace, eval, lookup, magnitude_meaning, decode_meaning]

theorem lowered_escape_matches_prior (source : List Char) :
    CssDerivation.execute (lower escapeTree .nil) source = CssDerivation.execute CssDerivation.escape source :=
  (execute_lowering escapeTree source).trans (escape_matches_prior source)

theorem escape_relation (source : List Char) (result : Result) :
    execute escapeTree source = result ↔ CssSemantics.CssEscape.Escaped source (toReference result) := by
  rw [escape_matches_prior]
  exact CssDerivation.escape_spec source result

theorem ready_escape (source : List Char) (ready : CallerReady source) :
    CssSemantics.CssEscape.ValidEscaped source (toReference (execute escapeTree source)) := by
  rw [escape_matches_prior]
  exact CssDerivation.valid_call source ready

#print axioms escape_matches_prior
#print axioms lowered_escape_matches_prior
#print axioms escape_relation
#print axioms ready_escape

end CssDerivation.FirstOrder
