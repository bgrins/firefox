import Proof
import Controls

namespace CssNativeHighBit
namespace CheckedControls

theorem copy_member : belongs 3 (.high firstHighOne) copyWitness := by
  constructor
  · decide
  · intro i hi
    have hv : i.val = 0 := by change i.val < 1 at hi; omega
    have he : i = 0 := Fin.ext hv
    subst i
    decide

theorem other_member : belongs 3 (.high firstHighOne) otherScalarWitness := by
  constructor
  · decide
  · intro i hi
    have hv : i.val = 0 := by change i.val < 1 at hi; omega
    have he : i = 0 := Fin.ext hv
    subst i
    decide

theorem omitted_high_class :
    belongs 3 (.high firstHighOne) copyWitness ∧
      (∀ cell, admissible 3 cell → cell ≠ .high firstHighOne →
        ∀ raw, generate 3 cell raw ≠ copyWitness) := by
  refine ⟨copy_member, ?_⟩
  intro cell hc hne raw he
  have hm := image_membership 3 cell raw (by decide) hc
  rw [he] at hm
  exact hne (class_unique 3 copyWitness cell (.high firstHighOne)
    hc hm (by decide) copy_member)

theorem fixed_remaining_high_bytes :
    belongs 3 (.high firstHighOne) otherScalarWitness ∧
      (∀ raw, fixedScalar raw ≠ otherScalarWitness) := by
  refine ⟨other_member, ?_⟩
  intro raw he
  have h := congrFun he (1 : Fin 5)
  change (197 : UInt8) = 194 at h
  exact (by decide : (197 : UInt8) ≠ 194) h

theorem zeroed_unused_tail :
    belongs 3 (.high firstHighOne) copyWitness ∧
      (∀ raw, zeroUnused 3 (firstHigh firstHighOne raw) ≠ copyWitness) := by
  refine ⟨copy_member, ?_⟩
  intro raw he
  have h := congrFun he (3 : Fin 5)
  change (0 : UInt8) = 255 at h
  exact (by decide : (0 : UInt8) ≠ 255) h

theorem complement_member : isAscii 2 asciiComplementWitness := by
  intro i hi
  have hv : i.val = 0 ∨ i.val = 1 := by omega
  rcases hv with hv | hv
  · have he : i = 0 := Fin.ext hv
    subst i
    decide
  · have he : i = 1 := Fin.ext hv
    subst i
    decide

theorem omitted_ascii_complement :
    isAscii 2 asciiComplementWitness ∧
      (∀ a : Fin 128, a.val ≠ 0 → ∀ raw,
        asciiChild 2 a raw ≠ asciiComplementWitness) := by
  refine ⟨complement_member, ?_⟩
  intro a hn raw he
  have h := congrArg UInt8.toNat (congrFun he (0 : Fin 5))
  change (UInt8.ofNat a.val).toNat = 0 at h
  rw [UInt8.toNat_ofNat_of_lt' (by have := a.isLt; omega)] at h
  exact hn h

theorem restricted_mode_page :
    ¬ restrictedContext dependentContext ∧ ¬ restrictedContext pageContext ∧
      (¬ (∀ c : NativeContext, restrictedContext c)) := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  exact (by decide : ¬ restrictedContext dependentContext) (h dependentContext)

theorem empty_context :
    (∀ _b : Backing, ∀ _c : Empty, False) ∧
      (¬ (∃ _b : Backing, ∃ _c : Empty, True)) := by
  constructor
  · intro _ c
    exact nomatch c
  · rintro ⟨_, c, _⟩
    exact nomatch c

theorem controls : Controls where
  omitted_high_class := omitted_high_class
  fixed_remaining_high_bytes := fixed_remaining_high_bytes
  zeroed_unused_tail := zeroed_unused_tail
  omitted_ascii_complement := omitted_ascii_complement
  restricted_mode_page := restricted_mode_page
  empty_context := empty_context

end CheckedControls
end CssNativeHighBit
