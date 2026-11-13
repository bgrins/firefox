Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool EntryAllocation EntryModel.
Import ListNotations.
Module NativeGeneration.
Import NativeSchedule.
Open Scope Z_scope.
Record Line := { items : list Row; countFrozen : nat; countNoncollapsed : nat;
  totalMBP : Z; totalOuter : Z }.
Definition emptyLine : Line := {| items := []; countFrozen := O; countNoncollapsed := O;
  totalMBP := 0; totalOuter := 0 |}.
Definition appendPending (s : Seed) (line : Line) : Line :=
  {| items := items line++[construct s]; countFrozen := countFrozen line;
     countNoncollapsed := countNoncollapsed line; totalMBP := totalMBP line; totalOuter := totalOuter line |}.
Definition withoutLast (line : Line) : Line :=
  {| items := firstn (Nat.pred (length (items line))) (items line);
     countFrozen := countFrozen line; countNoncollapsed := countNoncollapsed line;
     totalMBP := totalMBP line; totalOuter := totalOuter line |}.
Definition commit (gap : Z) (line : Line) : Line :=
  match rev (items line) with
  | [] => line
  | r::_ =>
    let noncollapsed := negb (isStrut (seed r)) in
    {| items := items line;
       countFrozen := if frozen r then S (countFrozen line) else countFrozen line;
       countNoncollapsed := if noncollapsed then S (countNoncollapsed line) else countNoncollapsed line;
       totalMBP := totalMBP line+measuredMBP (seed r);
       totalOuter := (totalOuter line+
         (if noncollapsed && negb (Nat.eqb (countNoncollapsed line) O) then gap else 0))+
         measuredOuter (seed r) |}
  end.
Record Generation := { finished : list Line; current : Line; pending : option Seed }.
Definition begin : Generation := {| finished := []; current := emptyLine; pending := None |}.
Definition stage (s : Seed) (g : Generation) : Generation :=
  {| finished := finished g; current := appendPending s (current g); pending := Some s |}.
Definition transfer (g : Generation) : Generation :=
  match pending g with None => g | Some s =>
    {| finished := finished g++[withoutLast (current g)];
       current := appendPending s emptyLine; pending := Some s |} end.
Definition finishPending (gap : Z) (g : Generation) : Generation :=
  {| finished := finished g; current := commit gap (current g); pending := None |}.
Inductive Reachable (gap : Z) : Generation -> Prop :=
| generated_begin : Reachable gap begin
| generated_stage : forall g s, Reachable gap g -> pending g = None -> Reachable gap (stage s g)
| generated_transfer : forall g s, Reachable gap g -> pending g = Some s ->
    (1 < length (items (current g)))%nat -> Reachable gap (transfer g)
| generated_commit : forall g s, Reachable gap g -> pending g = Some s -> Reachable gap (finishPending gap g)
| generated_restart : forall g, Reachable gap g -> Reachable gap begin.
Definition completed (g : Generation) := finished g++[current g].
Definition restart (_ : Generation) := begin.
Definition signed32 (z : Z) := let u := Z.modulo z 4294967296 in
  if Z.ltb u 2147483648 then u else u-4294967296.
Definition idealGaps (gap : Z) (line : Line) := Z.of_nat (Nat.pred (countNoncollapsed line))*gap.
Definition capturedGaps (gap : Z) (line : Line) := signed32 (idealGaps gap line).
Definition config (inner gap : Z) (line : Line) : NativePass.Config :=
  {| NativePass.spaceAvailable := inner-(totalMBP line+capturedGaps gap line);
     NativePass.growing := Z.ltb (totalOuter line) inner; NativePass.itemLimit := length (items line) |}.
Inductive Route := Fresh (g : Generation) | Continuation (rs : list Row).
Definition resolverEntries (inner gap : Z) (info : bool) (route : Route) : list (NativePass.Config*State) :=
  match route with
  | Continuation _ => []
  | Fresh g => match pending g with Some _ => [] | None =>
    map (fun line => (config inner gap line,
      initialize (NativePass.growing (config inner gap line)) info (items line) (countFrozen line))) (completed g) end
  end.
Definition CountAgrees (line : Line) :=
  countFrozen line = length (filter frozen (items line)) /\
  countNoncollapsed line = length (filter (fun r => negb (isStrut (seed r))) (items line)).
Definition FieldsConstructed (line : Line) := items line = map (fun r => construct (seed r)) (items line).
Definition AcquiredCoherent (s : Seed) :=
  measuredOuter s = clamp s (baseSize s)+measuredMBP s /\
  EntryAcquisition.Acquired32 (measuredMBP s) /\ EntryAcquisition.Acquired32 (measuredOuter s) /\
  (isStrut s = true -> initiallyFrozen s = true /\ clamp s (baseSize s) = 0 /\ measuredMBP s = 0).
Definition lineModel (allocation : EntryAllocation.ArrayState) (inner gap : Z) (line : Line) : EntryAcquisition.Line :=
  {| EntryAcquisition.allocation := allocation;
     EntryAcquisition.committedMBP := map (fun r => measuredMBP (seed r)) (items line);
     EntryAcquisition.inner := inner; EntryAcquisition.gap := capturedGaps gap line |}.
Fixpoint commitPrefixes (gap : Z) (line : Line) (rs : list Row) : list Line :=
  match rs with [] => [] | r::tail =>
    let next := commit gap (appendPending (seed r) line) in
    next::commitPrefixes gap next tail end.
Definition TotalsFit (line : Line) := Fits64 (totalMBP line) /\ Fits64 (totalOuter line).
Definition flatten (g : Generation) := concat (map items (completed g)).
End NativeGeneration.
