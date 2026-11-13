Require Import Reals ZArith List Flocq.IEEE754.Binary.
Require Import EntryAllocation EntryModel InputTarget InputProof PrefixTarget PrefixControls.
Import ListNotations.
Module EntryCases.
Import EntryAcquisition.
Definition half32 : Float32 := Binary.B754_finite 24 128 false 8388608 (-24) eq_refl.
Definition activeHalf (mode : bool) : Item :=
  {| itemId := 7%nat; payload := {| factor := half32; base := 1%Z; growing := mode |};
     frozen := false; stored := (-19)%R |}.
Definition activeFull (mode : bool) : Item :=
  {| itemId := 7%nat; payload := {| factor := one32; base := 1%Z; growing := mode |};
     frozen := false; stored := (-19)%R |}.
Definition zeroWeight : Item :=
  {| itemId := 7%nat; payload := {| factor := half32; base := 0%Z; growing := false |};
     frozen := false; stored := (-19)%R |}.
Definition twoAllocated : EntryAllocation.ArrayState :=
  {| EntryAllocation.tokens := [7%nat;7%nat]; EntryAllocation.capacity := 3%nat |}.
Definition cancellationLine : Line :=
  {| allocation := twoAllocated; committedMBP := [(-2147483648)%Z;2147483647%Z]; inner := 100%Z; gap := 0%Z |}.
Definition negativeLine : Line :=
  {| allocation := twoAllocated; committedMBP := [301%Z;0%Z]; inner := 100%Z; gap := 0%Z |}.
Definition zeroRound (mode : bool) : Round :=
  {| used := [1%Z;100%Z]; items := [activeHalf mode;frozenBad] |}.
Definition positiveRound (mode : bool) : Round :=
  {| used := [1%Z;0%Z]; items := [activeHalf mode;frozenBad] |}.
Definition flippedRound (mode : bool) : Round :=
  {| used := [1%Z;101%Z]; items := [activeHalf mode;frozenBad] |}.
Definition negativeRound (mode : bool) : Round :=
  {| used := [1%Z;(-2)%Z]; items := [activeHalf mode;frozenBad] |}.
Definition positiveFlip (mode : bool) : Round :=
  {| used := [1%Z;(-203)%Z]; items := [activeHalf mode;frozenBad] |}.
Definition fullRound (mode : bool) : Round :=
  {| used := [1%Z;0%Z]; items := [activeFull mode;frozenBad] |}.
Definition noWeightRound : Round := {| used := [0%Z;1%Z]; items := [zeroWeight;frozenBad] |}.
End EntryCases.
