import Target

namespace CssNativeHighBit

def ofBytes (a b c d e : UInt8) : Backing :=
  fun i => match i.val with
    | 0 => a
    | 1 => b
    | 2 => c
    | 3 => d
    | _ => e

def firstHighOne : Fin 5 := 1

def copyWitness : Backing := ofBytes 82 197 184 255 128

def otherScalarWitness : Backing := ofBytes 82 194 162 255 128

def asciiComplementWitness : Backing := ofBytes 0 0 255 128 1

def fixedScalar (b : Backing) : Backing :=
  fun i => if i.val = 1 then 197 else if i.val = 2 then 184 else firstHigh firstHighOne b i

def zeroUnused (n : Nat) (b : Backing) : Backing :=
  fun i => if n ≤ i.val then 0 else b i

structure NativeContext where
  mode : UInt8
  page : Bool
  feature : Feature
  deriving DecidableEq, Repr

def restrictedContext (c : NativeContext) : Prop :=
  (c.mode &&& 4).toNat = 0 ∧ c.page = false

def dependentContext : NativeContext := ⟨4, false, .gecko⟩

def pageContext : NativeContext := ⟨0, true, .servo⟩

structure Controls : Prop where
  omitted_high_class :
    belongs 3 (.high firstHighOne) copyWitness ∧
      (∀ cell, admissible 3 cell → cell ≠ .high firstHighOne →
        ∀ raw, generate 3 cell raw ≠ copyWitness)
  fixed_remaining_high_bytes :
    belongs 3 (.high firstHighOne) otherScalarWitness ∧
      (∀ raw, fixedScalar raw ≠ otherScalarWitness)
  zeroed_unused_tail :
    belongs 3 (.high firstHighOne) copyWitness ∧
      (∀ raw, zeroUnused 3 (firstHigh firstHighOne raw) ≠ copyWitness)
  omitted_ascii_complement :
    isAscii 2 asciiComplementWitness ∧
      (∀ a : Fin 128, a.val ≠ 0 → ∀ raw,
        asciiChild 2 a raw ≠ asciiComplementWitness)
  restricted_mode_page :
    ¬ restrictedContext dependentContext ∧ ¬ restrictedContext pageContext ∧
      (¬ (∀ c : NativeContext, restrictedContext c))
  empty_context :
    (∀ b : Backing, ∀ c : Empty, False) ∧
      (¬ (∃ b : Backing, ∃ c : Empty, True))

end CssNativeHighBit
