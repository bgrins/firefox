Require Import Reals ZArith List.
Require Import Target EntryAllocation EntryModel EntryCases WeightTarget InputTarget PrefixTarget ReverseTarget ConversionTarget.
Import ListNotations.
Module InitialEntryTarget.
Import EntryAcquisition.
Open Scope Z_scope.
Definition AllocationTarget : Prop := forall elementBytes state,
  (32 <= elementBytes)%nat -> EntryAllocation.Reachable elementBytes state ->
  (length (EntryAllocation.tokens state) <= EntryAllocation.capacity state)%nat /\
  (EntryAllocation.capacity state < 2^31)%nat /\
  (EntryAllocation.capacity state * elementBytes < 2^32)%nat /\
  (length (EntryAllocation.tokens state) <= 134217727)%nat.
Definition TransferTarget : Prop :=
  (forall e a b a' b', (32<=e)%nat -> EntryAllocation.Reachable e a -> EntryAllocation.Reachable e b ->
    EntryAllocation.Move a b a' b' -> EntryAllocation.Reachable e a' /\ EntryAllocation.Reachable e b') /\
  (forall e xs state, (32<=e)%nat -> EntryAllocation.Reconstruction e xs state ->
    EntryAllocation.Reachable e state /\ EntryAllocation.tokens state = xs).
Definition AcquisitionTarget : Prop := forall e line mode round,
  LineAdmitted e line -> RoundAdmitted line mode round ->
  (forall k, Z.abs (fold_left Z.add (firstn k (committedMBP line)) 0) <= 288230374004228096) /\
  Z.abs (mbpTotal line + gap line) <= 288230376151711744 /\
  Z.abs (initialSpace line) <= 288230378299195392 /\
  Fits64 (mbpTotal line) /\ Fits64 (mbpTotal line+gap line) /\ Fits64 (initialSpace line) /\
  (forall k, SmallDomain (fold_left Z.sub (firstn k (used round)) (initialSpace line)) /\
    Fits64 (fold_left Z.sub (firstn k (used round)) (initialSpace line))) /\
  roundFree line round = inner line - (fold_right Z.add 0 (committedMBP line)+gap line) -
    fold_right Z.add 0 (used round).
Definition CaptureTarget : Prop := forall e line mode rounds original,
  LineAdmitted e line -> History line mode rounds original ->
  SmallDomain original /\ original = firstNonzero (map (roundFree line) rounds) /\
  (original <> 0 -> exists before round after,
    rounds = before++round::after /\ Forall (fun r => roundFree line r=0) before /\ roundFree line round=original).
Definition FactorTarget : Prop := forall e line mode round,
  LineAdmitted e line -> RoundAdmitted line mode round ->
  factorRemaining (factorRun (items round)) = O /\
  (factorVisited (factorRun (items round)) <= length (items round))%nat /\
  factorTotal (factorRun (items round)) = WeightTarget.accumulate (activeFactors (items round)) 0%R /\
  (0 <= factorTotal (factorRun (items round)) <= sumLimit)%R /\
  (forall k, (0 <= WeightTarget.accumulate (firstn k (activeFactors (items round))) 0 <= sumLimit)%R) /\
  Admitted (items round).
Definition AdjustmentTarget : Prop := forall current original factors,
  SmallDomain current -> SmallDomain original -> (0<=factors<1)%R ->
  SmallDomain (integerDelta original (Fraction factors)) /\
  SmallDomain (adjustAvailable current (integerDelta original (Fraction factors))) /\
  Fits64 (adjustAvailable current (integerDelta original (Fraction factors))).
Definition EntryTarget : Prop := forall e line mode rounds original round,
  LineAdmitted e line -> History line mode rounds original -> RoundAdmitted line mode round ->
  SmallDomain (originalAfter (prepare line original round)) /\
  SmallDomain (entryFree (prepare line original round)) /\
  FreeDomain (entryFree (prepare line original round)) /\ Fits64 (entryFree (prepare line original round)) /\
  Admitted (items round).
Definition CompositionTarget : Prop := forall e line mode rounds original round,
  LineAdmitted e line -> History line mode rounds original -> RoundAdmitted line mode round ->
  let prepared := prepare line original round in let result := execute line original round in
  Forall BoundEvent (events result) /\ FreeDomain (finalFree result) /\ Fits64 (finalFree result) /\
  Chained (entryFree prepared) (events result) (finalFree result) /\
  finalFree result = entryFree prepared - eventSum (events result) /\
  reverseRemaining result = O /\
  map ordinal (events result) = (if enters prepared then rev (activePositions (items round)) else []) /\
  length (events result) = (if enters prepared then activeCount (items round) else O).
