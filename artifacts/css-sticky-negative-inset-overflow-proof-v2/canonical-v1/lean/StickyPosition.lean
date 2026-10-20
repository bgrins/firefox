import StickyAxis
namespace StickyPosition

def native (normal stickNear stickFar containNear containFar : Int) : Int :=
  min (max normal (min stickNear containFar)) (max stickFar containNear)

def project (point near far : Int) : Int :=
  if point < near then near else if far < point then far else point

theorem ordered_bounds (sl sh cl ch : Int) (hs : sl ≤ sh) (hc : cl ≤ ch) :
    min sl ch ≤ max sh cl := by omega

theorem native_projection (n sl sh cl ch : Int) (hs : sl ≤ sh) (hc : cl ≤ ch) :
    native n sl sh cl ch = project n (min sl ch) (max sh cl) := by
  unfold native project; split <;> (try split) <;> omega

theorem containment_when_normal_inside (n sl sh cl ch : Int)
    (hnl : cl ≤ n) (hnh : n ≤ ch) :
    cl ≤ native n sl sh cl ch ∧ native n sl sh cl ch ≤ ch := by
  unfold native; omega

theorem feasible_intersection_projection (n sl sh cl ch : Int)
    (hnl : cl ≤ n) (hnh : n ≤ ch)
    (feasible : max sl cl ≤ min sh ch) :
    native n sl sh cl ch = project n (max sl cl) (min sh ch) := by
  unfold native project; split <;> (try split) <;> omega

theorem idempotent (n sl sh cl ch : Int) :
    native (native n sl sh cl ch) sl sh cl ch = native n sl sh cl ch := by
  unfold native; omega

theorem translation_covariance (n sl sh cl ch d : Int) :
    native (n+d) (sl+d) (sh+d) (cl+d) (ch+d) = native n sl sh cl ch + d := by
  unfold native; omega

theorem inactive_identity (n cl ch low high : Int)
    (nl : low ≤ n) (nh : n ≤ high) :
    native n low high cl ch = n := by
  unfold native; omega

theorem empty_containment_policy : native 10 20 30 5 5 = 10 := by decide +kernel

theorem reversed_containment_policy : native 10 20 30 5 (-5) = 10 := by decide +kernel

theorem feasible_premise_necessary : native 100 0 200 0 10 = 100 := by decide +kernel

theorem reversed_stick_prefers_second_clamp : native 15 30 10 0 40 = 10 := by decide +kernel
end StickyPosition
