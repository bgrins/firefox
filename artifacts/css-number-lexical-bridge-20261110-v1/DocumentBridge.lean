import CssDerivation.Examples.NumberDocument
import LexicalBridge
import EntryBridge

namespace CssNumberLexicalBridge
open NumericDigits CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer CssDerivation.ParserJson
open CssSemantics CssNumberSyntax

theorem fixed_document_observation (source : List Byte) (oldError : Bool) :
    observeDocument numberFixture ⟨scalars source, oldError⟩ =
      some (observeNative (NumericLexical.native source)) := by
  simp only [observeDocument, executeDocument, number_fixture_decoded, Option.map_some]
  rw [CssParserLowering.number_parts]
  change some (observeParts (scalars source) (rawParts (consume (scalars source)).decimal)
    (consume (scalars source)).rest) = _
  rw [raw_parts_observation, lexical_observation]

theorem fixed_document_reference (source : List Byte) (oldError : Bool) :
    observeDocument numberFixture ⟨scalars source, oldError⟩ =
      some (observeNative (NumericLexical.reference source)) := by
  rw [fixed_document_observation, NumericLexical.native_reference]

theorem scalar_suffix (source : List Byte) :
    (consume (scalars source)).rest = scalars (NumericLexical.native source).rest := by
  rw [consume_bridge]
  rfl

theorem fixed_document_suffix_and_error (source : List Byte) (oldError : Bool) :
    (executeDocument NumberShape numberFixture ⟨scalars source, oldError⟩).map
      (fun result => (result.2.input, result.2.error)) =
      some (scalars (NumericLexical.native source).rest, oldError) := by
  simp only [executeDocument, number_fixture_decoded, Option.map_some]
  rw [CssParserLowering.number_parts]
  simp only [scalar_suffix]

theorem admitted_bridge (source : List Byte) (oldError : Bool) (domain : admitted source) :
    NormalizedASCII source ∧ CssSemantics.CssNumberParts.StartsNumber (scalars source) ∧
    observeDocument numberFixture ⟨scalars source, oldError⟩ =
      some (observeNative (NumericLexical.reference source)) ∧
    0 < (NumericLexical.native source).text.length ∧
    (NumericLexical.native source).text ++ (NumericLexical.native source).rest = source := by
  exact ⟨domain.1, (caller_domain source).mpr domain.2, fixed_document_reference source oldError,
    NumericLexical.positive source domain.2, NumericLexical.cover source⟩

end CssNumberLexicalBridge
