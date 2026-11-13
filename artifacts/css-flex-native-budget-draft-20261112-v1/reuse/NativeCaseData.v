Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool SignCases EntryCases InputProof.
Import ListNotations.
Module NativeCases.
Import NativeSchedule.
Open Scope Z_scope.
Definition one32 := InputProof.one32.
Definition half32 := EntryCases.half32.
Definition quarter32 := SignCases.quarter32.
Definition three32 : Float32 := Binary.B754_finite 24 128 false 12582912 (-22) eq_refl.
Definition million32 : Float32 := Binary.B754_finite 24 128 false 16000000 (-4) eq_refl.
Definition inf32 : Float32 := Binary.B754_infinity 24 128 false.
Definition seedOf (f : Float32) (base lo hi : Z) (frozen : bool)
    (stale : NativeFloat.F64) (mbp : Z) : Seed :=
  {| identity := 7%nat; growFactor := f; shrinkFactor := f;
     baseSize := base; minimum := lo; maximum := hi; initiallyFrozen := frozen;
     initialShare := stale; initialMinFlag := frozen; initialMaxFlag := false;
     isStrut := false; measuredMBP := mbp; measuredOuter := Z.max lo (Z.min base hi)+mbp |}.
Definition allocated (n : nat) : EntryAllocation.ArrayState :=
  {| EntryAllocation.tokens := repeat 7%nat n;
     EntryAllocation.capacity := if Nat.leb n 1 then n else if Nat.leb n 3 then 3%nat else 7%nat |}.
Definition lineOf (seeds : list Seed) (inner : Z) : EntryAcquisition.Line :=
  {| EntryAcquisition.allocation := allocated (length seeds);
     EntryAcquisition.committedMBP := map measuredMBP seeds;
     EntryAcquisition.inner := inner; EntryAcquisition.gap := 0 |}.
Definition growSeeds := [seedOf quarter32 0 0 120 false NativeFloat.nan (-120);
  seedOf half32 0 0 120 false NativeFloat.infinity 0].
Definition shrinkSeeds := [seedOf half32 120 0 120 false NativeFloat.nan 0;
  seedOf half32 120 0 120 false NativeFloat.infinity 0].
Definition noWeightSeeds := [seedOf half32 0 0 100 false NativeFloat.infinity 0;
  seedOf inf32 100 0 100 true NativeFloat.nan 0].
Definition overflowSeeds := [seedOf one32 0 0 2147483647 false NativeFloat.nan (-2147483648);
  seedOf inf32 0 0 0 true NativeFloat.infinity 0].
Definition preferredSeeds := [seedOf one32 0 0 2147483647 false NativeFloat.nan 0].
Definition orderedSeeds := [seedOf one32 0 0 200 false NativeFloat.nan 0;
  seedOf inf32 0 0 0 true NativeFloat.nan 0;
  seedOf three32 0 0 200 false NativeFloat.infinity 0].
Definition allFrozenSeeds := [seedOf inf32 10 0 100 true NativeFloat.nan 0;
  seedOf inf32 20 0 100 true NativeFloat.infinity 0].
Definition clippingSeeds := [seedOf million32 60000 0 60000 false NativeFloat.nan 0;
  seedOf one32 1800000000 0 60000 false NativeFloat.infinity 0;
  seedOf one32 1800000000 0 60000 false NativeFloat.nan 0].
Definition nonfiniteSeeds := [seedOf inf32 0 0 200 false NativeFloat.nan 0;
  seedOf inf32 0 0 200 false NativeFloat.infinity 0].
Definition first (seeds : list Seed) (inner : Z) (info : bool) :=
  NativePass.step (NativeEntry.config (lineOf seeds inner) seeds)
    (NativeEntry.initial (lineOf seeds inner) seeds info).
Definition second (seeds : list Seed) (inner : Z) (info : bool) :=
  match first seeds inner info with None => None | Some p =>
    NativePass.step (NativeEntry.config (lineOf seeds inner) seeds) (NativePass.next p) end.
Definition mains (p : NativePass.Pass) := map main (rows (NativePass.next p)).
Definition deltas (p : NativePass.Pass) :=
  match reports (NativePass.next p) with None => [] | Some xs => map reportDelta xs end.
