Require Import Reals ZArith List Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Target ConversionTarget DistributionTarget InputTarget BranchTarget.
Import ListNotations.
Open Scope R_scope.

Record Item := { itemId : nat; payload : WeightInput; frozen : bool; stored : R }.
Definition setStored (x : Item) (s : R) : Item :=
  {| itemId := itemId x; payload := payload x; frozen := frozen x; stored := s |}.
Fixpoint activeWeights (xs : list Item) : list R :=
  match xs with
  | [] => []
  | x :: tail => if frozen x then activeWeights tail
                 else sourceWeight (payload x) :: activeWeights tail
  end.
Definition activeCount (xs : list Item) : nat := length (activeWeights xs).
Definition ItemValid (x : Item) : Prop := frozen x = false -> InputValid (payload x).
Definition Admitted (xs : list Item) : Prop :=
  (Z.of_nat (length xs) <= countLimit)%Z /\ Forall ItemValid xs.
Definition shareAt (weight sum : R) : R :=
  if Req_EM_T weight 0 then 0 else WeightTarget.rn (weight / sum).
Record Result := { rows : list Item; remaining : nat; total : R; visited : nat }.
Fixpoint produce (left : nat) (sum : R) (xs : list Item) : Result :=
  match left, xs with
  | O, _ => {| rows := xs; remaining := O; total := sum; visited := O |}
  | S k, [] => {| rows := []; remaining := S k; total := sum; visited := O |}
  | S k, x :: tail =>
      if frozen x then
        let r := produce (S k) sum tail in
        {| rows := x :: rows r; remaining := remaining r; total := total r;
           visited := S (visited r) |}
      else
        let w := sourceWeight (payload x) in
        let next := WeightTarget.rn (sum + w) in
        let r := produce k next tail in
        {| rows := setStored x (shareAt w next) :: rows r;
           remaining := remaining r; total := total r; visited := S (visited r) |}
  end.
Definition run (xs : list Item) : Result := produce (activeCount xs) 0 xs.
Definition prefixShare (before : list Item) (x : Item) : R :=
  storedShare (activeWeights (before ++ [x])) (sourceWeight (payload x)).
Fixpoint specification (before xs : list Item) : list Item :=
  match xs with
  | [] => []
  | x :: tail =>
      (if frozen x then x else setStored x (prefixShare before x)) ::
      specification (before ++ [x]) tail
  end.
Definition identity (x : Item) := (itemId x, payload x, frozen x).
Definition shareChoice (s : R) : Choice :=
  if Req_EM_T s 1 then Whole else if Rlt_dec 0 s then Fraction s else Zero.
Definition producedDelta (free : Z) (x : Item) : Z := integerDelta free (shareChoice (stored x)).

Definition StopTarget : Prop := forall xs,
  remaining (run xs) = O /\ (visited (run xs) <= length xs)%nat /\
  Forall (fun x => frozen x = true) (skipn (visited (run xs)) xs) /\
  activeCount (firstn (visited (run xs)) xs) = activeCount xs.
Definition SpecificationTarget : Prop := forall xs, rows (run xs) = specification [] xs.
Definition PreservationTarget : Prop := forall xs,
  map identity (rows (run xs)) = map identity xs /\
  forall i x, nth_error xs i = Some x -> frozen x = true ->
    nth_error (rows (run xs)) i = Some x.
Definition PrefixTarget : Prop := forall before x after,
  frozen x = false ->
  nth_error (rows (run (before ++ x :: after))) (length before) =
    Some (setStored x (prefixShare before x)).
Definition SumTarget : Prop := forall xs,
  total (run xs) = WeightTarget.accumulate (activeWeights xs) 0.
Definition RangeTarget : Prop := forall xs i x y,
  Admitted xs -> nth_error xs i = Some x -> frozen x = false ->
  nth_error (rows (run xs)) i = Some y -> 0 <= stored y <= 1.
Definition DeltaTarget : Prop := forall xs i x y free,
  Admitted xs -> nth_error xs i = Some x -> frozen x = false ->
  nth_error (rows (run xs)) i = Some y ->
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  EnvelopeZ free (producedDelta free y) /\ Fits64 (producedDelta free y).
Definition BranchTarget : Prop :=
  (forall free x, stored x = 1 -> producedDelta free x = free) /\
  (forall free x, stored x = 0 -> producedDelta free x = 0%Z).
Definition FullStoredPrefixTarget : Prop := StopTarget /\ SpecificationTarget /\
  PreservationTarget /\ PrefixTarget /\ SumTarget /\ RangeTarget /\ DeltaTarget /\ BranchTarget.
