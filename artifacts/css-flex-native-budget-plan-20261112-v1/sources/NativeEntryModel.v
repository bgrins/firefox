Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool SignTarget.
Import ListNotations.
Module NativeEntry.
Import NativeSchedule.
Open Scope Z_scope.
Definition seedsMode (line : EntryAcquisition.Line) (seeds : list Seed) :=
  Z.ltb (SignHistory.fixed line+SignHistory.sumZ (map (fun s => clamp s (baseSize s)) seeds))
    (EntryAcquisition.inner line).
Definition modelSeeds (line : EntryAcquisition.Line) (seeds : list Seed) :=
  map (projectedSeed (seedsMode line seeds)) seeds.
Definition Admitted (elementBytes : nat) (line : EntryAcquisition.Line) (seeds : list Seed) :=
  SignHistory.InputValid elementBytes line (modelSeeds line seeds).
Definition config (line : EntryAcquisition.Line) (seeds : list Seed) : NativePass.Config :=
  {| NativePass.spaceAvailable := EntryAcquisition.initialSpace line;
     NativePass.growing := seedsMode line seeds; NativePass.itemLimit := length seeds |}.
Definition initial (line : EntryAcquisition.Line) (seeds : list Seed) (info : bool) :=
  let rs := map construct seeds in
  initialize (seedsMode line seeds) info rs (length (filter frozen rs)).
Definition ModelHistory (line : EntryAcquisition.Line) (seeds : list Seed) (info : bool) (state : State) :=
  NativePass.History (config line seeds) (initial line seeds info) state.
Definition OriginalAgrees (state : State) :=
  match original state with None => True | Some value => value <> 0 end.
Definition ActiveFresh (state : State) :=
  Forall (fun r => frozen r = false -> minFlag r = false /\ maxFlag r = false) (rows state).
Definition ReportShape (state : State) :=
  match reports state,reportMode state with
  | None,None => True
  | Some rs,Some _ => map reportIdentity rs = map (fun r => identity (seed r)) (rows state) /\
      map reportBase rs = map (fun r => baseSize (seed r)) (rows state)
  | _,_ => False end.
Definition NativeInvariant (line : EntryAcquisition.Line) (seeds : list Seed) (info : bool) (state : State) :=
  frozenCount state = length (filter frozen (rows state)) /\ ActiveFresh state /\
  OriginalAgrees state /\ ReportShape state /\
  reportMode state = (if info then Some (seedsMode line seeds) else None) /\
  map seed (rows state) = seeds /\
  SignHistory.History line (modelSeeds line seeds) info (iteration state)
    (projectedState (seedsMode line seeds) state).
End NativeEntry.