Definition flags (p : NativePass.Pass) := map (fun r => (minFlag r,maxFlag r)) (NativeClamp.clampedRows (NativePass.clamped p)).
Definition zeroLineFirst := first shrinkSeeds 240 true.
Definition growFirst := first growSeeds 180 true.
Definition growSecond := second growSeeds 180 true.
Definition shrinkFirst := first shrinkSeeds 180 true.
Definition noWeightFirst := first noWeightSeeds 50 true.
Definition overflowFirst := first overflowSeeds 2147483647 true.
Definition preferredFirst := first preferredSeeds 1500000000 true.
Definition orderedFirst := first orderedSeeds 150 true.
Definition nonfiniteFirst := first nonfiniteSeeds 150 true.
Definition clippingFirst := first clippingSeeds 60000 true.
Definition clippingSecond := second clippingSeeds 60000 true.
Definition allFrozenFirst := first allFrozenSeeds 100 true.
Definition lowerRawControl : Row := replaceMain
  (construct (seedOf one32 0 0 100 false NativeFloat.nan 0)) (-2147483649).
Definition frozenStrut :=
  {| identity := 8%nat; growFactor := inf32; shrinkFactor := inf32;
     baseSize := 0; minimum := 0; maximum := 0; initiallyFrozen := true;
     initialShare := NativeFloat.nan; initialMinFlag := false; initialMaxFlag := false;
     isStrut := true; measuredMBP := 0; measuredOuter := 0 |}.
Definition stagedOne := NativeGeneration.stage frozenStrut NativeGeneration.begin.
Definition committedOne := NativeGeneration.finishPending 0 stagedOne.
Definition stagedTwo := NativeGeneration.stage (hd frozenStrut growSeeds) committedOne.
Definition wrappedTwo := NativeGeneration.transfer stagedTwo.
Definition committedTwo := NativeGeneration.finishPending 0 wrappedTwo.
Definition correctionTotal (p : NativePass.Pass) :=
  match NativePass.reverse p with None => 0 | Some r => NativeReverse.violation r end.
Definition clampOnlyTotal (p : NativePass.Pass) :=
  fold_left Z.add (map NativeClamp.difference (NativeClamp.events (NativePass.clamped p))) 0.
Definition wrongSignCorrection (p : NativePass.Pass) := clampOnlyTotal p-correctionTotal p.
Definition missingOverflowFlags (p : NativePass.Pass) :=
  match NativePass.reverse p with None => [] | Some r =>
    map (fun e => let row := setFlags (NativeReverse.storedRow e) false false in
      fst (NativeClamp.one row)) (NativeReverse.events r) end.
Definition compactReports (p : NativePass.Pass) :=
  match NativePass.reverse p with None => None | Some r =>
    fold_left (fun out pair => updateReport (fst pair) (NativeReverse.delta (snd pair)) out)
      (combine (seq 0 (length (NativeReverse.events r))) (NativeReverse.events r))
      (Some (reportsFor (NativePass.resetRows (NativePass.acquisition (NativePass.prepared p))))) end.
Definition forwardWrong (seeds : list Seed) (inner : Z) :=
  let state := NativeEntry.initial (lineOf seeds inner) seeds true in
  match NativePass.prepare (NativeEntry.config (lineOf seeds inner) seeds) state with
  | None => None | Some p => match NativePass.producer p with None => None | Some prod =>
    NativeReverse.loop (NativeEntry.seedsMode (lineOf seeds inner) seeds)
      (NativeFloat.finite (NativeProducer.weightSum prod)) (NativeProducer.largest prod)
      (length seeds-frozenCount state)%nat (NativeProducer.ties prod) (NativePass.entryFree p) 0
      (reports state) (combine (seq 0 (length seeds)) (NativeProducer.producedRows prod)) end end.
Definition forceEarlyFallback (p : NativePass.Pass) := map freeze (rows (NativePass.next p)).
Definition gapSeed := seedOf one32 0 0 0 false NativeFloat.nan 0.
Definition feed (gap : Z) (g : NativeGeneration.Generation) (s : Seed) :=
  NativeGeneration.finishPending gap (NativeGeneration.stage s g).
Definition fiveGapGeneration := fold_left (feed 600000000) (repeat gapSeed 5) NativeGeneration.begin.
Definition overflowOuterSeed := seedOf one32 2 0 2 false NativeFloat.nan 2147483646.
End NativeCases.
