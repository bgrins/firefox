Require Import Reals ZArith List Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Target ConversionTarget InputTarget PrefixTarget.
Import ListNotations.
Open Scope R_scope.

Definition FreeDomain (free : Z) : Prop :=
  (-1152921504606846976 <= free <= 1152921504606846976)%Z.
Definition deltaAt (free : Z) (share : R) : Z := integerDelta free (shareChoice share).
Definition positioned (xs : list Item) : list (nat * Item) := combine (seq 0 (length xs)) xs.
Definition activePositions (xs : list Item) : list nat :=
  map fst (filter (fun p => negb (frozen (snd p))) (positioned xs)).
Record Event := {
  ordinal : nat;
  usedShare : R;
  beforeFree : Z;
  delta : Z;
  afterFree : Z
}.
Record ReverseResult := {
  events : list Event;
  finalFree : Z;
  reverseRemaining : nat;
  examined : nat
}.
Fixpoint reverseLoop (left : nat) (free : Z) (xs : list (nat * Item)) : ReverseResult :=
  match left, xs with
  | O, _ => {| events := []; finalFree := free; reverseRemaining := O; examined := O |}
  | S k, [] => {| events := []; finalFree := free; reverseRemaining := S k; examined := O |}
  | S k, (i, x) :: tail =>
      if frozen x then
        let r := reverseLoop (S k) free tail in
        {| events := events r; finalFree := finalFree r;
           reverseRemaining := reverseRemaining r; examined := S (examined r) |}
      else
        let d := producedDelta free x in
        let next := (free - d)%Z in
        let r := reverseLoop k next tail in
        {| events := {| ordinal := i; usedShare := stored x; beforeFree := free;
                        delta := d; afterFree := next |} :: events r;
           finalFree := finalFree r; reverseRemaining := reverseRemaining r;
           examined := S (examined r) |}
  end.
Definition reverseRun (xs : list Item) (free : Z) : ReverseResult :=
  let p := run xs in
  if Req_EM_T (total p) 0 then
    {| events := []; finalFree := free; reverseRemaining := O; examined := O |}
  else reverseLoop (activeCount xs) free (rev (positioned (rows p))).
Fixpoint Chained (start : Z) (es : list Event) (finish : Z) : Prop :=
  match es with
  | [] => finish = start
  | e :: tail => beforeFree e = start /\
      afterFree e = (beforeFree e - delta e)%Z /\ Chained (afterFree e) tail finish
  end.
Definition BoundEvent (e : Event) : Prop :=
  FreeDomain (beforeFree e) /\ FreeDomain (afterFree e) /\
  EnvelopeZ (beforeFree e) (delta e) /\ Fits64 (delta e) /\ Fits64 (afterFree e).
Definition EventBoundTo (xs : list Item) (e : Event) : Prop :=
  exists before x after y,
    xs = before ++ x :: after /\ ordinal e = length before /\ frozen x = false /\
    nth_error (rows (run xs)) (ordinal e) = Some y /\
    usedShare e = stored y /\ usedShare e = prefixShare before x /\
    delta e = producedDelta (beforeFree e) y /\
    afterFree e = (beforeFree e - delta e)%Z.
Definition eventSum (es : list Event) : Z := fold_right Z.add 0%Z (map delta es).

Definition SignTarget : Prop := forall free share,
  0 <= share <= 1 ->
  ((0 <= free)%Z -> (0 <= deltaAt free share)%Z) /\
  ((free <= 0)%Z -> (deltaAt free share <= 0)%Z).
Definition RemainderTarget : Prop := forall free share,
  FreeDomain free -> 0 <= share <= 1 ->
  (Z.min free (-1048576) <= free - deltaAt free share <= Z.max free 1048576)%Z /\
  FreeDomain (free - deltaAt free share)%Z /\
  Fits64 (deltaAt free share) /\ Fits64 (free - deltaAt free share)%Z.
Definition ReverseCountTarget : Prop := forall xs free,
  reverseRemaining (reverseRun xs free) = O /\
  (examined (reverseRun xs free) <= length xs)%nat /\
  length (events (reverseRun xs free)) =
    (if Req_EM_T (total (run xs)) 0 then O else activeCount xs).
Definition ReverseOrderTarget : Prop := forall xs free,
  map ordinal (events (reverseRun xs free)) =
    (if Req_EM_T (total (run xs)) 0 then [] else rev (activePositions xs)).
Definition EventBindingTarget : Prop := forall xs free,
  Forall (EventBoundTo xs) (events (reverseRun xs free)).
Definition TraceTarget : Prop := forall xs free,
  Chained free (events (reverseRun xs free)) (finalFree (reverseRun xs free)).
Definition ReverseSafetyTarget : Prop := forall xs free,
  Admitted xs -> FreeDomain free ->
  Forall BoundEvent (events (reverseRun xs free)) /\
  FreeDomain (finalFree (reverseRun xs free)) /\ Fits64 (finalFree (reverseRun xs free)).
Definition ConservationTarget : Prop := forall xs free,
  finalFree (reverseRun xs free) = (free - eventSum (events (reverseRun xs free)))%Z.
Definition ReverseBranchesTarget : Prop :=
  (forall xs free, total (run xs) = 0 ->
    events (reverseRun xs free) = [] /\ finalFree (reverseRun xs free) = free) /\
  (forall free, deltaAt free 1 = free /\ deltaAt free 0 = 0%Z).
Definition ReverseJointTarget : Prop := exists xs,
  Admitted xs /\ activeWeights xs = [1;3] /\
  map itemId xs = [7%nat;7%nat;7%nat;7%nat] /\
  (exists x, In x xs /\ frozen x = true /\ ~ InputValid (payload x)) /\
  total (run xs) <> 0 /\
  length (events (reverseRun xs 150)) = 2%nat /\
  length (events (reverseRun xs (-150))) = 2%nat.
Definition FullReverseTarget : Prop := SignTarget /\ RemainderTarget /\
  ReverseCountTarget /\ ReverseOrderTarget /\ EventBindingTarget /\ TraceTarget /\
  ReverseSafetyTarget /\ ConservationTarget /\ ReverseBranchesTarget /\ ReverseJointTarget.
