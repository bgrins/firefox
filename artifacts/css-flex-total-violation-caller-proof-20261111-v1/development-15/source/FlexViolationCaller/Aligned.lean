import FlexViolationCaller.Base

namespace FlexViolationCaller

theorem aligned_imp {R S : ItemState → ItemState → Prop} {xs ys : List ItemState}
    (h : Aligned R xs ys) (step : ∀ a b, R a b → S a b) : Aligned S xs ys := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [Aligned]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at h
    | cons y ys => exact ⟨step x y h.1, ih h.2⟩

theorem aligned_length {R : ItemState → ItemState → Prop} {xs ys : List ItemState}
    (h : Aligned R xs ys) : xs.length = ys.length := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [Aligned]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at h
    | cons y ys => simpa using ih h.2

theorem aligned_all {R : ItemState → ItemState → Prop} {P Q : ItemState → Prop}
    {xs ys : List ItemState} (h : Aligned R xs ys)
    (step : ∀ a b, R a b → P a → Q b) (hx : ∀ x ∈ xs, P x) : ∀ y ∈ ys, Q y := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [Aligned]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at h
    | cons y ys =>
      intro z hz
      rcases List.mem_cons.mp hz with rfl | hz
      · exact step x z h.1 (hx x (by simp))
      · exact ih h.2 (fun a ha => hx a (by simp [ha])) z hz

theorem aligned_trans {R S T : ItemState → ItemState → Prop} {xs ys zs : List ItemState}
    (hxy : Aligned R xs ys) (hyz : Aligned S ys zs)
    (step : ∀ a b c, R a b → S b c → T a c) : Aligned T xs zs := by
  induction xs generalizing ys zs with
  | nil => cases ys <;> cases zs <;> simp_all [Aligned]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at hxy
    | cons y ys =>
      cases zs with
      | nil => simp [Aligned] at hyz
      | cons z zs => exact ⟨step x y z hxy.1 hyz.1, ih hxy.2 hyz.2⟩

theorem aligned_map (f : ItemState → ItemState) (R : ItemState → ItemState → Prop)
    (xs : List ItemState) (h : ∀ x ∈ xs, R x (f x)) : Aligned R xs (xs.map f) := by
  induction xs with
  | nil => trivial
  | cons x xs ih => exact ⟨h x (by simp), ih (fun y hy => h y (by simp [hy]))⟩

theorem aligned_fields {xs ys : List ItemState}
    (h : Aligned (fun a b => a.fields = b.fields) xs ys) :
    xs.map ItemState.fields = ys.map ItemState.fields := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [Aligned]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at h
    | cons y ys => simpa only [List.map_cons, h.1] using congrArg (y.fields :: ·) (ih h.2)

theorem frozen_trans {xs ys zs : List ItemState}
    (hxy : FrozenPreserved xs ys) (hyz : FrozenPreserved ys zs) : FrozenPreserved xs zs := by
  apply aligned_trans hxy hyz
  intro a b c hab hbc
  refine ⟨hab.1.trans hbc.1, ?_⟩
  intro ha
  have hb := hab.2 ha
  subst b
  exact hbc.2 ha

theorem frozen_fields {xs ys : List ItemState} (h : FrozenPreserved xs ys) :
    xs.map ItemState.fields = ys.map ItemState.fields :=
  aligned_fields (aligned_imp h (fun _ _ h => h.1))

end FlexViolationCaller
