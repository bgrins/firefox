Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativeRefinementTarget.
Import NativeSchedule.
Open Scope Z_scope.
Definition FloatTarget : Prop :=
  (forall f, FactorInput f -> NativeFloat.finite (NativeFloat.promote f) = true /\
    NativeFloat.value (NativeFloat.promote f) = value32 f) /\
  (forall x z, NativeFloat.floorFinite x = Some z -> NativeFloat.finite x = true /\
    z = Raux.Zfloor (NativeFloat.value x)) /\
  (forall free share, ReverseTarget.FreeDomain free -> NativeFloat.finite share = true ->
    (0 <= NativeFloat.value share <= 1)%R ->
    NativeFloat.fractionDelta free share =
      Some (ReverseTarget.deltaAt free (NativeFloat.value share))).
Definition GenerationTarget : Prop :=
  (forall gap g, NativeGeneration.Reachable gap g -> NativeGeneration.pending g = None ->
    Forall (fun line => NativeGeneration.CountAgrees line /\ NativeGeneration.FieldsConstructed line)
      (NativeGeneration.completed g)) /\
  (forall inner gap info rs,
    NativeGeneration.resolverEntries inner gap info (NativeGeneration.Continuation rs) = []) /\
  (forall gap g s, NativeGeneration.Reachable gap g -> NativeGeneration.pending g = None ->
    NativeGeneration.countFrozen (NativeGeneration.current (NativeGeneration.stage s g)) =
    NativeGeneration.countFrozen (NativeGeneration.current g)) /\
  (forall g s, NativeGeneration.flatten (NativeGeneration.stage s g) =
    NativeGeneration.flatten g++[construct s]) /\
  (forall gap g s, NativeGeneration.Reachable gap g -> NativeGeneration.pending g = Some s ->
    (1 < length (NativeGeneration.items (NativeGeneration.current g)))%nat ->
    NativeGeneration.flatten (NativeGeneration.transfer g) = NativeGeneration.flatten g).
Definition AcquisitionTarget : Prop := forall bytes allocation inner gap info g line,
  NativeGeneration.Reachable gap g -> NativeGeneration.pending g = None ->
  In line (NativeGeneration.completed g) -> (32 <= bytes)%nat ->
  EntryAllocation.Reachable bytes allocation ->
  EntryAllocation.tokens allocation = map (fun r => identity (seed r)) (NativeGeneration.items line) ->
  EntryAcquisition.Acquired32 inner -> EntryAcquisition.Acquired32 gap -> 0 <= gap ->
  EntryAcquisition.Acquired32 (NativeGeneration.idealGaps gap line) ->
  Forall (fun r => NativeGeneration.AcquiredCoherent (seed r) /\
    SignHistory.SeedValid (projectedSeed (Z.ltb (NativeGeneration.totalOuter line) inner) (seed r)))
    (NativeGeneration.items line) ->
  let model := NativeGeneration.lineModel allocation inner gap line in
  let seeds := map seed (NativeGeneration.items line) in
  NativeEntry.Admitted bytes model seeds /\
  NativeGeneration.config inner gap line = NativeEntry.config model seeds /\
  initialize (NativePass.growing (NativeGeneration.config inner gap line)) info
    (NativeGeneration.items line) (NativeGeneration.countFrozen line) = NativeEntry.initial model seeds info /\
  (length seeds <= 134217727)%nat /\
  Forall NativeGeneration.TotalsFit (NativeGeneration.commitPrefixes gap NativeGeneration.emptyLine
    (NativeGeneration.items line)).
Definition InitialTarget : Prop := forall bytes line seeds info,
  NativeEntry.Admitted bytes line seeds ->
  NativeEntry.NativeInvariant line seeds info (NativeEntry.initial line seeds info) /\
  reports (NativeEntry.initial line seeds info) =
    (if info then Some (reportsFor (map construct seeds)) else None) /\
  original (NativeEntry.initial line seeds info) = None.
