import StickyGeometry
namespace StickyRanges
structure Range where
  atScroll : Int
  maxOffset : Int
  deriving Repr, DecidableEq

def nearRange (normal stickNear containFar : Int) : Range :=
  ⟨stickNear-normal, max 0 (containFar-normal)⟩
def farRange (normal stickFar containNear : Int) : Range :=
  ⟨normal-stickFar, max 0 (normal-containNear)⟩

theorem range_offsets_nonnegative (n sl sh cl ch : Int) :
    0 ≤ (nearRange n sl ch).maxOffset ∧ 0 ≤ (farRange n sh cl).maxOffset := by
  simp only [nearRange,farRange]; omega

theorem thresholds_ordered (n sl sh : Int) (ordered : sl ≤ sh) :
    (farRange n sh 0).atScroll ≤ (nearRange n sl 0).atScroll := by
  simp only [nearRange,farRange]; omega

def displacement (scroll : Int) (near far : Range) : Int :=
  min (max 0 (scroll-near.atScroll)) near.maxOffset -
    min (max 0 (far.atScroll-scroll)) far.maxOffset

theorem position_range_agreement (n sl sh cl ch scroll : Int)
    (normalLow : cl ≤ n) (normalHigh : n ≤ ch) (ordered : sl ≤ sh) :
    StickyPosition.native n (sl+scroll) (sh+scroll) cl ch =
      n + displacement scroll (nearRange n sl ch) (farRange n sh cl) := by
  simp only [StickyPosition.native,displacement,nearRange,farRange]
  omega

def maskedDisplacement (scroll n sl sh cl ch : Int) (nearActive farActive : Bool) : Int :=
  (if nearActive then min (max 0 (scroll-(n-sl))) (max 0 (ch-n)) else 0) -
  (if farActive then min (max 0 ((n-sh)-scroll)) (max 0 (n-cl)) else 0)

theorem masked_position_range_agreement (n sl sh cl ch scroll low high : Int)
    (nearActive farActive : Bool)
    (normalLow : cl ≤ n) (normalHigh : n ≤ ch)
    (inactiveNearSafe : low ≤ cl) (inactiveFarSafe : ch ≤ high)
    (ordered : nearActive = true → farActive = true → sl ≤ sh) :
    StickyPosition.native n
      (if nearActive then sl+scroll else low)
      (if farActive then sh+scroll else high) cl ch =
    n + maskedDisplacement scroll n sl sh cl ch nearActive farActive := by
  cases nearActive <;> cases farActive <;>
    simp_all [StickyPosition.native,maskedDisplacement]
  all_goals omega

def earliest (offset endAt endMax startAt startMax : Int) : Int :=
  if endMax ≠ 0 ∧ offset ≤ endAt then offset-endMax
  else if startMax ≠ 0 ∧ offset > startAt then offset+startMax else offset

def latest (offset endAt endMax startAt startMax : Int) : Int :=
  if endMax ≠ 0 ∧ offset < endAt then offset-endMax
  else if startMax ≠ 0 ∧ offset ≥ startAt then offset+startMax else offset

theorem endpoint_interval_ordered (offset endAt endMax startAt startMax : Int)
    (em : 0 ≤ endMax) (sm : 0 ≤ startMax) (order : endAt ≤ startAt) :
    earliest offset endAt endMax startAt startMax ≤ latest offset endAt endMax startAt startMax := by
  unfold earliest latest
  repeat' split
  all_goals omega

theorem endpoints_only_differ_at_threshold (offset endAt endMax startAt startMax : Int)
    (notEnd : offset ≠ endAt) (notStart : offset ≠ startAt) :
    earliest offset endAt endMax startAt startMax = latest offset endAt endMax startAt startMax := by
  unfold earliest latest
  repeat' split
  all_goals omega

structure AbsoluteInterval where
  near : Int
  far : Int
  deriving Repr, DecidableEq

def moveInside (inner outer : AbsoluteInterval) : AbsoluteInterval :=
  let left := max outer.near inner.near
  let width := min (outer.far-outer.near) (inner.far-inner.near)
  let newLeft := min (left+width) outer.far - width
  ⟨newLeft,newLeft+width⟩

theorem clamped_inner_contained (inner outer : AbsoluteInterval)
    (io : inner.near ≤ inner.far) (oo : outer.near ≤ outer.far) :
    outer.near ≤ (moveInside inner outer).near ∧
    (moveInside inner outer).far ≤ outer.far ∧
    (moveInside inner outer).near ≤ (moveInside inner outer).far := by
  simp only [moveInside]; omega

theorem old_range_guard_counterexample :
    (farRange 200 0 0).atScroll > (nearRange 200 20 600).atScroll := by decide +kernel
end StickyRanges
