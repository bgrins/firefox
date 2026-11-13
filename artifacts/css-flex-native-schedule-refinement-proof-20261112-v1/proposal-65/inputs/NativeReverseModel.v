Require Import NativeFloatModel NativeState NativeProducerModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativeReverse.
Import NativeSchedule NativeProducer.
Open Scope Z_scope.
Record Event := {
  ordinal : nat; beforeFree : Z; delta : Z; afterFree : Z;
  oldRow : Row; rawTarget : Z; storedRow : Row;
  correction : Z; totalBefore : Z; totalAfter : Z;
  largestBefore : nat; largestAfter : nat; finiteBranch : bool
}.
Record Result := {
  indexedRows : list (nat*Row); finalFree : Z; violation : Z;
  left : nat; visited : nat; largestLeft : nat;
  reportsAfter : option (list Report); events : list Event
}.
Definition deltaFor (grow finiteSum : bool) (largestWeight : NativeFloat.F64)
    (largestCount : nat) (free : Z) (r : Row) : option (Z*nat) :=
  if finiteSum then
    match NativeFloat.fractionDelta free (share r) with
    | Some d => Some (d,largestCount) | None => None end
  else if NativeFloat.equal (weight grow r) largestWeight then
    match NativeFloat.equally free largestCount with
    | Some d => Some (d,Nat.pred largestCount) | None => None end
  else Some (0,largestCount).
Fixpoint loop (grow finiteSum : bool) (largestWeight : NativeFloat.F64)
    (remaining largestCount : nat) (free total : Z)
    (reportRows : option (list Report)) (rs : list (nat*Row)) : option Result :=
  match remaining,rs with
  | O,_ => Some {| indexedRows := rs; finalFree := free; violation := total;
      left := O; visited := O; largestLeft := largestCount;
      reportsAfter := reportRows; events := [] |}
  | S k,[] => Some {| indexedRows := []; finalFree := free; violation := total;
      left := S k; visited := O; largestLeft := largestCount;
      reportsAfter := reportRows; events := [] |}
  | S k,(i,r)::tail =>
      if frozen r then
        match loop grow finiteSum largestWeight (S k) largestCount free total reportRows tail with
        | None => None
        | Some result => Some {| indexedRows := (i,r)::indexedRows result;
          finalFree := finalFree result; violation := violation result;
          left := left result; visited := S (visited result); largestLeft := largestLeft result;
          reportsAfter := reportsAfter result; events := events result |} end
      else match deltaFor grow finiteSum largestWeight largestCount free r with
      | None => None
      | Some (d,nextLargest) =>
        let raw := main r+d in
        let stored := project32 raw in
        let updated := setFlags (replaceMain r stored)
          (minFlag r || Z.ltb raw (-2147483648))
          (maxFlag r || Z.ltb 2147483647 raw) in
        let correction := stored-raw in
        match loop grow finiteSum largestWeight k nextLargest (free-d) (total+correction)
            (updateReport i d reportRows) tail with
        | None => None
        | Some result => Some {| indexedRows := (i,updated)::indexedRows result;
          finalFree := finalFree result; violation := violation result;
          left := left result; visited := S (visited result); largestLeft := largestLeft result;
          reportsAfter := reportsAfter result;
          events := {| ordinal := i; beforeFree := free; delta := d; afterFree := free-d;
            oldRow := r; rawTarget := raw; storedRow := updated; correction := correction;
            totalBefore := total; totalAfter := total+correction;
            largestBefore := largestCount; largestAfter := nextLargest; finiteBranch := finiteSum |}
            :: events result |} end
      end
  end.
Definition run (grow : bool) (p : Produced) (count : nat) (free : Z)
    (reportRows : option (list Report)) :=
  loop grow (NativeFloat.finite (weightSum p)) (largest p)
    (length (producedRows p)-count)%nat (ties p) free 0 reportRows
    (rev (combine (seq 0 (length (producedRows p))) (producedRows p))).
Definition restored (result : Result) := map snd (rev (indexedRows result)).
Definition FitsEvent (e : Event) :=
  Forall Fits64 [beforeFree e; delta e; afterFree e; main (oldRow e);
    rawTarget e; main (storedRow e); correction e; totalBefore e; totalAfter e].
End NativeReverse.