Definition BranchTarget : Prop :=
  (forall line original round, roundFree line round=0 ->
    selectedBranch (prepare line original round)=NoSpace /\ originalAfter (prepare line original round)=original /\
    events (execute line original round)=[] /\ finalFree (execute line original round)=0) /\
  (forall line original round, roundFree line round<>0 -> (total (run (items round))=0)%R ->
    selectedBranch (prepare line original round)=NoWeight /\
    originalAfter (prepare line original round)=capture original (roundFree line round) /\
    events (execute line original round)=[] /\ finalFree (execute line original round)=roundFree line round) /\
  (forall line original round, roundFree line round<>0 -> (total (run (items round))<>0)%R ->
    (factorTotal (factorRun (items round))<1)%R -> selectedBranch (prepare line original round)=Adjusted /\
    entryFree (prepare line original round)=adjustAvailable (roundFree line round)
      (integerDelta (capture original (roundFree line round)) (Fraction (factorTotal (factorRun (items round)))))) /\
  (forall line original round, roundFree line round<>0 -> (total (run (items round))<>0)%R ->
    (1<=factorTotal (factorRun (items round)))%R -> selectedBranch (prepare line original round)=Unadjusted /\
    entryFree (prepare line original round)=roundFree line round).
Definition JointTarget : Prop :=
  EntryAllocation.Reachable 32 EntryCases.twoAllocated /\
  EntryAllocation.capacity EntryCases.twoAllocated=3%nat /\
  LineAdmitted 32 EntryCases.cancellationLine /\ LineAdmitted 32 EntryCases.negativeLine /\
  (forall mode,
    RoundAdmitted EntryCases.cancellationLine mode (EntryCases.zeroRound mode) /\
    RoundAdmitted EntryCases.cancellationLine mode (EntryCases.positiveRound mode) /\
    RoundAdmitted EntryCases.cancellationLine mode (EntryCases.flippedRound mode) /\
    History EntryCases.cancellationLine mode [EntryCases.zeroRound mode] 0 /\
    History EntryCases.cancellationLine mode [EntryCases.zeroRound mode;EntryCases.positiveRound mode] 100 /\
    selectedBranch (prepare EntryCases.cancellationLine 0 (EntryCases.zeroRound mode))=NoSpace /\
    selectedBranch (prepare EntryCases.cancellationLine 0 (EntryCases.positiveRound mode))=Adjusted /\
    entryFree (prepare EntryCases.cancellationLine 0 (EntryCases.positiveRound mode))=50 /\
    entryFree (prepare EntryCases.cancellationLine 100 (EntryCases.flippedRound mode))=50 /\
    length (events (execute EntryCases.cancellationLine 100 (EntryCases.flippedRound mode)))=1%nat /\
    finalFree (execute EntryCases.cancellationLine 100 (EntryCases.flippedRound mode))=0 /\
    RoundAdmitted EntryCases.negativeLine mode (EntryCases.negativeRound mode) /\
    RoundAdmitted EntryCases.negativeLine mode (EntryCases.positiveFlip mode) /\
    History EntryCases.negativeLine mode [EntryCases.negativeRound mode] (-200) /\
    entryFree (prepare EntryCases.negativeLine (-200) (EntryCases.positiveFlip mode))=(-100) /\
    RoundAdmitted EntryCases.cancellationLine mode (EntryCases.fullRound mode) /\
    selectedBranch (prepare EntryCases.cancellationLine 0 (EntryCases.fullRound mode))=Unadjusted /\
    entryFree (prepare EntryCases.cancellationLine 0 (EntryCases.fullRound mode))=100) /\
  (RoundAdmitted EntryCases.cancellationLine false EntryCases.noWeightRound /\
    selectedBranch (prepare EntryCases.cancellationLine 0 EntryCases.noWeightRound)=NoWeight /\
    originalAfter (prepare EntryCases.cancellationLine 0 EntryCases.noWeightRound)=100 /\
    finalFree (execute EntryCases.cancellationLine 0 EntryCases.noWeightRound)=100).
Definition BoundaryTarget : Prop :=
  EntryAllocation.grownBytes 32 1 2=128%nat /\
  ((EntryAllocation.grownBytes 32 1 2-8)/32=3)%nat /\
  firstNonzero [0;0;-7;9]=(-7) /\
  adjustAvailable 1 (-100)=(-100) /\ adjustAvailable (-1) 100=100 /\
  (Z.abs (adjustAvailable 1 (-100)) > Z.abs 1) /\
  (1073741825<=4294967295) /\ Acquired32 1073741824 /\
  ~ FreeDomain (-(1073741825*1073741824)) /\
  ~ FreeDomain (1073741825*1073741824) /\
  (1073741825>134217727).
Definition FullEntryTarget : Prop := AllocationTarget /\ TransferTarget /\ AcquisitionTarget /\
  CaptureTarget /\ FactorTarget /\ AdjustmentTarget /\ EntryTarget /\ CompositionTarget /\
  BranchTarget /\ JointTarget /\ BoundaryTarget.
End InitialEntryTarget.
