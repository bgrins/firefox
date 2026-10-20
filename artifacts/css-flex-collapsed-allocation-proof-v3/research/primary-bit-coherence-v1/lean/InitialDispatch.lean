import Publication

namespace PrimaryBit

inductive InitEffect where
  | queryRegistration | anchorReference | anchorNames | hiddenCount | autoRegistration
  | animationFlag | removeB | removeI | observe | unobserve | sticky
  deriving DecidableEq, Repr

structure InitialFacts where
  queryContainer : Bool
  anchorReference : Bool
  anchorNames : Bool
  nonDisplay : Bool
  hidden : Bool
  autoVisibility : Bool
  isElement : Bool
  autoB : Bool
  autoI : Bool
  hidesContent : Bool
  nonReplacedInline : Bool
  sticky : Bool
  svgLayout : Bool

def initialEffects (s : InitialFacts) : List InitEffect :=
  (if s.queryContainer then [.queryRegistration] else []) ++
  (if s.anchorReference then [.anchorReference] else []) ++
  (if s.anchorNames && !s.nonDisplay then [.anchorNames] else []) ++
  (if s.hidden then [.hiddenCount] else if s.autoVisibility then [.autoRegistration] else []) ++
  [.animationFlag] ++
  (if s.isElement then
    (if s.autoB then [] else [.removeB]) ++
    (if s.autoI then [] else [.removeI]) ++
    (if (s.autoB || s.autoI) && !s.hidesContent && !s.nonReplacedInline
      then [.observe] else [.unobserve])
   else []) ++
  (if s.sticky && !(s.nonDisplay || s.svgLayout) then [.sticky] else [])

def plainFacts : InitialFacts :=
  ⟨false, false, false, false, false, false, true,
    false, false, false, false, false, false⟩

def runEffect (c : Content) (e : InitEffect) (w : World) : Option World :=
  match e with
  | .animationFlag => some { w with animationUpdate := true }
  | .removeB => some (removeRememberedB w c)
  | .removeI => some (removeRememberedI w c)
  | .unobserve => some (unobserve w c)
  | _ => none

def runEffects (c : Content) : List InitEffect → World → Option World
  | [], w => some w
  | e :: es, w => (runEffect c e w).bind (runEffects c es)

theorem accepted_effect_preserves (c : Content) (e : InitEffect) (w after : World)
    (success : runEffect c e w = some after) : after.frames = w.frames := by
  cases e <;> simp [runEffect] at success <;> cases success <;> rfl

theorem successful_effects_preserve (c : Content) (es : List InitEffect) (w after : World)
    (success : runEffects c es w = some after) : after.frames = w.frames := by
  induction es generalizing w with
  | nil => simp [runEffects] at success; cases success; rfl
  | cons e es ih =>
    cases h : runEffect c e w with
    | none => simp [runEffects, h] at success
    | some mid =>
      have result := ih mid (by simpa [runEffects, h] using success)
      exact result.trans (accepted_effect_preserves c e w mid h)

theorem plain_dispatch : initialEffects plainFacts =
    [.animationFlag, .removeB, .removeI, .unobserve] := rfl

theorem plain_execution (c : Content) (w : World) :
    runEffects c (initialEffects plainFacts) w = some (ordinaryInit w c) := rfl

theorem unsupported_query_fails_closed (c : Content) (w : World) :
    runEffects c (initialEffects { plainFacts with queryContainer := true }) w = none := rfl

end PrimaryBit
