import Scaling

namespace ClampCandidate
open ClampNaN ClampScaling

inductive Hint where
  | notPercentage | rawPercentage | unresolvedPercentage
  deriving DecidableEq, Repr

inductive Op where
  | min | max
  deriving DecidableEq, Repr

def operation : Op → Number → Number → Number
  | .min => strictMin
  | .max => strictMax

def infinite : Number → Bool
  | .value .negInf | .value .posInf => true
  | _ => false

structure Interface (L E : Type) where
  raw : L → Option Number
  hint : L → Hint
  canonical : L → Bool
  nanTest : L → Option Bool
  tryOp : Op → L → L → Option L
  compare : L → L → Option Ordering
  evaluate : E → L → Number

def allowed (api : Interface L E) (leaf : L) : Bool :=
  match api.raw leaf with
  | none => false
  | some _ => api.hint leaf != .unresolvedPercentage

def Comparison (order : Ordering) (a b : Scalar) : Prop :=
  match order with
  | .lt => scalarLE a b
  | .eq => a = b
  | .gt => scalarLE b a

def relativeInfinity (api : Interface L E) (leaf : L) : Bool :=
  match api.raw leaf with
  | none => false
  | some value => infinite value && !api.canonical leaf

def safeFallback (api : Interface L E) (leaf : L) : Bool :=
  allowed api leaf && !relativeInfinity api leaf

def acceptResult (api : Interface L E) (a b c result : L) : Bool :=
  if relativeInfinity api a || relativeInfinity api b || relativeInfinity api c then
    match api.raw result with
    | none => false
    | some value => !finiteNumber value
  else true

inductive FoldCertificate (api : Interface L E) (a b c result : L) : Prop where
  | canonical (x y z : Number)
      (inputs : ∀ env, api.evaluate env a = x ∧ api.evaluate env b = y ∧ api.evaluate env c = z)
      (output : ∀ env, api.evaluate env result = nativeClamp x y z)
  | relative (basis : E → Rat) (nonnegative : ∀ env, 0 ≤ basis env) (x y z : Number)
      (inputs : ∀ env, api.evaluate env a = resolveScale (basis env) x ∧
        api.evaluate env b = resolveScale (basis env) y ∧ api.evaluate env c = resolveScale (basis env) z)
      (output : ∀ env, api.evaluate env result = resolveScale (basis env) (nativeClamp x y z))
      (guard : safeRelative x y z = true)

structure Bridge (api : Interface L E) : Prop where
  compatible : ∀ a b c inner result,
    allowed api a = true → allowed api b = true → allowed api c = true →
    api.tryOp .min b c = some inner → api.tryOp .max a inner = some result →
    acceptResult api a b c result = true → FoldCertificate api a b c result
  nonNan : ∀ leaf, safeFallback api leaf = true → api.nanTest leaf = some false →
    ∀ env, ∃ value, api.evaluate env leaf = .value value
  comparison : ∀ a b order, safeFallback api a = true → safeFallback api b = true →
    api.nanTest a = some false → api.nanTest b = some false → api.compare a b = some order →
    ∀ env x y, api.evaluate env a = .value x → api.evaluate env b = .value y → Comparison order x y

theorem certificate_sound (api : Interface L E) (a b c result : L)
    (certificate : FoldCertificate api a b c result) (env : E) :
    api.evaluate env result = specClamp (api.evaluate env a) (api.evaluate env b) (api.evaluate env c) := by
  cases certificate with
  | canonical x y z inputs output =>
    obtain ⟨hx, hy, hz⟩ := inputs env
    rw [output env, hx, hy, hz, native_clamp_sound orderLaws]
  | relative basis nonnegative x y z inputs output guard =>
    obtain ⟨hx, hy, hz⟩ := inputs env
    rw [output env, hx, hy, hz, native_clamp_sound orderLaws]
    exact guarded_common_unit_clamp (basis env) (nonnegative env) x y z guard

theorem comparison_not_gt (o : Ordering) (a b : Scalar) (h : Comparison o a b)
    (ng : o ≠ .gt) : scalarLE a b := by
  cases o <;> simp_all [Comparison, scalar_refl]

theorem comparison_not_lt (o : Ordering) (a b : Scalar) (h : Comparison o a b)
    (nl : o ≠ .lt) : scalarLE b a := by
  cases o <;> simp_all [Comparison, scalar_refl]

