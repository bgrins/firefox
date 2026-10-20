import DelimiterProvider
import AfterDriver
set_option autoImplicit false
namespace ProviderReview
open PublicCache

theorem driver_width : DelimiterProvider.PunctuationWidth provider := by
  intro byte tail selected
  rcases selected with rfl | rfl | rfl <;> simp [provider]

theorem driver_law (bytes : List Byte) :
    UntilAfter.DelimiterLaw bytes (ByteLex.read provider bytes) :=
  DelimiterProvider.delimiter_law provider driver_width bytes

theorem driver_zero : provider .whitespace [59] = 0 := by decide +kernel

theorem driver_not_global_progress : ¬ ByteLexProgress.ProviderProgress provider := by
  intro h
  have positive := h .whitespace [59] (by simp)
  rw [driver_zero] at positive
  exact Nat.not_lt_zero _ positive

def unitProvider (_ : ByteLex.Family) (xs : List Byte) : Nat :=
  if xs = [] then 0 else 1

theorem unit_width : DelimiterProvider.PunctuationWidth unitProvider := by
  intro byte tail _
  simp [unitProvider]

theorem unit_progress : ByteLexProgress.ProviderProgress unitProvider := by
  intro family xs nonempty
  simp [unitProvider, nonempty]

theorem unit_bound : ByteLexProgress.ProviderBound unitProvider := by
  intro family xs
  cases xs <;> simp [unitProvider]

theorem simultaneous_inhabited : ∃ p,
    DelimiterProvider.PunctuationWidth p ∧
    ByteLexProgress.ProviderProgress p ∧ ByteLexProgress.ProviderBound p :=
  ⟨unitProvider, unit_width, unit_progress, unit_bound⟩

def doubleProvider (_ : ByteLex.Family) (_ : List Byte) : Nat := 2

theorem wrong_width : ¬ DelimiterProvider.PunctuationWidth doubleProvider := by
  intro h
  have bad := h 59 [] (Or.inl rfl)
  simp [doubleProvider] at bad

theorem wrong_read :
    ByteLex.read doubleProvider [59] 0 ≠ UntilAfter.delimiterLexeme 59 0 := by
  decide +kernel

theorem wrong_law : ¬ UntilAfter.DelimiterLaw [59] (ByteLex.read doubleProvider [59]) := by
  intro h
  exact wrong_read (h 0 59 (by decide +kernel) (Or.inr (Or.inl rfl)))

theorem curly_provider_independent (p : ByteLex.Family → List Byte → Nat)
    (tail : List Byte) : ByteLex.native p (123 :: tail) = ⟨.open .curly, 1⟩ := by
  rw [ByteLex.native, DelimiterProvider.selected_false 123 tail (Or.inl rfl)]
  simp [ByteLex.other]

end ProviderReview
