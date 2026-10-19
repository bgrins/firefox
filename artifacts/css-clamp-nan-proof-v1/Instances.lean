import Candidate

namespace ClampInstances
open ClampNaN ClampScaling ClampCandidate

def isNaN : Number → Bool
  | .nan => true
  | _ => false

def rawOp : Op → Number → Number → Number
  | .min => nativeMin
  | .max => nativeMax

def canonicalAPI : Interface Number Unit where
  raw n := some n
  hint _ := .notPercentage
  canonical _ := true
  nanTest n := some (isNaN n)
  tryOp op a b := some (rawOp op a b)
  compare _ _ := none
  evaluate _ n := n

theorem canonical_bridge : Bridge canonicalAPI where
  compatible := by
    intro a b c inner result ha hb hc hi hr accepted
    simp only [canonicalAPI, rawOp, Option.some.injEq] at hi hr
    subst inner
    subst result
    exact .canonical a b c (fun _ => ⟨rfl, rfl, rfl⟩) (fun _ => rfl)
  nonNan := by
    intro leaf allowed notnan env
    cases leaf with
    | nan => simp [canonicalAPI, isNaN] at notnan
    | value n => exact ⟨n, rfl⟩
  comparison := by
    intro a b order ha hb na nb compared
    simp [canonicalAPI] at compared

