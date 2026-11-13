Require Import Reals ZArith Gappa.Gappa_library.
Open Scope R_scope.

Definition rn (x : R) := rounding_float rndNE 53 (-1074) x.
Definition half : R := float10R (Float10 5 (-1)).
Definition integerRound (x : R) := rounding_fixed rndDN 0 (rn (x + half)).
Definition mulDelta (free share : R) := integerRound (rn (rn free * share)).
Definition divDelta (free count : R) := integerRound (rn (rn free / count)).
Definition EnvelopeR (free delta : R) : Prop :=
  Rmin free 0 - 1048576 <= delta <= Rmax free 0 + 1048576.
Definition DomainR (free : R) : Prop :=
  -1152921504606846976 <= free <= 1152921504606846976.

Inductive Choice : Type :=
  | Zero
  | Whole
  | Fraction (share : R)
  | Equal (count : R).

Definition ValidChoice (choice : Choice) : Prop :=
  match choice with
  | Zero | Whole => True
  | Fraction share => 0 <= share <= 1
  | Equal count => 1 <= count <= 134217728
  end.

Definition computeDelta (free : R) (choice : Choice) : R :=
  match choice with
  | Zero => 0
  | Whole => free
  | Fraction share => mulDelta free share
  | Equal count => divDelta free count
  end.

Definition MulTarget : Prop := forall free share,
  DomainR free -> 0 <= share <= 1 -> EnvelopeR free (mulDelta free share).
Definition DivTarget : Prop := forall free count,
  DomainR free -> 1 <= count <= 134217728 -> EnvelopeR free (divDelta free count).
Definition FactorTarget : Prop := forall free share,
  -576460752303423488 <= free <= 576460752303423488 ->
  0 <= share <= 1 ->
  -576460752303423488 <= mulDelta free share <= 576460752303423488.
Definition ProviderTarget : Prop := forall free choice,
  DomainR free -> ValidChoice choice -> EnvelopeR free (computeDelta free choice).
Definition IntegerTarget : Prop := forall (free delta : Z) choice,
  (-1152921504606846976 <= free <= 1152921504606846976)%Z ->
  ValidChoice choice -> IZR delta = computeDelta (IZR free) choice ->
  (Z.min free 0 - 1048576 <= delta <= Z.max free 0 + 1048576)%Z.
Definition FullTarget : Prop :=
  MulTarget /\ DivTarget /\ FactorTarget /\ ProviderTarget /\ IntegerTarget.
