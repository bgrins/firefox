Require Import Reals ZArith List.
Require Import InputTarget PrefixTarget ReverseTarget ShareTarget ConversionTarget Target EntryModel EntryTarget SignModel SignCases.
Import ListNotations.
Module NativeHistorySignTarget.
Import SignHistory.
Open Scope Z_scope.
Definition BetweenZero (bound value : Z) : Prop := Z.min bound 0 <= value <= Z.max bound 0.
Definition ContractionTarget : Prop := forall current stored,
  FreeDomain current -> ShareTarget.Representable stored -> (0 <= stored <= 1)%R ->
  BetweenZero current (deltaAt current stored) /\
  BetweenZero current (current - deltaAt current stored).
Definition StoredTarget : Prop := forall xs i original produced,
  Admitted xs -> nth_error xs i = Some original -> frozen original = false ->
  nth_error (PrefixTarget.rows (PrefixTarget.run xs)) i = Some produced ->
  ShareTarget.Representable (stored produced) /\ (0 <= stored produced <= 1)%R.
Definition ReverseTarget : Prop := forall xs current,
  Admitted xs -> FreeDomain current ->
  Forall (fun event => BetweenZero (beforeFree event) (delta event) /\
    BetweenZero current (beforeFree event) /\ BetweenZero current (afterFree event))
    (events (reverseRun xs current)) /\
  BetweenZero current (finalFree (reverseRun xs current)) /\
  ((PrefixTarget.total (PrefixTarget.run xs) <> 0)%R -> finalFree (reverseRun xs current) = 0).
Definition InitialTarget : Prop := forall e line seeds,
  InputValid e line seeds ->
  map seed (rows (initial line seeds)) = seeds /\
  Forall (ActiveBase (mode line seeds)) (rows (initial line seeds)) /\
  Balanced line (mode line seeds) (initial line seeds) /\
  Direction (mode line seeds) (free line (mode line seeds) (initial line seeds)).
Definition StructureTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  map seed (rows state) = seeds /\
  Forall (ActiveBase (mode line seeds)) (rows state) /\
  Forall (fun row => seedMin (seed row) <= main row <= seedMax (seed row)) (rows state) /\
  (iteration <= length seeds)%nat /\ (ActiveCount state <= length seeds - iteration)%nat /\
  (forall i row, nth_error (rows state) i = Some row -> isFrozen row = true ->
    nth_error (rows (next (pass line (mode line seeds) (length seeds) iteration state))) i = Some row).
Definition AcquisitionTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  EntryAcquisition.RoundAdmitted line (mode line seeds) (asRound (mode line seeds) state) /\
  exists previous,
    length previous = iteration /\
    EntryAcquisition.History line (mode line seeds) previous (saved state).
Definition BalanceTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  Balanced line (mode line seeds) state /\
  Direction (mode line seeds) (free line (mode line seeds) state) /\
  Direction (mode line seeds) (saved state).
Definition AdjustmentTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  EntryAcquisition.entryFree (prepared line (mode line seeds) state) =
    normativeAmount line (mode line seeds) state /\
  BetweenZero (free line (mode line seeds) state)
    (EntryAcquisition.entryFree (prepared line (mode line seeds) state)).
Definition CaptureTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  ((0 < iteration)%nat -> saved state = free line (mode line seeds) (initial line seeds)) /\
  (CanStep info seeds iteration state -> free line (mode line seeds) state = 0 ->
    ActiveCount (next (pass line (mode line seeds) (length seeds) iteration state)) = O).
Definition CompletionTarget : Prop := forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  (CanStep info seeds iteration state ->
    usedFallback (pass line (mode line seeds) (length seeds) iteration state) = false /\
    ((0 < ActiveCount state)%nat ->
      (ActiveCount (next (pass line (mode line seeds) (length seeds) iteration state)) < ActiveCount state)%nat)) /\
  (iteration = length seeds -> ActiveCount state = O).
