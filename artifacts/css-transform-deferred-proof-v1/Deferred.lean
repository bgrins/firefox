import Init.Data.Rat.Lemmas

namespace DeferredTransform

inductive Failure where
  | needsContext | unsupportedDeferred | semanticFailure
  deriving DecidableEq, Repr

inductive Result (M : Type) where
  | ok (matrix : M)
  | error (failure : Failure)
  deriving DecidableEq, Repr

structure Algebra (M : Type) where
  identity : M
  translate : Rat → M
  compose : M → M → M
  interpolate : Rat → M → M → Result M
  accumulate : Nat → M → M → Result M

inductive Transform (M : Type) where
  | empty
  | constant (matrix : M)
  | length (pixels percent : Rat)
  | invalid
  | append (head tail : Transform M)
  | interpolate (progress : Rat) (left right : Transform M)
  | accumulate (count : Nat) (left right : Transform M)
  deriving Repr

def combine (f : M → M → Result M) (left right : Result M) : Result M :=
  match left, right with
  | .ok a, .ok b => f a b
  | .error e, _ => .error e
  | _, .error e => .error e

def evaluate (alg : Algebra M) (box : Rat) : Transform M → Result M
  | .empty => .ok alg.identity
  | .constant m => .ok m
  | .length pixels percent => .ok (alg.translate (pixels + percent * box))
  | .invalid => .error .semanticFailure
  | .append a b => combine (fun x y => .ok (alg.compose x y))
      (evaluate alg box a) (evaluate alg box b)
  | .interpolate p a b => combine (alg.interpolate p)
      (evaluate alg box a) (evaluate alg box b)
  | .accumulate n a b => combine (alg.accumulate n)
      (evaluate alg box a) (evaluate alg box b)

def partialEval (alg : Algebra M) : Transform M → Result M
  | .empty => .ok alg.identity
  | .constant m => .ok m
  | .length pixels percent => if percent = 0 then .ok (alg.translate pixels)
      else .error .needsContext
  | .invalid => .error .semanticFailure
  | .append a b => combine (fun x y => .ok (alg.compose x y))
      (partialEval alg a) (partialEval alg b)
  | .interpolate p a b => combine (alg.interpolate p)
      (partialEval alg a) (partialEval alg b)
  | .accumulate n a b => combine (alg.accumulate n)
      (partialEval alg a) (partialEval alg b)

def eager (alg : Algebra M) : Transform M → Result M
  | .empty => .ok alg.identity
  | .constant m => .ok m
  | .length pixels percent => if percent = 0 then .ok (alg.translate pixels)
      else .error .needsContext
  | .invalid => .error .semanticFailure
  | .append a b => combine (fun x y => .ok (alg.compose x y))
      (eager alg a) (eager alg b)
  | .interpolate _ _ _ => .error .unsupportedDeferred
  | .accumulate _ _ _ => .error .unsupportedDeferred

theorem combine_success (f : M → M → Result M) (a b : Result M) (m : M)
    (h : combine f a b = .ok m) :
    ∃ x y, a = .ok x ∧ b = .ok y ∧ f x y = .ok m := by
  cases a with
  | error e => simp [combine] at h
  | ok x => cases b with
    | error e => simp [combine] at h
    | ok y => exact ⟨x, y, rfl, rfl, h⟩

theorem partial_sound (alg : Algebra M) (tree : Transform M) :
    ∀ m, partialEval alg tree = .ok m → ∀ box, evaluate alg box tree = .ok m := by
  induction tree with
  | empty => intro m h box; exact h
  | constant x => intro m h box; exact h
  | length px pct =>
    intro m h box
    by_cases hp : pct = 0
    · simpa [partialEval, evaluate, hp, Rat.add_zero] using h
    · simp [partialEval, hp] at h
  | invalid => intro m h; simp [partialEval] at h
  | append a b ia ib =>
    intro m h box
    obtain ⟨x, y, hx, hy, hf⟩ := combine_success _ _ _ _ h
    simp only [evaluate, ia x hx box, ib y hy box, combine]
    exact hf
  | interpolate p a b ia ib =>
    intro m h box
    obtain ⟨x, y, hx, hy, hf⟩ := combine_success _ _ _ _ h
    simp only [evaluate, ia x hx box, ib y hy box, combine]
    exact hf
  | accumulate n a b ia ib =>
    intro m h box
    obtain ⟨x, y, hx, hy, hf⟩ := combine_success _ _ _ _ h
    simp only [evaluate, ia x hx box, ib y hy box, combine]
    exact hf