theorem minimum_left (a b : Scalar) (h : scalarLE a b) : minimum a b = a := by simp [minimum, h]

theorem minimum_right (a b : Scalar) (h : scalarLE b a) : minimum a b = b := by
  unfold minimum
  split
  · rename_i ab
    exact scalar_antisymm a b ab h
  · rfl

theorem maximum_left (a b : Scalar) (h : scalarLE b a) : maximum a b = a := by
  unfold maximum
  split
  · rename_i ab
    exact scalar_antisymm b a h ab
  · rfl

theorem maximum_right (a b : Scalar) (h : scalarLE a b) : maximum a b = b := by simp [maximum, h]

theorem lower_wins (a b c : Scalar) (ba : scalarLE b a) :
    maximum a (minimum b c) = a := by
  have mb := (minimum_spec orderLaws b c).1
  exact maximum_left a _ (scalar_trans _ _ _ mb ba)

def winner (api : Interface L E) (a b c : L) : Option L :=
  match api.compare a b with
  | none => none
  | some ab => if ab == .gt then some a else
    match api.compare c b with
    | none => none
    | some cb => if cb == .lt then
      match api.compare c a with
      | none => none
      | some ca => if ca == .lt then some a else some c
      else some b

theorem winner_sound (api : Interface L E) (bridge : Bridge api) (a b c result : L)
    (ha : safeFallback api a = true) (hb : safeFallback api b = true) (hc : safeFallback api c = true)
    (na : api.nanTest a = some false) (nb : api.nanTest b = some false) (nc : api.nanTest c = some false)
    (chosen : winner api a b c = some result) (env : E) :
    api.evaluate env result = specClamp (api.evaluate env a) (api.evaluate env b) (api.evaluate env c) := by
  obtain ⟨x, hx⟩ := bridge.nonNan a ha na env
  obtain ⟨y, hy⟩ := bridge.nonNan b hb nb env
  obtain ⟨z, hz⟩ := bridge.nonNan c hc nc env
  unfold winner at chosen
  split at chosen
  · simp at chosen
  · rename_i ab hab
    have cab := bridge.comparison a b ab ha hb na nb hab env x y hx hy
    split at chosen
    · rename_i gt
      simp only [beq_iff_eq] at gt
      subst ab
      cases chosen
      simp only [hx, hy, hz, specClamp, strictMin, strictMax]
      exact congrArg Number.value (lower_wins x y z cab).symm
    · rename_i notgt
      have xy := comparison_not_gt ab x y cab (by simpa only [beq_iff_eq] using notgt)
      split at chosen
      · simp at chosen
      · rename_i cb hcb
        have ccb := bridge.comparison c b cb hc hb nc nb hcb env z y hz hy
        split at chosen
        · rename_i lt
          simp only [beq_iff_eq] at lt
          subst cb
          split at chosen
          · simp at chosen
          · rename_i ca hca
            have cca := bridge.comparison c a ca hc ha nc na hca env z x hz hx
            split at chosen
            · rename_i ltca
              simp only [beq_iff_eq] at ltca
              subst ca
              cases chosen
              simp only [hx, hy, hz, specClamp, strictMin, strictMax, minimum_right y z ccb,
                maximum_left x z cca]
            · rename_i notlt
              have xz := comparison_not_lt ca z x cca (by simpa only [beq_iff_eq] using notlt)
              cases chosen
              simp only [hx, hy, hz, specClamp, strictMin, strictMax, minimum_right y z ccb,
                maximum_right x z xz]
        · rename_i notlt
          have yz := comparison_not_lt cb z y ccb (by simpa only [beq_iff_eq] using notlt)
          cases chosen
          simp only [hx, hy, hz, specClamp, strictMin, strictMax, minimum_left y z yz,
            maximum_right x y xy]

def strictFold (api : Interface L E) (a b c : L) : Option L := do
  let inner ← api.tryOp .min b c
  api.tryOp .max a inner

theorem strict_fold_sound (api : Interface L E) (bridge : Bridge api) (a b c result : L)
    (ha : allowed api a = true) (hb : allowed api b = true) (hc : allowed api c = true)
    (chosen : strictFold api a b c = some result) (accepted : acceptResult api a b c result = true) (env : E) :
    api.evaluate env result = specClamp (api.evaluate env a) (api.evaluate env b) (api.evaluate env c) := by
  unfold strictFold at chosen
  cases inner : api.tryOp .min b c with
  | none => simp [inner] at chosen
  | some mid =>
    simp only [inner, Option.bind_some] at chosen
    exact certificate_sound api a b c result (bridge.compatible a b c mid result ha hb hc inner chosen accepted) env