Definition JointTarget : Prop :=
  InputValid 32 SignCases.growLine SignCases.growSeeds /\
  mode SignCases.growLine SignCases.growSeeds = true /\
  History SignCases.growLine SignCases.growSeeds false 2
    (next (SignCases.second SignCases.growLine SignCases.growSeeds)) /\
  totalViolation (SignCases.first SignCases.growLine SignCases.growSeeds) = -30 /\
  map main (rows (next (SignCases.first SignCases.growLine SignCases.growSeeds))) = [75;120] /\
  map isFrozen (rows (next (SignCases.first SignCases.growLine SignCases.growSeeds))) = [false;true] /\
  free SignCases.growLine true (next (SignCases.first SignCases.growLine SignCases.growSeeds)) = 180 /\
  saved (next (SignCases.first SignCases.growLine SignCases.growSeeds)) = 300 /\
  map main (rows (next (SignCases.second SignCases.growLine SignCases.growSeeds))) = [75;120] /\
  ActiveCount (next (SignCases.second SignCases.growLine SignCases.growSeeds)) = O /\
  InputValid 32 SignCases.shrinkLine SignCases.shrinkSeeds /\
  mode SignCases.shrinkLine SignCases.shrinkSeeds = false /\
  History SignCases.shrinkLine SignCases.shrinkSeeds false 1
    (next (SignCases.first SignCases.shrinkLine SignCases.shrinkSeeds)) /\
  map main (rows (next (SignCases.first SignCases.shrinkLine SignCases.shrinkSeeds))) = [90;90] /\
  InputValid 32 SignCases.zeroLine SignCases.shrinkSeeds /\
  EntryAcquisition.selectedBranch (prepared SignCases.zeroLine false
    (initial SignCases.zeroLine SignCases.shrinkSeeds)) = EntryAcquisition.NoSpace /\
  ActiveCount (next (SignCases.first SignCases.zeroLine SignCases.shrinkSeeds)) = O /\
  InputValid 32 SignCases.noWeightLine SignCases.noWeightSeeds /\
  EntryAcquisition.selectedBranch (prepared SignCases.noWeightLine false
    (initial SignCases.noWeightLine SignCases.noWeightSeeds)) = EntryAcquisition.NoWeight /\
  map share (rows (next (SignCases.first SignCases.noWeightLine SignCases.noWeightSeeds))) = [0%R;42%R] /\
  InputValid 32 SignCases.noWeightLine SignCases.frozenBadSeeds /\
  History SignCases.noWeightLine SignCases.frozenBadSeeds false 1
    (next (SignCases.first SignCases.noWeightLine SignCases.frozenBadSeeds)) /\
  nth_error (rows (next (SignCases.first SignCases.noWeightLine SignCases.frozenBadSeeds))) 1 =
    nth_error (rows (initial SignCases.noWeightLine SignCases.frozenBadSeeds)) 1 /\
  InputValid 32 SignCases.noWeightLine SignCases.allFrozenSeeds /\
  History SignCases.noWeightLine SignCases.allFrozenSeeds true 1
    (next (SignCases.first SignCases.noWeightLine SignCases.allFrozenSeeds)) /\
  ~ CanStep false SignCases.allFrozenSeeds 0 (initial SignCases.noWeightLine SignCases.allFrozenSeeds).
Definition BoundaryTarget : Prop :=
  FreeDomain SignCases.huge /\
  deltaAt SignCases.huge 1 = SignCases.huge /\
  ConversionTarget.integerDelta SignCases.huge (Target.Fraction 1) = SignCases.huge + 1 /\
  (0 < SignCases.nonrepresentableShare < 1)%R /\
  ~ ShareTarget.Representable SignCases.nonrepresentableShare /\
  deltaAt SignCases.huge SignCases.nonrepresentableShare = SignCases.huge + 1.
Definition FullHistorySignTarget : Prop := ContractionTarget /\ StoredTarget /\ ReverseTarget /\
  InitialTarget /\ StructureTarget /\ AcquisitionTarget /\ BalanceTarget /\ AdjustmentTarget /\
  CaptureTarget /\ CompletionTarget /\ JointTarget /\ BoundaryTarget.
End NativeHistorySignTarget.