theorem eager_refines_partial (alg : Algebra M) (tree : Transform M) :
    ∀ m, eager alg tree = .ok m → partialEval alg tree = .ok m := by
  induction tree with
  | empty => exact fun _ h => h
  | constant _ => exact fun _ h => h
  | length _ _ => exact fun _ h => h
  | invalid => exact fun _ h => h
  | append a b ia ib =>
    intro m h
    obtain ⟨x, y, hx, hy, hf⟩ := combine_success _ _ _ _ h
    simp only [partialEval, ia x hx, ib y hy, combine]
    exact hf
  | interpolate => intro m h; simp [eager] at h
  | accumulate => intro m h; simp [eager] at h

theorem eager_sound (alg : Algebra M) (tree : Transform M) (m : M)
    (h : eager alg tree = .ok m) (box : Rat) : evaluate alg box tree = .ok m :=
  partial_sound alg tree m (eager_refines_partial alg tree m h) box

def transformList (items : List (Transform M)) : Transform M :=
  items.foldr Transform.append .empty

theorem arbitrary_list_sound (alg : Algebra M) (items : List (Transform M))
    (m : M) (h : eager alg (transformList items) = .ok m) (box : Rat) :
    evaluate alg box (transformList items) = .ok m := eager_sound alg _ _ h box

theorem list_success_members (alg : Algebra M) (items : List (Transform M))
    (tree : Transform M) (member : tree ∈ items) (m : M)
    (success : eager alg (transformList items) = .ok m) :
    ∃ value, eager alg tree = .ok value := by
  induction items generalizing m with
  | nil => simp at member
  | cons head tail ih =>
    obtain ⟨x, y, hx, hy, _⟩ := combine_success _ _ _ _ success
    simp only [List.mem_cons] at member
    cases member with
    | inl same => subst tree; exact ⟨x, hx⟩
    | inr inside => exact ih inside y hy

theorem list_failure_propagates (alg : Algebra M) (items : List (Transform M))
    (tree : Transform M) (member : tree ∈ items)
    (failure : ∀ m, eager alg tree ≠ .ok m) :
    ∀ m, eager alg (transformList items) ≠ .ok m := by
  intro m success
  obtain ⟨value, hv⟩ := list_success_members alg items tree member m success
  exact failure value hv

inductive Operation where
  | interpolate (progress : Rat)
  | accumulate (count : Nat)
  deriving DecidableEq, Repr

def applyOperation (alg : Algebra M) : Operation → M → M → Result M
  | .interpolate p => alg.interpolate p
  | .accumulate n => alg.accumulate n

def deferred (op : Operation) (left right : Transform M) : Transform M :=
  match op with
  | .interpolate p => .interpolate p left right
  | .accumulate n => .accumulate n left right

def attempt (alg : Algebra M) (native : Operation → M → M → Result M)
    (op : Operation) (left right : Transform M) : Transform M :=
  match combine (native op) (eager alg left) (eager alg right) with
  | .ok value => .constant value
  | .error _ => deferred op left right

def OperatorSound (alg : Algebra M) (native : Operation → M → M → Result M) : Prop :=
  ∀ op a b m, native op a b = .ok m → applyOperation alg op a b = .ok m

theorem deferred_denotation (alg : Algebra M) (box : Rat) (op : Operation)
    (left right : Transform M) :
    evaluate alg box (deferred op left right) =
      combine (applyOperation alg op) (evaluate alg box left) (evaluate alg box right) := by
  cases op <;> rfl

theorem attempt_sound (alg : Algebra M) (native : Operation → M → M → Result M)
    (sound : OperatorSound alg native) (op : Operation) (left right : Transform M)
    (box : Rat) :
    evaluate alg box (attempt alg native op left right) =
      evaluate alg box (deferred op left right) := by
  unfold attempt
  cases success : combine (native op) (eager alg left) (eager alg right) with
  | error e => rfl
  | ok value =>
    obtain ⟨x, y, hx, hy, hv⟩ := combine_success _ _ _ _ success
    rw [deferred_denotation, eager_sound alg left x hx box, eager_sound alg right y hy box]
    simp only [evaluate, combine]
    exact (sound op x y value hv).symm

theorem fallback_preserves_left (alg : Algebra M) (native : Operation → M → M → Result M)
    (op : Operation) (left right : Transform M) (e : Failure)
    (h : eager alg left = .error e) :
    attempt alg native op left right = deferred op left right := by
  simp [attempt, h, combine]

theorem fallback_preserves_right (alg : Algebra M) (native : Operation → M → M → Result M)
    (op : Operation) (left right : Transform M) (e : Failure)
    (h : eager alg right = .error e) :
    attempt alg native op left right = deferred op left right := by
  cases hl : eager alg left <;> simp [attempt, hl, h, combine]

