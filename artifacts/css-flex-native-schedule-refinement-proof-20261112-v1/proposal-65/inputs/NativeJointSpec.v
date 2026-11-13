Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativeJointTarget.
Import NativeSchedule NativeCases.
Open Scope Z_scope.
Definition AdmittedCase (seeds : list Seed) (inner : Z) := NativeEntry.Admitted 32 (lineOf seeds inner) seeds.
Definition FirstHistory (seeds : list Seed) (inner : Z) (p : NativePass.Pass) :=
  first seeds inner true = Some p /\
  NativePass.canStep (NativeEntry.config (lineOf seeds inner) seeds)
    (NativeEntry.initial (lineOf seeds inner) seeds true) = true /\
  NativeEntry.ModelHistory (lineOf seeds inner) seeds true (NativePass.next p).
Definition SecondHistory (seeds : list Seed) (inner : Z) (p q : NativePass.Pass) :=
  FirstHistory seeds inner p /\ second seeds inner true = Some q /\
  NativePass.canStep (NativeEntry.config (lineOf seeds inner) seeds) (NativePass.next p) = true /\
  NativeEntry.ModelHistory (lineOf seeds inner) seeds true (NativePass.next q).
Definition JointTarget : Prop :=
  (AdmittedCase growSeeds 180 /\ exists p q,
    SecondHistory growSeeds 180 p q /\ mains p = [75;120] /\ mains q = [75;120] /\
    frozenCount (NativePass.next p) = 1%nat /\ frozenCount (NativePass.next q) = 2%nat /\
    original (NativePass.next p) = Some 300 /\ original (NativePass.next q) = Some 300 /\
    NativePass.entryFree (NativePass.prepared q) = 75 /\ deltas q = [75;150]) /\
  (AdmittedCase shrinkSeeds 180 /\ exists p, FirstHistory shrinkSeeds 180 p /\ mains p = [90;90]) /\
  (AdmittedCase shrinkSeeds 240 /\ exists p, FirstHistory shrinkSeeds 240 p /\
    NativePass.branch (NativePass.prepared p) = NativePass.NoSpace /\
    NativePass.reverse p = None /\ mains p = [120;120] /\ original (NativePass.next p) = None) /\
  (AdmittedCase noWeightSeeds 50 /\ exists p, FirstHistory noWeightSeeds 50 p /\
    NativePass.branch (NativePass.prepared p) = NativePass.NoWeight /\ mains p = [0;100] /\
    map share (rows (NativePass.next p)) = [NativeFloat.zero;NativeFloat.nan]) /\
  (AdmittedCase overflowSeeds 2147483647 /\ exists p, FirstHistory overflowSeeds 2147483647 p /\
    mains p = [2147483647;0] /\ NativeClamp.total (NativePass.clamped p) = -2147483648 /\
    flags p = [(false,true);(true,false)] /\ deltas p = [4294967295;0]) /\
  (AdmittedCase preferredSeeds 1500000000 /\ exists p, FirstHistory preferredSeeds 1500000000 p /\
    mains p = [1500000000]) /\
  (AdmittedCase orderedSeeds 150 /\ exists p, FirstHistory orderedSeeds 150 p /\
    mains p = [37;0;113] /\ deltas p = [37;0;113]) /\
  (AdmittedCase clippingSeeds 60000 /\ exists p q, SecondHistory clippingSeeds 60000 p q /\
    mains p = [0;60000;60000] /\ mains q = [0;30000;30000] /\
    NativeClamp.total (NativePass.clamped p) = 60000 /\ clampOnlyTotal p < 0 /\
    frozenCount (NativePass.next p) = 1%nat /\ frozenCount (NativePass.next q) = 3%nat) /\
  (AdmittedCase allFrozenSeeds 100 /\ exists p, FirstHistory allFrozenSeeds 100 p /\
    mains p = [10;20] /\ deltas p = [0;0]) /\
  (AdmittedCase [] 0 /\ NativePass.canStep (NativeEntry.config (lineOf [] 0) [])
    (NativeEntry.initial (lineOf [] 0) [] true) = false /\
    reports (NativeEntry.initial (lineOf [] 0) [] true) = Some []) /\
  (NativePass.canStep (NativeEntry.config (lineOf allFrozenSeeds 100) allFrozenSeeds)
    (NativeEntry.initial (lineOf allFrozenSeeds 100) allFrozenSeeds false) = false).
Definition GenerationJointTarget : Prop :=
  NativeGeneration.Reachable 0 committedTwo /\ NativeGeneration.pending committedTwo = None /\
  map (fun line => map (fun r => identity (seed r)) (NativeGeneration.items line))
    (NativeGeneration.completed committedTwo) = [[8%nat];[7%nat]] /\
  NativeGeneration.countFrozen (NativeGeneration.current stagedOne) = O /\
  NativeGeneration.countFrozen (NativeGeneration.current committedOne) = 1%nat /\
  NativeGeneration.Reachable 0 (NativeGeneration.restart committedTwo) /\
  NativeGeneration.restart committedTwo = NativeGeneration.begin /\
  NativeGeneration.resolverEntries 0 0 true
    (NativeGeneration.Continuation (map construct allFrozenSeeds)) = [].
