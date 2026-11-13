Require Import Reals ZArith List Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import Target EntryAllocation WeightTarget InputTarget PrefixTarget ReverseTarget ConversionTarget.
Import ListNotations.
Module EntryAcquisition.
Open Scope Z_scope.
Definition Acquired32 (value : Z) : Prop := -2147483648 <= value <= 2147483647.
Definition SmallDomain (value : Z) : Prop := -576460752303423488 <= value <= 576460752303423488.
Record Line := { allocation : EntryAllocation.ArrayState; committedMBP : list Z; inner : Z; gap : Z }.
Definition LineAdmitted (elementBytes : nat) (line : Line) : Prop :=
  (32 <= elementBytes)%nat /\ EntryAllocation.Reachable elementBytes (allocation line) /\
  length (committedMBP line) = length (EntryAllocation.tokens (allocation line)) /\
  Forall Acquired32 (committedMBP line) /\ Acquired32 (inner line) /\ Acquired32 (gap line).
Definition mbpTotal (line : Line) := fold_left Z.add (committedMBP line) 0.
Definition initialSpace (line : Line) := inner line - (mbpTotal line + gap line).
Record Round := { used : list Z; items : list Item }.
Definition UsedSource (value : Z) (item : Item) : Prop :=
  Acquired32 value /\ (frozen item = false -> value = base (payload item)).
Definition RoundAdmitted (line : Line) (mode : bool) (round : Round) : Prop :=
  map itemId (items round) = EntryAllocation.tokens (allocation line) /\
  Forall2 UsedSource (used round) (items round) /\ Forall ItemValid (items round) /\
  Forall (fun item => frozen item = false -> growing (payload item) = mode) (items round).
Definition roundFree (line : Line) (round : Round) := fold_left Z.sub (used round) (initialSpace line).
Definition capture (original current : Z) := if Z.eq_dec original 0 then current else original.
Fixpoint firstNonzero (values : list Z) : Z :=
  match values with [] => 0 | value::tail => if Z.eq_dec value 0 then firstNonzero tail else value end.
Inductive History (line : Line) (mode : bool) : list Round -> Z -> Prop :=
| history_empty : History line mode [] 0
| history_step : forall rounds original round,
    History line mode rounds original -> RoundAdmitted line mode round ->
    History line mode (rounds++[round]) (capture original (roundFree line round)).
Record FactorResult := { factorTotal : R; factorRemaining : nat; factorVisited : nat }.
Fixpoint factorLoop (left : nat) (sum : R) (xs : list Item) : FactorResult :=
  match left,xs with
  | O,_ => {| factorTotal := sum; factorRemaining := O; factorVisited := O |}
  | S k,[] => {| factorTotal := sum; factorRemaining := S k; factorVisited := O |}
  | S k,item::tail =>
    let result := if frozen item then factorLoop (S k) sum tail
      else factorLoop k (WeightTarget.rn (sum + value32 (factor (payload item))))%R tail in
    {| factorTotal := factorTotal result; factorRemaining := factorRemaining result;
       factorVisited := S (factorVisited result) |}
  end.
Definition activeFactors (xs : list Item) : list R :=
  map (fun item => value32 (factor (payload item))) (filter (fun item => negb (frozen item)) xs).
Definition factorRun (xs : list Item) := factorLoop (activeCount xs) 0%R xs.
Definition adjustAvailable (current desired : Z) :=
  if Z.ltb 0 current then Z.min current desired else Z.max current desired.
Inductive Branch := NoSpace | NoWeight | Unadjusted | Adjusted.
Record Prepared := { originalAfter : Z; entryFree : Z; factorResult : R; selectedBranch : Branch }.
Definition prepare (line : Line) (original : Z) (round : Round) : Prepared :=
  let current := roundFree line round in
  if Z.eq_dec current 0 then {| originalAfter := original; entryFree := current;
    factorResult := 0%R; selectedBranch := NoSpace |}
  else let original' := capture original current in
    let factors := factorTotal (factorRun (items round)) in
    if Req_EM_T (total (run (items round))) 0 then
      {| originalAfter := original'; entryFree := current; factorResult := factors; selectedBranch := NoWeight |}
    else if Rlt_dec factors 1 then
      {| originalAfter := original'; entryFree := adjustAvailable current (integerDelta original' (Fraction factors));
        factorResult := factors; selectedBranch := Adjusted |}
    else {| originalAfter := original'; entryFree := current; factorResult := factors; selectedBranch := Unadjusted |}.
Definition enters (prepared : Prepared) : bool :=
  match selectedBranch prepared with NoSpace | NoWeight => false | _ => true end.
Definition execute (line : Line) (original : Z) (round : Round) : ReverseResult :=
  let prepared := prepare line original round in
  if enters prepared then reverseRun (items round) (entryFree prepared)
  else {| events := []; finalFree := entryFree prepared; reverseRemaining := O; examined := O |}.
End EntryAcquisition.
