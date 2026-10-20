import UntilAfter
import ByteLexProgress
set_option autoImplicit false
namespace DelimiterProvider
open PublicCache

def PunctuationWidth (provider : ByteLex.Family → List Byte → Nat) : Prop :=
  ∀ byte tail, byte = 59 ∨ byte = 33 ∨ byte = 44 →
    provider .punctuation (byte :: tail) = 1

theorem selected_false (byte : Byte) (tail : List Byte)
    (h : UntilAfter.requested byte) : ByteLex.selected (byte :: tail) = false := by
  rcases h with rfl | rfl | rfl | rfl <;>
    simp [ByteLex.selected, IdentifierStart.nativeAscii] <;> decide +kernel

theorem relative_delimiter (provider : ByteLex.Family → List Byte → Nat)
    (width : PunctuationWidth provider) (byte : Byte) (tail : List Byte)
    (h : UntilAfter.requested byte) :
    ByteLex.native provider (byte :: tail) = ⟨UntilAfter.delimiterToken byte, 1⟩ := by
  rw [ByteLex.native, selected_false byte tail h]
  simp only [Bool.false_eq_true, ↓reduceIte]
  rcases h with rfl | rfl | rfl | rfl
  · simp [ByteLex.other, UntilAfter.delimiterToken]
  · simp [ByteLex.other, ByteLex.family, URLScan.nativeWhitespace, ByteLex.digit,
      UntilAfter.delimiterToken, show (59 : Byte).val = 59 from rfl, width 59 tail (Or.inl rfl)]
  · simp [ByteLex.other, ByteLex.family, URLScan.nativeWhitespace, ByteLex.digit,
      UntilAfter.delimiterToken, show (33 : Byte).val = 33 from rfl, width 33 tail (Or.inr (Or.inl rfl))]
  · simp [ByteLex.other, ByteLex.family, URLScan.nativeWhitespace, ByteLex.digit,
      UntilAfter.delimiterToken, show (44 : Byte).val = 44 from rfl, width 44 tail (Or.inr (Or.inr rfl))]

theorem drop_at (bytes : List Byte) (position : Nat) (byte : Byte)
    (atByte : bytes[position]? = some byte) :
    ∃ tail, bytes.drop position = byte :: tail := by
  induction position generalizing bytes with
  | zero =>
    cases bytes with
    | nil => simp at atByte
    | cons head tail =>
      simp only [List.getElem?_cons_zero, Option.some.injEq] at atByte
      subst head
      exact ⟨tail, rfl⟩
  | succ position ih =>
    cases bytes with
    | nil => simp at atByte
    | cons head tail => exact ih tail atByte

theorem delimiter_law (provider : ByteLex.Family → List Byte → Nat)
    (width : PunctuationWidth provider) (bytes : List Byte) :
    UntilAfter.DelimiterLaw bytes (ByteLex.read provider bytes) := by
  intro position byte atByte requested
  obtain ⟨tail, suffix⟩ := drop_at bytes position byte atByte
  simp only [ByteLex.read, suffix, relative_delimiter provider width byte tail requested]
  rcases requested with rfl | rfl | rfl | rfl <;>
    simp [UntilAfter.delimiterLexeme, UntilAfter.delimiterToken, ByteLex.pending]

theorem after_refines (provider : ByteLex.Family → List Byte → Nat)
    (width : PunctuationWidth provider) (positive : ByteLexProgress.ProviderProgress provider)
    (bytes : List Byte) (names : List (List Byte))
    (extra : List Byte) (stopOnError : Bool) (body : List Byte → WrapperControl.Program)
    (s : NestedControl.State) (r : NestedControl.Reference)
    (aligned : NestedControl.Aligned (ByteLex.read provider bytes) names s r)
    (mask : ∀ byte, extra.contains byte = true → UntilAfter.requested byte) :
    (UntilAfter.native bytes (ByteLex.read provider bytes) names extra stopOnError body s).1 =
      (UntilAfter.reference bytes (ByteLex.read provider bytes) extra stopOnError body r).1 ∧
    NestedControl.Aligned (ByteLex.read provider bytes) names
      (UntilAfter.native bytes (ByteLex.read provider bytes) names extra stopOnError body s).2
      (UntilAfter.reference bytes (ByteLex.read provider bytes) extra stopOnError body r).2 :=
  UntilAfter.after_refines bytes (ByteLex.read provider bytes) names extra stopOnError body s r
    aligned (ByteLexProgress.read_progress provider bytes positive) mask
    (delimiter_law provider width bytes)

end DelimiterProvider
