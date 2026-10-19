import Init.Data.Rat.Lemmas

namespace ClampNaN

inductive Scalar where
  | negInf | finite (value : Rat) | negZero | posInf
  deriving DecidableEq, Repr

def scalarLE : Scalar → Scalar → Prop
  | .negInf, _ => True
  | _, .posInf => True
  | .posInf, _ => False
  | _, .negInf => False
  | .negZero, .negZero => True
  | .negZero, .finite b => 0 ≤ b
  | .finite a, .negZero => a < 0
  | .finite a, .finite b => a ≤ b

instance (a b : Scalar) : Decidable (scalarLE a b) := by
  cases a <;> cases b <;> simp only [scalarLE] <;> infer_instance

structure OrderLaws : Prop where
  refl : ∀ a, scalarLE a a
  trans : ∀ a b c, scalarLE a b → scalarLE b c → scalarLE a c
  total : ∀ a b, scalarLE a b ∨ scalarLE b a
  antisymm : ∀ a b, scalarLE a b → scalarLE b a → a = b

theorem rat_lt_le (a b c : Rat) (ab : a < b) (bc : b ≤ c) : a < c := by
  apply Rat.not_le.mp
  intro ca
  exact Rat.not_le.mpr ab (Rat.le_trans bc ca)

theorem rat_le_lt (a b c : Rat) (ab : a ≤ b) (bc : b < c) : a < c := by
  apply Rat.not_le.mp
  intro ca
  exact Rat.not_le.mpr bc (Rat.le_trans ca ab)

theorem scalar_refl (a : Scalar) : scalarLE a a := by
  cases a <;> simp [scalarLE, Rat.le_refl]

theorem scalar_total (a b : Scalar) : scalarLE a b ∨ scalarLE b a := by
  cases a <;> cases b <;> simp only [scalarLE, true_or, or_true]
  · exact Rat.le_total
  · exact Classical.em _ |>.imp_right Rat.not_lt.mp
  · exact (Classical.em _).imp_right Rat.not_le.mp

theorem scalar_antisymm (a b : Scalar) (ab : scalarLE a b) (ba : scalarLE b a) : a = b := by
  cases a <;> cases b <;> simp_all [scalarLE]
  · exact Rat.le_antisymm ab ba
  · exact (Rat.not_le.mpr ab ba).elim
  · exact (Rat.not_le.mpr ba ab).elim

theorem scalar_trans (a b c : Scalar) (ab : scalarLE a b) (bc : scalarLE b c) : scalarLE a c := by
  cases a <;> cases b <;> cases c <;> simp_all [scalarLE]
  · exact Rat.le_trans ab bc
  · exact rat_le_lt _ _ _ ab bc
  · exact Rat.le_trans (Rat.le_of_lt ab) bc
  · exact Rat.le_trans ab bc

theorem orderLaws : OrderLaws := ⟨scalar_refl, scalar_trans, scalar_total, scalar_antisymm⟩

inductive Number where
  | nan | value (scalar : Scalar)
  deriving DecidableEq, Repr

def minimum (a b : Scalar) : Scalar := if scalarLE a b then a else b

def maximum (a b : Scalar) : Scalar := if scalarLE a b then b else a

def strictMin : Number → Number → Number
  | .value a, .value b => .value (minimum a b)
  | _, _ => .nan

def strictMax : Number → Number → Number
  | .value a, .value b => .value (maximum a b)
  | _, _ => .nan

def specClamp (lower center upper : Number) : Number :=
  strictMax lower (strictMin center upper)

def IsMinimum (a b result : Scalar) : Prop :=
  scalarLE result a ∧ scalarLE result b ∧
    ∀ x, scalarLE x a → scalarLE x b → scalarLE x result

def IsMaximum (a b result : Scalar) : Prop :=
  scalarLE a result ∧ scalarLE b result ∧
    ∀ x, scalarLE a x → scalarLE b x → scalarLE result x

theorem minimum_spec (laws : OrderLaws) (a b : Scalar) : IsMinimum a b (minimum a b) := by
  unfold minimum
  split
  · rename_i h
    exact ⟨laws.refl a, h, fun _ ha _ => ha⟩
  · rename_i h
    exact ⟨(laws.total a b).resolve_left h, laws.refl b, fun _ _ hb => hb⟩