Definition StepTarget : Prop := forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.canStep (NativeEntry.config line seeds) state = true ->
  exists result, NativePass.step (NativeEntry.config line seeds) state = Some result /\
    projectedState (NativeEntry.seedsMode line seeds) (NativePass.next result) =
      SignHistory.next (SignHistory.pass line (NativeEntry.seedsMode line seeds)
        (length seeds) (iteration state) (projectedState (NativeEntry.seedsMode line seeds) state)) /\
    NativeEntry.NativeInvariant line seeds info (NativePass.next result).
Definition ProducerTarget : Prop := forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state = Some p ->
  NativePass.branch p <> NativePass.NonfiniteDistribution /\
  match NativePass.producer p with None => NativePass.branch p = NativePass.NoSpace
  | Some produced =>
    NativeProducer.remaining produced = O /\
    NativeFloat.finite (NativeProducer.weightSum produced) = true /\
    NativeFloat.finite (NativeProducer.factorSum produced) = true /\
    map (fun r => SignHistory.asItem (NativeEntry.seedsMode line seeds)
      (projectedRow (NativeEntry.seedsMode line seeds) r)) (NativeProducer.producedRows produced) =
      PrefixTarget.rows (PrefixTarget.run (SignHistory.itemRows (NativeEntry.seedsMode line seeds)
        (projectedState (NativeEntry.seedsMode line seeds) state))) /\
    NativeFloat.value (NativeProducer.weightSum produced) =
      PrefixTarget.total (PrefixTarget.run (SignHistory.itemRows (NativeEntry.seedsMode line seeds)
        (projectedState (NativeEntry.seedsMode line seeds) state))) /\
    NativeFloat.value (NativeProducer.factorSum produced) =
      EntryAcquisition.factorTotal (EntryAcquisition.factorRun (SignHistory.itemRows
        (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)))
  end.
Definition EventMatches (native : NativeReverse.Event) (model : ReverseTarget.Event) :=
  NativeReverse.ordinal native = ReverseTarget.ordinal model /\
  NativeReverse.beforeFree native = ReverseTarget.beforeFree model /\
  NativeReverse.delta native = ReverseTarget.delta model /\
  NativeReverse.afterFree native = ReverseTarget.afterFree model /\
  NativeFloat.value (share (NativeReverse.oldRow native)) = ReverseTarget.usedShare model.
Definition ReverseTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  let model := SignHistory.distributed line (NativeEntry.seedsMode line seeds)
    (projectedState (NativeEntry.seedsMode line seeds) state) in
  match NativePass.reverse result with
  | None => ReverseTarget.events model = []
  | Some reversed => NativeReverse.left reversed = O /\
    Forall2 EventMatches (NativeReverse.events reversed) (ReverseTarget.events model) /\
    NativeReverse.finalFree reversed = ReverseTarget.finalFree model
  end.
Definition ProjectionTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  let grow := NativeEntry.seedsMode line seeds in
  let semantic := projectedState grow state in
  let distributed := SignHistory.distributed line grow semantic in
  NativeClamp.total (NativePass.clamped result) = SignHistory.violation distributed semantic /\
  forall i before after,
    nth_error (rows state) i = Some before ->
    nth_error (NativeClamp.clampedRows (NativePass.clamped result)) i = Some after ->
    main after = SignHistory.boundedAt distributed i (projectedRow grow before) /\
    (frozen before = false ->
      minFlag after = Z.ltb (SignHistory.rawAt distributed i (projectedRow grow before)) (main after) /\
      maxFlag after = Z.ltb (main after) (SignHistory.rawAt distributed i (projectedRow grow before))).
