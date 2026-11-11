import TokenBridge
import RuntimeSupport

set_option cbv.warning false
set_option maxRecDepth 20000
set_option maxHeartbeats 8000000

namespace CssNumberLexicalBridge.Cases
open CssDerivation.NumberTransfer CssDerivation.ParserJson

def fixed (bytes : List NumericDigits.Byte) (oldError : Bool := false) :=
  observeDocument numberFixture ⟨scalars bytes, oldError⟩

theorem plus_presence : (fixed [43, 48, 120]).map Observation.hasSign = some true := by cbv <;> decide

theorem minus_presence : (fixed [45, 48]).map Observation.hasSign = some true := by cbv <;> decide

theorem unsigned_presence : (fixed [48]).map Observation.hasSign = some false := by cbv <;> decide

theorem exponent_not_integer : (fixed [49, 101, 48]).map Observation.isInteger = some false := by cbv <;> decide

theorem fraction_not_integer : (fixed [49, 46, 48]).map Observation.isInteger = some false := by cbv <;> decide

theorem invalid_exponent_is_integer : (fixed [49, 101, 43]).map Observation.isInteger = some true := by cbv <;> decide

theorem no_prefix_overrun : (fixed [49, 120]).map Observation.consumed = some [49] := by cbv <;> decide

theorem fraction_rollback : (fixed [49, 46, 120]).map Observation.rest = some [46, 120] := by cbv <;> decide

theorem exponent_rollback : (fixed [49, 101, 43]).map Observation.rest = some [101, 43] := by cbv <;> decide

theorem exponent_sign_rollback : (fixed [49, 101, 45, 120]).map Observation.rest = some [101, 45, 120] := by cbv <;> decide

theorem leading_fraction : (fixed [45, 46, 53]).map Observation.integerDigits = some [] := by cbv <;> decide

theorem all_digit_runs : (fixed [43, 48, 49, 46, 50, 48, 69, 45, 48, 51, 120]).map
    (fun r => (r.integerDigits, r.fractionDigits, r.exponentDigits)) =
    some ([48, 49], [50, 48], [48, 51]) := by cbv <;> decide

theorem numeric_core_not_full_token :
    (fixed [49, 101, 43]).map Observation.rest = some [101, 43] ∧
    (NumericToken.native [49, 101, 43]).kind = .dimension ∧
    (NumericToken.native [49, 101, 43]).unit = [101] ∧
    (NumericToken.native [49, 101, 43]).rest = [43] := by cbv <;> decide

theorem percentage_suffix :
    (fixed [49, 37, 120]).map Observation.rest = some [37, 120] ∧
    (NumericToken.native [49, 37, 120]).kind = .percentage ∧
    (NumericToken.native [49, 37, 120]).rest = [120] := by cbv <;> decide

theorem true_model_error_preserved :
    (executeDocument NumberShape numberFixture ⟨['1', 'e', '+'], true⟩).map
      (fun result => result.2.error) = some true := by cbv <;> decide

theorem invalid_entry_refused : admittedBytes "+" = none := by cbv <;> decide

theorem empty_refused : admittedBytes "" = none := by cbv <;> decide

theorem bare_dot_refused : admittedBytes "." = none := by cbv <;> decide

theorem nul_refused : admittedBytes (String.ofList ['1', Char.ofNat 0]) = none := by cbv <;> decide

theorem cr_refused : admittedBytes (String.ofList ['1', Char.ofNat 13]) = none := by cbv <;> decide

theorem ff_refused : admittedBytes (String.ofList ['1', Char.ofNat 12]) = none := by cbv <;> decide

theorem non_ascii_refused : admittedBytes "1é" = none := by cbv <;> decide

end CssNumberLexicalBridge.Cases
