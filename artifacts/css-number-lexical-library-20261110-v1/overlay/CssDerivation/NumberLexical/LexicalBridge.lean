import CssDerivation.Examples.NumberCorrespondence
import CssDerivation.NumberLexical.Observation
import CssDerivation.NumberLexical.PartsBridge

namespace CssNumberLexicalBridge
open NumericDigits CssSemantics CssNumberParts CssNumberSyntax
open CssDerivation CssDerivation.NumberTransfer CssDerivation.ParserJson

def fromByteParts (source : List Byte) : CssNumberSyntax.Result :=
  let integer := NumericDigits.scan (NumericEntry.stripSign source)
  let fraction := NumericParts.fraction integer.rest
  let exponent := NumericParts.exponent fraction.rest
  ⟨⟨outerSign source, scalars integer.digits,
    if fraction.used then some (scalars fraction.digits) else none,
    if exponent.used then some (outerSign (fraction.rest.drop 1), scalars exponent.digits) else none⟩,
    scalars exponent.rest⟩

theorem consume_bridge (source : List Byte) : consume (scalars source) = fromByteParts source := by
  simp only [consume, sign_bridge, scan_bridge, fraction_bridge, exponent_bridge, fromByteParts]

def observeSyntax (source : List Char) (result : CssNumberSyntax.Result) : Observation :=
  ⟨codes (source.take (source.length - result.rest.length)), codes result.rest,
    codes result.decimal.integer, codes (result.decimal.fraction.getD []),
    codes ((result.decimal.exponent.map Prod.snd).getD []),
    result.decimal.sign.isSome, result.decimal.fraction.isNone && result.decimal.exponent.isNone⟩

theorem raw_parts_observation (source : List Char) (result : CssNumberSyntax.Result) :
    observeParts source (rawParts result.decimal) result.rest = observeSyntax source result := by
  rcases result with ⟨⟨sign, integer, fraction, exponent⟩, rest⟩
  cases sign <;> cases fraction <;> cases exponent <;>
    simp [observeParts, observeSyntax, rawParts, signChars, exponentChars]

theorem prefix_from_suffix (source : List Byte) :
    source.take (source.length - (NumericLexical.native source).rest.length) =
      (NumericLexical.native source).text := by
  have cover := NumericLexical.cover source
  have lengths := congrArg List.length cover
  have count : source.length - (NumericLexical.native source).rest.length =
      (NumericLexical.native source).text.length := by simp only [List.length_append] at lengths; omega
  rw [count]
  calc
    _ = ((NumericLexical.native source).text ++ (NumericLexical.native source).rest).take
        (NumericLexical.native source).text.length := congrArg (List.take _) cover.symm
    _ = _ := by simp

theorem codes_scalars_take (source : List Byte) (n : Nat) :
    codes ((scalars source).take n) = (source.take n).map Fin.val := by
  simp [codes, scalars, List.map_take, List.map_map, Function.comp_def, scalar_nat]

theorem lexical_observation (source : List Byte) :
    observeSyntax (scalars source) (consume (scalars source)) = observeNative (NumericLexical.native source) := by
  rw [consume_bridge]
  simp only [fromByteParts, observeSyntax, observeNative, NumericLexical.native,
    fraction_selected_digits, exponent_selected_digits, optional_isNone, scalars_length,
    codes_scalars_take, scalars_codes, outer_sign_presence]
  have prefix_eq := prefix_from_suffix source
  simp only [NumericLexical.native] at prefix_eq
  rw [prefix_eq]

end CssNumberLexicalBridge