def leafFold (api : Interface L E) (a b c : L) : Option L :=
  if allowed api a && allowed api b && allowed api c then
    match strictFold api a b c with
    | some result => if acceptResult api a b c result then some result else none
    | none => if !relativeInfinity api a && !relativeInfinity api b && !relativeInfinity api c &&
        api.nanTest a == some false && api.nanTest b == some false &&
        api.nanTest c == some false then winner api a b c else none
  else none

theorem leaf_fold_sound (api : Interface L E) (bridge : Bridge api) (a b c result : L)
    (chosen : leafFold api a b c = some result) (env : E) :
    api.evaluate env result = specClamp (api.evaluate env a) (api.evaluate env b) (api.evaluate env c) := by
  unfold leafFold at chosen
  split at chosen
  · rename_i guard
    simp only [Bool.and_eq_true] at guard
    obtain ⟨⟨ha, hb⟩, hc⟩ := guard
    split at chosen
    · rename_i result' success
      split at chosen
      · rename_i accepted
        cases chosen
        exact strict_fold_sound api bridge a b c result ha hb hc success accepted env
      · simp at chosen
    · split at chosen
      · rename_i nonnan
        simp only [Bool.and_eq_true, beq_iff_eq] at nonnan
        obtain ⟨⟨⟨⟨⟨ia, ib⟩, ic⟩, na⟩, nb⟩, nc⟩ := nonnan
        apply winner_sound api bridge a b c result ?_ ?_ ?_ na nb nc chosen env
        · simp only [safeFallback, ha, ia, Bool.true_and]
        · simp only [safeFallback, hb, ib, Bool.true_and]
        · simp only [safeFallback, hc, ic, Bool.true_and]
      · simp at chosen
  · simp at chosen

inductive Tree (L : Type) where
  | leaf (value : L)
  | environment (name : Nat)
  | application (name : Nat) (argument : Tree L)
  | clamp (a b c : Tree L)

structure Semantics (E : Type) where
  environment : E → Nat → Number
  application : E → Nat → Number → Number

def evaluate (api : Interface L E) (sem : Semantics E) (env : E) : Tree L → Number
  | .leaf leaf => api.evaluate env leaf
  | .environment name => sem.environment env name
  | .application name argument => sem.application env name (evaluate api sem env argument)
  | .clamp a b c => specClamp (evaluate api sem env a) (evaluate api sem env b) (evaluate api sem env c)

def fold (api : Interface L E) (a b c : Tree L) : Tree L :=
  match a, b, c with
  | .leaf x, .leaf y, .leaf z =>
      match leafFold api x y z with
      | some result => .leaf result
      | none => .clamp a b c
  | _, _, _ => .clamp a b c

theorem fold_sound (api : Interface L E) (bridge : Bridge api) (sem : Semantics E) (env : E)
    (a b c : Tree L) : evaluate api sem env (fold api a b c) = evaluate api sem env (.clamp a b c) := by
  unfold fold
  split
  · rename_i x y z
    split
    · rename_i result chosen
      exact leaf_fold_sound api bridge x y z result chosen env
    · rfl
  · rfl

def simplify (api : Interface L E) : Tree L → Tree L
  | .leaf leaf => .leaf leaf
  | .environment name => .environment name
  | .application name argument => .application name (simplify api argument)
  | .clamp a b c => fold api (simplify api a) (simplify api b) (simplify api c)

theorem candidate_preservation (api : Interface L E) (bridge : Bridge api)
    (sem : Semantics E) (env : E) (tree : Tree L) :
    evaluate api sem env (simplify api tree) = evaluate api sem env tree := by
  induction tree with
  | leaf => rfl
  | environment => rfl
  | application name argument ih => simp only [simplify, evaluate, ih]
  | clamp a b c ia ib ic => simp only [simplify, fold_sound api bridge, evaluate, ia, ib, ic]

#print axioms certificate_sound
#print axioms winner_sound
#print axioms strict_fold_sound
#print axioms leaf_fold_sound
#print axioms fold_sound
#print axioms candidate_preservation

end ClampCandidate
