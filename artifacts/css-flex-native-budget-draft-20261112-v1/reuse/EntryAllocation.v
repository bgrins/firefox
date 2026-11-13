Require Import Arith PeanoNat List ZArith.
Import ListNotations.
Module EntryAllocation.
Open Scope nat_scope.
Definition headerBytes : nat := 8.
Definition mib : nat := 1048576.
Definition roundPowerTwo (n : nat) : nat := 2 ^ (Nat.log2 (n-1)+1).
Definition requestValid (elementBytes requested : nat) : Prop :=
  2 * requested * elementBytes <= 4294967295.
Definition grownBytes (elementBytes oldCapacity requested : nat) : nat :=
  let requestedBytes := headerBytes + requested * elementBytes in
  let oldBytes := headerBytes + oldCapacity * elementBytes in
  if requestedBytes <? 8 * mib then roundPowerTwo requestedBytes
  else mib * ((Nat.max requestedBytes (oldBytes + oldBytes/8) + mib-1)/mib).
Inductive Capacity (elementBytes : nat) : nat -> nat -> nat -> Prop :=
| spare : forall old requested, requested <= old -> Capacity elementBytes old requested old
| first : forall requested, 0 < requested -> requestValid elementBytes requested ->
    Capacity elementBytes 0 requested requested
| grow : forall old requested, 0 < old -> old < requested -> requestValid elementBytes requested ->
    Capacity elementBytes old requested ((grownBytes elementBytes old requested-headerBytes)/elementBytes).
Record ArrayState := { tokens : list nat; capacity : nat }.
Definition emptyArray := {| tokens := []; capacity := 0 |}.
Inductive ArrayStep (elementBytes : nat) : ArrayState -> ArrayState -> Prop :=
| append : forall xs cap cap' token, Capacity elementBytes cap (length xs+1) cap' ->
    ArrayStep elementBytes {| tokens := xs; capacity := cap |}
      {| tokens := xs++[token]; capacity := cap' |}
| pop : forall xs cap token, ArrayStep elementBytes {| tokens := xs++[token]; capacity := cap |}
      {| tokens := xs; capacity := cap |}
| shrink : forall xs cap, xs <> [] -> length xs < cap ->
    ArrayStep elementBytes {| tokens := xs; capacity := cap |} {| tokens := xs; capacity := length xs |}
| release : forall cap, ArrayStep elementBytes {| tokens := []; capacity := cap |} emptyArray
| unchanged : forall state, ArrayStep elementBytes state state.
Inductive Reachable (elementBytes : nat) : ArrayState -> Prop :=
| initial : Reachable elementBytes emptyArray
| next : forall before after, Reachable elementBytes before -> ArrayStep elementBytes before after ->
    Reachable elementBytes after.
Inductive Move : ArrayState -> ArrayState -> ArrayState -> ArrayState -> Prop :=
| transfer : forall source destination, Move source destination emptyArray source.
Inductive Reconstruction (elementBytes : nat) : list nat -> ArrayState -> Prop :=
| rebuild_empty : Reconstruction elementBytes [] emptyArray
| rebuild_append : forall xs cap cap' token,
    Reconstruction elementBytes xs {| tokens := xs; capacity := cap |} ->
    Capacity elementBytes cap (length xs+1) cap' ->
    Reconstruction elementBytes (xs++[token]) {| tokens := xs++[token]; capacity := cap' |}.
End EntryAllocation.
