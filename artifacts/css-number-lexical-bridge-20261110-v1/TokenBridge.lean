import DocumentBridge
import NumericToken

namespace CssNumberLexicalBridge
open NumericDigits CssDerivation.NumberTransfer CssDerivation.ParserJson

theorem token_numeric_component (source : List Byte) :
    (NumericToken.native source).numeric = NumericLexical.native source := by
  unfold NumericToken.native
  dsimp only
  split
  · rfl
  · split <;> rfl

theorem fixed_document_token_component (source : List Byte) (oldError : Bool) :
    observeDocument numberFixture ⟨scalars source, oldError⟩ =
      some (observeNative (NumericToken.reference source).numeric) := by
  rw [← NumericToken.native_reference, token_numeric_component, fixed_document_observation]

theorem admitted_full_token (source : List Byte) (oldError : Bool) (domain : admitted source) :
    observeDocument numberFixture ⟨scalars source, oldError⟩ =
      some (observeNative (NumericToken.reference source).numeric) ∧
    0 < (NumericToken.native source).count ∧
    (NumericToken.native source).rest = source.drop (NumericToken.native source).count ∧
    (NumericToken.native source).count ≤ source.length := by
  exact ⟨fixed_document_token_component source oldError, NumericToken.positive source domain.2,
    NumericToken.exact_suffix source, NumericToken.count_bound source⟩

end CssNumberLexicalBridge