theorem maximum_spec (laws : OrderLaws) (a b : Scalar) : IsMaximum a b (maximum a b) := by
  unfold maximum
  split
  · rename_i h
    exact ⟨h, laws.refl b, fun _ _ hb => hb⟩
  · rename_i h
    exact ⟨laws.refl a, (laws.total a b).resolve_left h, fun _ ha _ => ha⟩

def ClampRelation (lower center upper result : Number) : Prop :=
  match lower, center, upper with
  | .value a, .value b, .value c =>
      ∃ middle final, IsMinimum b c middle ∧ IsMaximum a middle final ∧ result = .value final
  | _, _, _ => result = .nan

theorem spec_satisfies_relation (laws : OrderLaws) (a b c : Number) :
    ClampRelation a b c (specClamp a b c) := by
  cases a <;> cases b <;> cases c <;> simp only [ClampRelation, specClamp, strictMin, strictMax]
  all_goals first | rfl | exact ⟨_, _, minimum_spec laws _ _, maximum_spec laws _ _, rfl⟩

def rawCompare (a b : Scalar) : Ordering :=
  if scalarLE a b then if scalarLE b a then .eq else .lt else .gt

def nativeMin (a b : Number) : Number :=
  match a, b with
  | .nan, _ | _, .nan => .nan
  | .value x, .value y =>
      if rawCompare x y == .gt then .value y else .value x

def nativeMax (a b : Number) : Number :=
  match a, b with
  | .nan, _ | _, .nan => .nan
  | .value x, .value y =>
      if rawCompare x y == .lt then .value y else .value x

theorem native_min_sound (a b : Number) : nativeMin a b = strictMin a b := by
  cases a <;> cases b <;> simp [nativeMin, strictMin, rawCompare, minimum]
  repeat' first | split | simp_all

