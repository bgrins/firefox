Require Import Reals ZArith List Bool Lia Psatz.
Require Import ConversionTarget ReverseTarget EntryModel NativeState NativeMainBounds NativeClampFacts NativeProjectionAlgebra.
Import ListNotations.
Module NativeBudgetArithmetic.
Import NativeSchedule.
Open Scope Z_scope.
Definition Good (r : Row) := NativeMainBounds.SeedRange (seed r) /\ EntryAcquisition.Acquired32 (main r).
Definition cap : Z := 1152921504606846976.
Definition differenceCap : Z := 4294967295.
Lemma abs_fits : forall x, Z.abs x <= 9223372036854775807 -> Fits64 x.
Proof. intros x H; unfold Fits64; pose proof (Z.abs_spec x); lia. Qed.
Lemma acquired_abs : forall x, EntryAcquisition.Acquired32 x -> Z.abs x <= 2147483648.
Proof. intros x H; unfold EntryAcquisition.Acquired32 in H; pose proof (Z.abs_spec x); lia. Qed.
Lemma acquired_fits : forall x, EntryAcquisition.Acquired32 x -> Fits64 x.
Proof. intros x H; apply abs_fits; pose proof (acquired_abs x H); lia. Qed.
Lemma project_bounds : forall x, EntryAcquisition.Acquired32 (project32 x).
Proof.
  intro x; unfold project32,EntryAcquisition.Acquired32.
  pose proof (Z.min_spec x 2147483647); pose proof (Z.max_spec (-2147483648) (Z.min x 2147483647)); intuition lia.
Qed.
Lemma clamp_good : forall r, Good r -> Good (fst (NativeClamp.one r)).
Proof.
  intros r [Seed Main]. unfold Good. rewrite NativeClampFacts.one_seed; split; [exact Seed|].
  pose proof (NativeMainBounds.one_bounds r Seed) as [_ Range].
  unfold NativeMainBounds.MainRange in Range. rewrite NativeClampFacts.one_seed in Range.
  unfold NativeMainBounds.SeedRange in Seed. unfold EntryAcquisition.Acquired32; lia.
Qed.
Lemma clamp_difference : forall r, Good r -> Z.abs (snd (NativeClamp.one r)) <= differenceCap.
Proof.
  intros r G. pose proof (proj2 G) as Before. pose proof (proj2 (clamp_good r G)) as After.
  rewrite NativeClampFacts.one_difference. unfold EntryAcquisition.Acquired32 in *.
  unfold differenceCap. pose proof (Z.abs_spec (main (fst (NativeClamp.one r))-main r)); lia.
Qed.
Lemma budget_fits : forall n free,
  (n<=134217727)%nat -> Z.abs free<=cap ->
  Z.abs free+Z.of_nat n*differenceCap <= 9223372036854775807.
Proof. intros n free N F; unfold cap,differenceCap in *; assert (Z.of_nat n<=134217727) by lia; nia. Qed.
Lemma domain_abs : forall free, ReverseTarget.FreeDomain free -> Z.abs free<=cap.
Proof. intros free D; unfold ReverseTarget.FreeDomain,cap in *; pose proof (Z.abs_spec free); lia. Qed.
Lemma abs_domain : forall free, Z.abs free<=cap -> ReverseTarget.FreeDomain free.
Proof. intros free D; unfold ReverseTarget.FreeDomain,cap in *; pose proof (Z.abs_spec free); lia. Qed.
Print Assumptions abs_fits.
Print Assumptions acquired_abs.
Print Assumptions acquired_fits.
Print Assumptions project_bounds.
Print Assumptions clamp_good.
Print Assumptions clamp_difference.
Print Assumptions budget_fits.
Print Assumptions domain_abs.
Print Assumptions abs_domain.
End NativeBudgetArithmetic.