Definition BudgetTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  NativePass.FitsPass result /\ Fits64 (NativePass.spaceAvailable (NativeEntry.config line seeds)) /\
  Fits64 (EntryAcquisition.inner line) /\ Fits64 (EntryAcquisition.gap line) /\
  Fits64 (EntryAcquisition.mbpTotal line) /\ Fits64 (SignHistory.fixed line) /\
  Fits64 (NativeClamp.total (NativePass.clamped result)) /\
  (length seeds <= 134217727)%nat /\
  (match NativePass.reverse result with None => True | Some reversed =>
    SignHistory.sumZ (map (fun e => Z.abs (NativeReverse.delta e)) (NativeReverse.events reversed)) <=
      Z.abs (NativePass.entryFree (NativePass.prepared result)) /\
    Forall (fun e => Z.abs (NativeReverse.totalAfter e) <= Z.abs (NativePass.entryFree (NativePass.prepared result)))
      (NativeReverse.events reversed) end) /\
  Forall (fun e => Z.abs (NativeClamp.totalAfter e) <=
    Z.abs (NativePass.entryFree (NativePass.prepared result)) + Z.of_nat (length seeds)*4294967295)
      (NativeClamp.events (NativePass.clamped result)).
Definition PreservationTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  map seed (rows (NativePass.next result)) = map seed (rows state) /\
  (forall i before, nth_error (rows state) i = Some before -> frozen before = true ->
    nth_error (rows (NativePass.next result)) i = Some before) /\
  NativeEntry.ActiveFresh (NativePass.next result) /\
  (frozenCount state <= frozenCount (NativePass.next result))%nat.
Definition eventReportDelta (result : NativePass.Pass) (index : nat) (old : Z) :=
  match NativePass.reverse result with None => old | Some reversed =>
    fold_left (fun value e => if Nat.eqb index (NativeReverse.ordinal e)
      then NativeReverse.delta e else value) (NativeReverse.events reversed) old end.
Definition ReportTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  NativeEntry.ReportShape (NativePass.next result) /\
  reportMode (NativePass.next result) = reportMode state /\
  reports (NativePass.next result) =
    match NativePass.reverse result with None => reports state | Some reversed =>
      fold_left (fun out e => updateReport (NativeReverse.ordinal e) (NativeReverse.delta e) out)
        (NativeReverse.events reversed) (reports state) end /\
  (forall before after index old updated,
    reports state = Some before -> reports (NativePass.next result) = Some after ->
    nth_error before index = Some old -> nth_error after index = Some updated ->
    reportIdentity updated = reportIdentity old /\ reportBase updated = reportBase old /\
    reportDelta updated = eventReportDelta result index (reportDelta old)).
Definition CaptureTarget : Prop := forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  NativeEntry.OriginalAgrees (NativePass.next result) /\
  (NativePass.freeSpace (NativePass.acquisition (NativePass.prepared result)) = 0 ->
    original (NativePass.next result) = original state /\ NativePass.reverse result = None /\
    map share (NativePass.preparedRows (NativePass.prepared result)) = map share (rows state) /\
    Forall (fun r => frozen r = true) (rows (NativePass.next result))).
Definition HistoryTarget : Prop := forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativeEntry.NativeInvariant line seeds info state /\
  (active (rows state) <= length seeds-iteration state)%nat /\
  (forall result, NativePass.canStep (NativeEntry.config line seeds) state = true ->
    NativePass.step (NativeEntry.config line seeds) state = Some result ->
    NativeClamp.fallbackOrdinals (NativePass.selection result) = [] /\
    ((active (rows state) > 0)%nat ->
      (frozenCount state < frozenCount (NativePass.next result))%nat)).
Definition CompletionTarget : Prop := forall bytes line seeds info,
  NativeEntry.Admitted bytes line seeds ->
  exists result, NativePass.run (length seeds) (NativeEntry.config line seeds)
    (NativeEntry.initial line seeds info) = Some result /\
    frozenCount (NativePass.finalState result) = length seeds /\
    Forall (fun r => frozen r = true) (rows (NativePass.finalState result)) /\
    Forall NativePass.FitsPass (NativePass.passes result) /\
    Forall (fun p => NativeClamp.fallbackOrdinals (NativePass.selection p) = []) (NativePass.passes result).
End NativeRefinementTarget.