Definition NonfiniteTarget : Prop :=
  ~ AdmittedCase nonfiniteSeeds 150 /\
  exists p reversed, nonfiniteFirst = Some p /\ NativePass.reverse p = Some reversed /\
    NativePass.branch (NativePass.prepared p) = NativePass.NonfiniteDistribution /\
    mains p = [75;75] /\ deltas p = [75;75] /\
    map NativeReverse.finiteBranch (NativeReverse.events reversed) = [false;false] /\
    map NativeReverse.largestBefore (NativeReverse.events reversed) = [2%nat;1%nat] /\
    NativeReverse.largestLeft reversed = O /\
    map share (rows (NativePass.next p)) = [NativeFloat.nan;NativeFloat.infinity].
Definition BoundaryTarget : Prop :=
  NativeFloat.fractionDelta 576460752303423487 NativeFloat.one = Some 576460752303423487 /\
  NativeFloat.equally 576460752303423487 1 = Some 576460752303423488 /\
  NativeFloat.roundInteger NativeFloat.infinity = None /\
  NativeFloat.roundInteger NativeFloat.nan = None /\
  NativeFloat.equal NativeFloat.nan NativeFloat.nan = false /\
  NativeFloat.equal (@BinarySingleNaN.B754_zero 53 1024 true) NativeFloat.zero = true.
Definition ControlsTarget : Prop :=
  (exists p, overflowFirst = Some p /\ clampOnlyTotal p <> NativeClamp.total (NativePass.clamped p)) /\
  (exists p, overflowFirst = Some p /\ wrongSignCorrection p > 0 /\
    NativeClamp.total (NativePass.clamped p) < 0) /\
  (exists p, overflowFirst = Some p /\
    map maxFlag (missingOverflowFlags p) = [false] /\
    map maxFlag (NativeClamp.clampedRows (NativePass.clamped p)) = [true;false]) /\
  (exists p, preferredFirst = Some p /\ map (Z.min 1073741823) (mains p) <> mains p) /\
  (exists p wrong, orderedFirst = Some p /\ forwardWrong orderedSeeds 150 = Some wrong /\
    map (fun pair => main (snd pair)) (NativeReverse.indexedRows wrong) <> mains p) /\
  (exists p q, SecondHistory growSeeds 180 p q /\
    NativeFloat.scale 180 (NativeFloat.promote quarter32) = Some 45 /\
    NativePass.entryFree (NativePass.prepared q) = 75) /\
  (exists p, noWeightFirst = Some p /\
    map share (rows (NativePass.next p)) <> map initialShare noWeightSeeds) /\
  (exists p, orderedFirst = Some p /\ compactReports p <> reports (NativePass.next p)) /\
  (exists p, growFirst = Some p /\ forceEarlyFallback p <> rows (NativePass.next p)).
Definition AcquisitionBoundaryTarget : Prop :=
  EntryAcquisition.Acquired32 (measuredMBP overflowOuterSeed) /\
  ~ EntryAcquisition.Acquired32 (measuredOuter overflowOuterSeed) /\
  NativeGeneration.Reachable 600000000 fiveGapGeneration /\
  EntryAllocation.Reachable 32 (allocated 5) /\
  EntryAllocation.tokens (allocated 5) = map (fun r => identity (seed r))
    (NativeGeneration.items (NativeGeneration.current fiveGapGeneration)) /\
  NativeEntry.Admitted 32
    (NativeGeneration.lineModel (allocated 5) 100 600000000 (NativeGeneration.current fiveGapGeneration))
    (repeat gapSeed 5) /\
  ~ EntryAcquisition.Acquired32 (NativeGeneration.idealGaps 600000000 (NativeGeneration.current fiveGapGeneration)) /\
  NativeGeneration.idealGaps 600000000 (NativeGeneration.current fiveGapGeneration) = 2400000000 /\
  NativeGeneration.capturedGaps 600000000 (NativeGeneration.current fiveGapGeneration) = -1894967296 /\
  NativePass.growing (NativeGeneration.config 100 600000000 (NativeGeneration.current fiveGapGeneration)) = false /\
  NativeEntry.seedsMode
    (NativeGeneration.lineModel (allocated 5) 100 600000000 (NativeGeneration.current fiveGapGeneration))
    (repeat gapSeed 5) = true.
Definition FullRefinementTarget : Prop :=
  NativeRefinementTarget.FloatTarget /\ NativeRefinementTarget.GenerationTarget /\
  NativeRefinementTarget.AcquisitionTarget /\ NativeRefinementTarget.InitialTarget /\
  NativeRefinementTarget.StepTarget /\ NativeRefinementTarget.ProducerTarget /\
  NativeRefinementTarget.ReverseTarget /\ NativeRefinementTarget.ProjectionTarget /\
  NativeRefinementTarget.BudgetTarget /\ NativeRefinementTarget.PreservationTarget /\
  NativeRefinementTarget.ReportTarget /\ NativeRefinementTarget.CaptureTarget /\
  NativeRefinementTarget.HistoryTarget /\ NativeRefinementTarget.CompletionTarget /\
  JointTarget /\ GenerationJointTarget /\ NonfiniteTarget /\ BoundaryTarget /\ ControlsTarget /\ AcquisitionBoundaryTarget.
End NativeJointTarget.
