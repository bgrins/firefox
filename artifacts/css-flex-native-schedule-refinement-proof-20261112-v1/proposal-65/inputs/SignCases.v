Require Import Reals ZArith List Flocq.IEEE754.Binary.
Require Import InputTarget EntryModel EntryCases SignModel.
Import ListNotations.
Module SignCases.
Import SignHistory.
Open Scope Z_scope.
Definition quarter32 : Float32 := Binary.B754_finite 24 128 false 8388608 (-25) eq_refl.
Definition zero32 : Float32 := Binary.B754_zero 24 128 false.
Definition seedOf (factor : Float32) (base minimum maximum : Z) (frozen : bool) (stored : R) : Seed :=
  {| seedId := 7%nat; seedFactor := factor; seedBase := base;
     seedMin := minimum; seedMax := maximum; seedFrozen := frozen; seedShare := stored |}.
Definition lineOf (mbp : list Z) (inner : Z) : EntryAcquisition.Line :=
  {| EntryAcquisition.allocation := EntryCases.twoAllocated;
     EntryAcquisition.committedMBP := mbp; EntryAcquisition.inner := inner; EntryAcquisition.gap := 0 |}.
Definition growLine := lineOf [-120;0] 180.
Definition growSeeds := [seedOf quarter32 0 0 120 false (-19)%R;
  seedOf EntryCases.half32 0 0 120 false 42%R].
Definition shrinkLine := lineOf [0;0] 180.
Definition shrinkSeeds := [seedOf EntryCases.half32 120 0 120 false (-19)%R;
  seedOf EntryCases.half32 120 0 120 false 42%R].
Definition zeroLine := lineOf [0;0] 240.
Definition noWeightLine := lineOf [0;0] 50.
Definition noWeightSeeds := [seedOf EntryCases.half32 0 0 100 false (-19)%R;
  seedOf zero32 100 0 100 true 42%R].
Definition frozenBadSeeds := [seedOf EntryCases.half32 100 0 100 false (-19)%R;
  seedOf (Binary.B754_infinity 24 128 false) (-1099511627776) 0 100 true 42%R].
Definition allFrozenSeeds := [seedOf zero32 10 0 100 true (-19)%R;
  seedOf zero32 20 0 100 true 42%R].
Definition first (line : EntryAcquisition.Line) (seeds : list Seed) :=
  pass line (mode line seeds) (length seeds) O (initial line seeds).
Definition second (line : EntryAcquisition.Line) (seeds : list Seed) :=
  pass line (mode line seeds) (length seeds) 1 (next (first line seeds)).
Definition huge : Z := 576460752303423487.
Definition nonrepresentableShare : R := (1 - / (2^100))%R.
End SignCases.