theorem native_max_sound (laws : OrderLaws) (a b : Number) : nativeMax a b = strictMax a b := by
  cases a <;> cases b <;> simp [nativeMax, strictMax, rawCompare, maximum]
  split
  · rename_i h
    split
    · rename_i h'
      simp [laws.antisymm _ _ h h']
    · simp
  · simp

def nativeClamp (a b c : Number) : Number := nativeMax a (nativeMin b c)

theorem native_clamp_sound (laws : OrderLaws) (a b c : Number) :
    nativeClamp a b c = specClamp a b c := by
  simp [nativeClamp, native_min_sound, native_max_sound laws, specClamp]

def Monotone (f : Scalar → Scalar) : Prop :=
  ∀ a b, scalarLE a b → scalarLE (f a) (f b)

theorem minimum_map (f : Scalar → Scalar) (mono : Monotone f) (a b : Scalar) :
    f (minimum a b) = minimum (f a) (f b) := by
  unfold minimum
  by_cases h : scalarLE a b
  · simp [h, mono a b h]
  · have rev := scalar_total a b |>.resolve_left h
    by_cases mapped : scalarLE (f a) (f b)
    · simp only [h, mapped, ite_false, ite_true]
      exact scalar_antisymm _ _ (mono b a rev) mapped
    · simp [h, mapped]

theorem maximum_map (f : Scalar → Scalar) (mono : Monotone f) (a b : Scalar) :
    f (maximum a b) = maximum (f a) (f b) := by
  unfold maximum
  by_cases h : scalarLE a b
  · simp [h, mono a b h]
  · have rev := scalar_total a b |>.resolve_left h
    by_cases mapped : scalarLE (f a) (f b)
    · simp only [h, mapped, ite_false, ite_true]
      exact scalar_antisymm _ _ mapped (mono b a rev)
    · simp [h, mapped]

def scaleZero : Scalar → Scalar
  | .negInf | .negZero => .negZero
  | .posInf => .finite 0
  | .finite a => if a < 0 then .negZero else .finite 0

theorem scale_zero_monotone : Monotone scaleZero := by
  intro a b ab
  cases a <;> cases b
  case finite.finite a b =>
    by_cases ha : a < 0 <;> by_cases hb : b < 0 <;> simp_all [scalarLE, scaleZero, Rat.le_refl]
    exact (ha (rat_le_lt _ _ _ ab hb)).elim
  case negInf.finite b =>
    by_cases hb : b < 0 <;> simp_all [scalarLE, scaleZero, Rat.le_refl]
  case finite.negInf a => simp_all [scalarLE]
  case finite.negZero a => simp_all [scalarLE, scaleZero]
  case finite.posInf a =>
    by_cases ha : a < 0 <;> simp_all [scalarLE, scaleZero, Rat.le_refl]
  case negZero.finite b =>
    have hb : ¬ b < 0 := Rat.not_lt.mpr ab
    simp [scalarLE, scaleZero, hb, Rat.le_refl]
  case posInf.finite b => simp_all [scalarLE]
  all_goals simp_all [scalarLE, scaleZero, Rat.le_refl]

def scalePositive (basis : Rat) : Scalar → Scalar
  | .finite a => .finite (a * basis)
  | other => other

theorem scale_positive_monotone (basis : Rat) (positive : 0 < basis) :
    Monotone (scalePositive basis) := by
  intro a b ab
  cases a <;> cases b <;> simp_all [scalarLE, scalePositive]
  · exact Rat.mul_le_mul_of_nonneg_right ab (Rat.le_of_lt positive)
  · exact (Rat.mul_neg_iff_of_pos_right positive).mpr ab
  · exact Rat.mul_nonneg ab (Rat.le_of_lt positive)

def scaled (basis : Rat) : Scalar → Scalar :=
  if basis = 0 then scaleZero else scalePositive basis

theorem scaled_monotone (basis : Rat) (nonnegative : 0 ≤ basis) : Monotone (scaled basis) := by
  unfold scaled
  split
  · exact scale_zero_monotone
  · rename_i nonzero
    exact scale_positive_monotone basis (Rat.lt_of_le_of_ne nonnegative (Ne.symm nonzero))

def finiteScalar : Scalar → Bool
  | .finite _ | .negZero => true
  | _ => false

theorem finite_minimum (a b : Scalar) (ha : finiteScalar a = true) (hb : finiteScalar b = true) :
    finiteScalar (minimum a b) = true := by unfold minimum; split <;> assumption

theorem finite_maximum (a b : Scalar) (ha : finiteScalar a = true) (hb : finiteScalar b = true) :
    finiteScalar (maximum a b) = true := by unfold maximum; split <;> assumption

def resolveScale (basis : Rat) : Number → Number
  | .nan => .nan
  | .value a => if basis = 0 ∧ finiteScalar a = false then .nan else .value (scaled basis a)

theorem resolve_finite_scale (basis : Rat) (a : Scalar) (ha : finiteScalar a = true) :
    resolveScale basis (.value a) = .value (scaled basis a) := by simp [resolveScale, ha]

theorem finite_common_unit_clamp (basis : Rat) (nonnegative : 0 ≤ basis) (a b c : Scalar)
    (ha : finiteScalar a = true) (hb : finiteScalar b = true) (hc : finiteScalar c = true) :
    resolveScale basis (specClamp (.value a) (.value b) (.value c)) =
      specClamp (resolveScale basis (.value a)) (resolveScale basis (.value b))
        (resolveScale basis (.value c)) := by
  simp only [specClamp, strictMin, strictMax]
  rw [resolve_finite_scale basis a ha, resolve_finite_scale basis b hb,
    resolve_finite_scale basis c hc,
    resolve_finite_scale basis _ (finite_maximum _ _ ha (finite_minimum _ _ hb hc))]
  simp only [strictMin, strictMax]
  rw [maximum_map _ (scaled_monotone basis nonnegative), minimum_map _ (scaled_monotone basis nonnegative)]

theorem nonfinite_zero_basis_counterexample :
    resolveScale 0 (.value .posInf) = .nan ∧
    resolveScale 0 (.value .negInf) = .nan := by decide +kernel

theorem negative_basis_counterexample :
    resolveScale (-1) (specClamp (.value (.finite 1)) (.value (.finite 2)) (.value (.finite 3))) ≠
      specClamp (resolveScale (-1) (.value (.finite 1))) (resolveScale (-1) (.value (.finite 2)))
        (resolveScale (-1) (.value (.finite 3))) := by decide +kernel

theorem greater_lower_wins (a b c : Scalar) (greater : ¬ scalarLE a b) :
    maximum a (minimum b c) = a := by
  unfold minimum
  split
  · simp [maximum, greater]
  · rename_i not_bc
    have cb := (scalar_total b c).resolve_left not_bc
    have not_ac : ¬ scalarLE a c := fun ac => greater (scalar_trans a c b ac cb)
    simp [maximum, not_ac]

def finiteUnitFold (a b c : Scalar) : Scalar :=
  maximum a (minimum b c)

theorem common_unit_rewrite_sound (basis : Rat) (nonnegative : 0 ≤ basis) (a b c : Scalar)
    (ha : finiteScalar a = true) (hb : finiteScalar b = true) (hc : finiteScalar c = true) :
    resolveScale basis (.value (finiteUnitFold a b c)) =
      specClamp (resolveScale basis (.value a)) (resolveScale basis (.value b))
        (resolveScale basis (.value c)) := finite_common_unit_clamp basis nonnegative a b c ha hb hc

inductive Expr where
  | literal (number : Number)
  | environment (name : Nat)
  | operation (name : Nat) (argument : Expr)
  | clamp (lower center upper : Expr)
  deriving DecidableEq, Repr

structure Context where
  values : Nat → Number
  operators : Nat → Number → Number

def eval (ctx : Context) : Expr → Number
  | .literal n => n
  | .environment name => ctx.values name
  | .operation name argument => ctx.operators name (eval ctx argument)
  | .clamp a b c => specClamp (eval ctx a) (eval ctx b) (eval ctx c)

def AlwaysScalar (expr : Expr) : Prop := ∀ ctx, ∃ n, eval ctx expr = .value n

def AlwaysGreater (a b : Expr) : Prop := ∀ ctx x y,
  eval ctx a = .value x → eval ctx b = .value y → ¬ scalarLE x y

theorem guarded_early_return (a b c : Expr)
    (ha : AlwaysScalar a) (hb : AlwaysScalar b) (hc : AlwaysScalar c)
    (greater : AlwaysGreater a b) (ctx : Context) :
    eval ctx a = eval ctx (.clamp a b c) := by
  obtain ⟨x, hx⟩ := ha ctx
  obtain ⟨y, hy⟩ := hb ctx
  obtain ⟨z, hz⟩ := hc ctx
  simp only [eval, hx, hy, hz, specClamp, strictMin, strictMax]
  exact congrArg Number.value (greater_lower_wins x y z (greater ctx x y hx hy)).symm

def known : Expr → Option Number
  | .literal n => some n
  | _ => none

theorem known_sound (expr : Expr) (value : Number) (h : known expr = some value)
    (ctx : Context) : eval ctx expr = value := by
  cases expr <;> simp_all [known, eval]

def foldClamp (a b c : Expr) : Expr :=
  match known a, known b, known c with
  | some x, some y, some z => .literal (nativeClamp x y z)
  | _, _, _ => .clamp a b c

theorem fold_sound (laws : OrderLaws) (ctx : Context) (a b c : Expr) :
    eval ctx (foldClamp a b c) = eval ctx (.clamp a b c) := by
  unfold foldClamp
  split
  · rename_i x y z ha hb hc
    simp only [eval, native_clamp_sound laws, known_sound a x ha ctx,
      known_sound b y hb ctx, known_sound c z hc ctx]
  · rfl

def simplify : Expr → Expr
  | .literal n => .literal n
  | .environment name => .environment name
  | .operation name argument => .operation name (simplify argument)
  | .clamp a b c => foldClamp (simplify a) (simplify b) (simplify c)

theorem simplify_sound (laws : OrderLaws) (ctx : Context) (expr : Expr) :
    eval ctx (simplify expr) = eval ctx expr := by
  induction expr with
  | literal => rfl
  | environment => rfl
  | operation name argument ih => simp only [simplify, eval, ih]
  | clamp a b c ia ib ic =>
    simp only [simplify, fold_sound laws, eval, ia, ib, ic]

theorem simplified_clamp_relation (laws : OrderLaws) (ctx : Context) (a b c : Expr) :
    ClampRelation (eval ctx a) (eval ctx b) (eval ctx c)
      (eval ctx (simplify (.clamp a b c))) := by
  rw [simplify_sound laws]
  exact spec_satisfies_relation laws _ _ _

theorem simplify_sound_unconditional (ctx : Context) (expr : Expr) :
    eval ctx (simplify expr) = eval ctx expr := simplify_sound orderLaws ctx expr

theorem clamp_relation_unconditional (ctx : Context) (a b c : Expr) :
    ClampRelation (eval ctx a) (eval ctx b) (eval ctx c)
      (eval ctx (simplify (.clamp a b c))) := simplified_clamp_relation orderLaws ctx a b c

def oldFold (a b c : Expr) : Expr :=
  match known a, known b with
  | some (.value lower), some (.value center) =>
      if rawCompare lower center == .gt then a else .clamp a b c
  | _, _ => .clamp a b c

def finite (x : Rat) : Number := .value (.finite x)

def witnessUpper : Expr := .operation 0 (.environment 0)

def witness : Expr := .clamp (.literal (finite 75)) (.literal (finite 25)) witnessUpper

def nanContext : Context := ⟨fun _ => finite 16, fun _ _ => .nan⟩
def finiteContext : Context := ⟨fun _ => finite 16, fun _ n => n⟩

theorem old_unknown_counterexample :
    eval nanContext (oldFold (.literal (finite 75)) (.literal (finite 25)) witnessUpper) = finite 75 ∧
    eval nanContext witness = .nan := by decide +kernel

theorem old_literal_counterexample :
    eval nanContext (oldFold (.literal (finite 75)) (.literal (finite 25)) (.literal .nan)) = finite 75 ∧
    eval nanContext (.clamp (.literal (finite 75)) (.literal (finite 25)) (.literal .nan)) = .nan := by decide +kernel

theorem retain_unknown_upper : simplify witness = witness := by decide +kernel

theorem unknown_environment_changes_result :
    eval nanContext witness = .nan ∧ eval finiteContext witness = finite 75 := by decide +kernel

theorem nan_in_every_position (a b : Number) :
    nativeClamp .nan a b = .nan ∧ nativeClamp a .nan b = .nan ∧ nativeClamp a b .nan = .nan := by
  cases a <;> cases b <;> simp [nativeClamp, nativeMin, nativeMax]

theorem signed_zero_order :
    rawCompare .negZero (.finite 0) = .lt ∧ rawCompare (.finite 0) .negZero = .gt ∧
    nativeClamp (.value .negZero) (finite 0) (.value .negZero) = .value .negZero ∧
    nativeClamp (finite 0) (.value .negZero) (finite 0) = finite 0 := by decide +kernel

theorem infinity_controls :
    nativeClamp (.value .negInf) (finite 2) (.value .posInf) = finite 2 ∧
    nativeClamp (.value .posInf) (finite 2) (.value .negInf) = .value .posInf ∧
    nativeClamp (.value .posInf) (finite 2) .nan = .nan := by decide +kernel

#print axioms orderLaws
#print axioms minimum_spec
#print axioms maximum_spec
#print axioms spec_satisfies_relation
#print axioms native_min_sound
#print axioms native_max_sound
#print axioms native_clamp_sound
#print axioms common_unit_rewrite_sound
#print axioms guarded_early_return
#print axioms finite_common_unit_clamp
#print axioms nonfinite_zero_basis_counterexample
#print axioms negative_basis_counterexample
#print axioms known_sound
#print axioms fold_sound
#print axioms simplify_sound
#print axioms simplified_clamp_relation
#print axioms simplify_sound_unconditional
#print axioms clamp_relation_unconditional
#print axioms old_unknown_counterexample
#print axioms old_literal_counterexample
#print axioms retain_unknown_upper
#print axioms unknown_environment_changes_result
#print axioms nan_in_every_position
#print axioms signed_zero_order
#print axioms infinity_controls

end ClampNaN
