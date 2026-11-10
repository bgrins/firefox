import Model

namespace CssAnimationTaint.Cases

def plain : Payload := ⟨[10], false⟩
def attr : Payload := ⟨[20], true⟩
def fallback : Payload := ⟨[30], false⟩
def empty : Payload := ⟨[], false⟩

def environment : Environment
  | 1 => ⟨some plain, true⟩
  | 2 => ⟨some attr, false⟩
  | 3 => ⟨some plain, false⟩
  | 4 => ⟨some attr, true⟩
  | _ => ⟨none, false⟩

def checks : List (String × Bool) := [
  ("missing reference", decide (evaluate environment .nonanimatable
    (.reference 0 none) = ⟨none, [0]⟩)),
  ("empty fallback is valid", decide (evaluate environment .nonanimatable
    (.reference 0 (some (.literal empty))) = ⟨some empty, [0]⟩)),
  ("blocked source selects fallback", decide (evaluate environment .nonanimatable
    (.reference 1 (some (.literal fallback))) = ⟨some fallback, [1]⟩)),
  ("blocked source without fallback", decide (evaluate environment .nonanimatable
    (.reference 1 none) = ⟨none, [1]⟩)),
  ("tainted source allowed in animatable destination", decide (evaluate environment .animatable
    (.reference 1 none) = ⟨some plain, [1]⟩)),
  ("attribute taint is independent", decide (evaluate environment .nonanimatable
    (.reference 2 none) = ⟨some attr, [2]⟩)),
  ("both taints preserved in animatable destination", decide (evaluate environment .animatable
    (.reference 4 none) = ⟨some attr, [4]⟩)),
  ("both taints blocked by animation gate", decide (evaluate environment .nonanimatable
    (.reference 4 none) = ⟨none, [4]⟩)),
  ("unused fallback not read", decide (evaluate environment .nonanimatable
    (.reference 3 (some (.reference 1 none))) = ⟨some plain, [3]⟩)),
  ("selected fallback preserves attribute taint", decide (evaluate environment .nonanimatable
    (.reference 1 (some (.reference 2 none))) = ⟨some attr, [1, 2]⟩)),
  ("nested rejection selects next fallback", decide (evaluate environment .nonanimatable
    (.reference 1 (some (.reference 4 (some (.literal fallback))))) =
      ⟨some fallback, [1, 4]⟩)),
  ("nested fallback failure propagates", decide (evaluate environment .nonanimatable
    (.reference 0 (some (.reference 1 none))) = ⟨none, [0, 1]⟩)),
  ("literal metadata preserved", decide (evaluate environment .nonanimatable
    (.literal attr) = ⟨some attr, []⟩)),
  ("same tokens different taint select different outcomes", decide (
    evaluate environment .nonanimatable (.reference 1 none) ≠
    evaluate environment .nonanimatable (.reference 3 none)))
]

end CssAnimationTaint.Cases