abbrev Basis := { value : Rat // 0 ≤ value }

def relativeAPI : Interface Number Basis where
  raw n := some n
  hint _ := .notPercentage
  canonical _ := false
  nanTest n := some (isNaN n)
  tryOp op a b := some (rawOp op a b)
  compare _ _ := none
  evaluate basis n := resolveScale basis.val n

theorem infinity_eq (n : Number) : infinite n = hasInfinity n := by cases n with
  | nan => rfl
  | value s => cases s <;> rfl

theorem accepted_relative (a b c : Number)
    (h : acceptResult relativeAPI a b c (nativeClamp a b c) = true) : safeRelative a b c = true := by
  simp only [acceptResult, relativeInfinity, relativeAPI, Bool.not_false, Bool.and_true,
    infinity_eq, native_clamp_sound orderLaws] at h
  unfold safeRelative
  split at h
  · rename_i infinity
    simp [infinity, h]
  · rename_i noInfinity
    simp_all

theorem relative_bridge : Bridge relativeAPI where
  compatible := by
    intro a b c inner result ha hb hc hi hr accepted
    simp only [relativeAPI, rawOp, Option.some.injEq] at hi hr
    subst inner
    subst result
    exact .relative Subtype.val (fun env => env.property) a b c (fun _ => ⟨rfl, rfl, rfl⟩)
      (fun _ => rfl) (accepted_relative a b c accepted)
  nonNan := by
    intro leaf allowed notnan env
    cases leaf with
    | nan => simp [relativeAPI, isNaN] at notnan
    | value s =>
      cases s with
      | negInf => simp [safeFallback, relativeInfinity, relativeAPI, infinite] at allowed
      | posInf => simp [safeFallback, relativeInfinity, relativeAPI, infinite] at allowed
      | finite n => exact ⟨scaled env.val (.finite n), resolve_finite_scale env.val (.finite n) rfl⟩
      | negZero => exact ⟨scaled env.val .negZero, resolve_finite_scale env.val .negZero rfl⟩
  comparison := by
    intro a b order ha hb na nb compared
    simp [relativeAPI] at compared

def fallbackAPI : Interface Number Unit := { canonicalAPI with
  tryOp := fun _ _ _ => none
  compare := fun a b => match a, b with
    | .value x, .value y => some (rawCompare x y)
    | _, _ => none }

theorem raw_compare_meaning (x y : Scalar) : Comparison (rawCompare x y) x y := by
  unfold rawCompare
  split
  · rename_i xy
    split
    · rename_i yx
      exact scalar_antisymm x y xy yx
    · exact xy
  · rename_i nxy
    exact (scalar_total x y).resolve_left nxy

theorem fallback_bridge : Bridge fallbackAPI where
  compatible := by
    intro a b c inner result ha hb hc hi
    simp [fallbackAPI] at hi
  nonNan := by
    intro leaf allowed notnan env
    cases leaf with
    | nan => simp [fallbackAPI, canonicalAPI, isNaN] at notnan
    | value n => exact ⟨n, rfl⟩
  comparison := by
    intro a b order ha hb na nb compared env x y hx hy
    cases a <;> cases b <;> simp_all [fallbackAPI, canonicalAPI]
    simpa [← compared] using raw_compare_meaning x y

theorem all_winner_branches :
    leafFold fallbackAPI (finite 3) (finite 1) (finite 2) = some (finite 3) ∧
    leafFold fallbackAPI (finite 2) (finite 3) (finite 1) = some (finite 2) ∧
    leafFold fallbackAPI (finite 1) (finite 3) (finite 2) = some (finite 2) ∧
    leafFold fallbackAPI (finite 1) (finite 2) (finite 3) = some (finite 2) ∧
    leafFold fallbackAPI (finite 3) (finite 1) .nan = none := by decide +kernel

theorem unresolved_percentage_retained :
    leafFold {canonicalAPI with hint := fun _ => .unresolvedPercentage}
      (finite 3) (finite 1) (finite 2) = none := by decide +kernel

theorem unavailable_raw_retained :
    leafFold {canonicalAPI with raw := fun _ => none}
      (finite 3) (finite 1) (finite 2) = none := by decide +kernel

def sem : Semantics Unit where
  environment _ _ := finite 16
  application _ _ _ := .nan

def unknownUpper : Tree Number := .application 0 (.environment 0)

def unknownWitness : Tree Number :=
  .clamp (.leaf (finite 75)) (.leaf (finite 25)) unknownUpper

theorem canonical_all_nan_positions (a b : Number) :
    leafFold canonicalAPI .nan a b = some .nan ∧
    leafFold canonicalAPI a .nan b = some .nan ∧
    leafFold canonicalAPI a b .nan = some .nan := by
  cases a <;> cases b <;> simp [leafFold, allowed, relativeInfinity, strictFold, acceptResult,
    canonicalAPI, rawOp, nativeMin, nativeMax]

theorem unknown_upper_kept : simplify canonicalAPI unknownWitness = unknownWitness := by rfl

theorem unknown_upper_nan : evaluate canonicalAPI sem () (simplify canonicalAPI unknownWitness) = .nan := by rfl

theorem relative_infinite_safe :
    leafFold relativeAPI (.value .posInf) (.value .posInf) (.value .posInf) = some (.value .posInf) ∧
    leafFold relativeAPI .nan (.value .posInf) (finite 2) = some .nan ∧
    leafFold relativeAPI (finite 1) (finite 2) (.value .posInf) = none := by decide +kernel

theorem relative_zero_sign :
    evaluate relativeAPI (⟨fun _ _ => .nan, fun _ _ n => n⟩) ⟨0, Rat.le_refl⟩
      (simplify relativeAPI (.clamp (.leaf (finite (-3))) (.leaf (finite (-2))) (.leaf (finite (-1))))) =
      .value .negZero := by decide +kernel

theorem relative_candidate_preservation (sem : Semantics Basis) (env : Basis) (tree : Tree Number) :
    evaluate relativeAPI sem env (simplify relativeAPI tree) = evaluate relativeAPI sem env tree :=
  candidate_preservation relativeAPI relative_bridge sem env tree

#print axioms fallback_bridge
#print axioms all_winner_branches
#print axioms unresolved_percentage_retained
#print axioms unavailable_raw_retained
#print axioms canonical_bridge
#print axioms relative_bridge
#print axioms canonical_all_nan_positions
#print axioms unknown_upper_kept
#print axioms unknown_upper_nan
#print axioms relative_infinite_safe
#print axioms relative_zero_sign
#print axioms relative_candidate_preservation
end ClampInstances