structure Affine where
  scale : Rat
  offset : Rat
  deriving DecidableEq, Repr

def affine : Algebra Affine where
  identity := ⟨1, 0⟩
  translate x := ⟨1, x⟩
  compose a b := ⟨a.scale * b.scale, a.offset + a.scale * b.offset⟩
  interpolate p a b := if a.scale > 0 ∧ b.scale > 0 then
    .ok ⟨(1-p) * a.scale + p * b.scale, (1-p) * a.offset + p * b.offset⟩
    else .error .semanticFailure
  accumulate n a b := if a.scale > 0 ∧ b.scale > 0 then
    .ok ⟨n * (a.scale - 1) + b.scale, n * a.offset + b.offset⟩
    else .error .semanticFailure

def percentageEndpoint (scale : Rat) : Transform Affine :=
  .accumulate 1 (.length 0 (1/2)) (.constant ⟨scale, 0⟩)

def witness : Transform Affine :=
  .interpolate (1/2) (percentageEndpoint 1) (percentageEndpoint 2)

def oldEager (alg : Algebra M) : Transform M → Result M
  | .empty => .ok alg.identity
  | .constant m => .ok m
  | .length px pct => if pct = 0 then .ok (alg.translate px) else .error .needsContext
  | .invalid => .error .semanticFailure
  | .append a b => combine (fun x y => .ok (alg.compose x y)) (oldEager alg a) (oldEager alg b)
  | .interpolate _ _ _ | .accumulate _ _ _ => .ok alg.identity

theorem observed_witness : evaluate affine 200 witness = .ok ⟨3/2, 100⟩ := by decide +kernel

theorem resized_witness : evaluate affine 400 witness = .ok ⟨3/2, 200⟩ := by decide +kernel

theorem old_identity_counterexample : oldEager affine witness = .ok affine.identity ∧
    evaluate affine 200 witness ≠ .ok affine.identity := by decide +kernel

theorem old_interpolation_counterexample :
    oldEager affine (.interpolate (1/2) (.length 100 0) (.length 200 0)) = .ok affine.identity ∧
    evaluate affine 200 (.interpolate (1/2) (.length 100 0) (.length 200 0)) ≠ .ok affine.identity := by decide +kernel

theorem old_accumulation_counterexample :
    oldEager affine (percentageEndpoint 1) = .ok affine.identity ∧
    evaluate affine 200 (percentageEndpoint 1) ≠ .ok affine.identity := by decide +kernel

theorem prefix_does_not_hide_deferred :
    eager affine (transformList [.length 7 0, percentageEndpoint 1, .constant ⟨2, 0⟩]) =
      .error .unsupportedDeferred := by decide +kernel

theorem repaired_rejects_witness : eager affine witness = .error .unsupportedDeferred := by decide +kernel

theorem missing_context_is_not_invalid :
    partialEval affine (percentageEndpoint 1) = .error .needsContext ∧
    evaluate affine 200 (percentageEndpoint 1) = .ok ⟨1, 100⟩ ∧
    partialEval affine (.interpolate (1/2) (.constant ⟨0, 0⟩) (.constant ⟨1, 0⟩)) =
      .error .semanticFailure := by decide +kernel

theorem fixed_pixel_control :
    partialEval affine (.interpolate (1/2)
      (.accumulate 1 (.length 100 0) (.constant ⟨1, 0⟩))
      (.accumulate 1 (.length 100 0) (.constant ⟨2, 0⟩))) = .ok ⟨3/2, 100⟩ := by decide +kernel

theorem native_pixel_list_control :
    eager affine (transformList [.length 100 0, .constant ⟨2, 0⟩]) = .ok ⟨2, 100⟩ := by decide +kernel

theorem ordered_list_control :
    eager affine (transformList [.constant ⟨2, 0⟩, .length 100 0]) = .ok ⟨2, 200⟩ := by decide +kernel

#print axioms old_interpolation_counterexample
#print axioms old_accumulation_counterexample
#print axioms prefix_does_not_hide_deferred

#print axioms list_success_members
#print axioms list_failure_propagates
#print axioms deferred_denotation
#print axioms attempt_sound
#print axioms fallback_preserves_left
#print axioms fallback_preserves_right

#print axioms combine_success
#print axioms partial_sound
#print axioms eager_refines_partial
#print axioms eager_sound
#print axioms arbitrary_list_sound
#print axioms observed_witness
#print axioms resized_witness
#print axioms old_identity_counterexample
#print axioms repaired_rejects_witness
#print axioms missing_context_is_not_invalid
#print axioms fixed_pixel_control
#print axioms native_pixel_list_control
#print axioms ordered_list_control

end DeferredTransform
