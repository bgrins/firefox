import CountTransport

namespace SubgridGuardedConsumer
open SubgridCountTransport

def remaining (nativeCap : Int) (stored : Nat) : Nat :=
  let capacity := nativeCap.toNat
  if stored < capacity then capacity - stored else 0

theorem guarded_transport (nativeCap : Int) (signedMax storageCap : Nat)
    (capFits : nativeCap ≤ (signedMax : Int))
    (storageFits : signedMax ≤ storageCap)
    (terms : List (Nat × Nat)) :
    (remaining nativeCap (cache storageCap terms) : Int) =
      max 0 (nativeCap - (total terms : Int)) ∧
    remaining nativeCap (cache storageCap terms) ≤ signedMax ∧
    (cache storageCap terms < nativeCap.toNat →
      nativeCap.toNat - cache storageCap terms ≤ signedMax) := by
  simp only [remaining, cache, cache_correct, Nat.zero_add]
  split <;> omega

example : remaining (-2147483648) 0 = 0 := by decide +kernel
example : remaining (-1) 4294967295 = 0 := by decide +kernel
example : remaining 0 0 = 0 := by decide +kernel
example : remaining 3 (cache 4294967295 [(2147483647, 2)]) = 0 := by decide +kernel
example : remaining 3 (cache 18446744073709551615 [(2147483647, 2)]) = 0 := by decide +kernel
example : remaining 2147483647 0 = 2147483647 := by decide +kernel
example : ¬ (remaining 3 (min 2 10) = 0) := by decide +kernel
example : max 0 (3 - narrow32 4294967295) ≠
    (remaining 3 4294967295 : Int) := by decide +kernel

#print axioms guarded_transport
end SubgridGuardedConsumer
