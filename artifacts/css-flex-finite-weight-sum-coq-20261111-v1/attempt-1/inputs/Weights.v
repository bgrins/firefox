Require Import Reals ZArith List Psatz Classical Gappa.Gappa_library.
Require Import WeightTarget Product Addition.
Open Scope R_scope.

Lemma count_bound (count : Z) (sum : R) :
  (0 <= count <= countLimit)%Z -> 0 <= sum <= IZR count*stride ->
  0 <= sum <= sumLimit.
Proof.
  intros Hcount Hsum.
  unfold countLimit in Hcount.
  assert (Hreal : IZR count <= 4294967295) by (apply IZR_le; lia).
  unfold stride, sumLimit in *. lra.
Qed.

Lemma product_output (f b : R) : Product.p1 f -> Product.p2 b -> Product.p4 f b.
Proof.
  intros Hf Hb. apply NNPP. intro Hbad. apply (Product.l1 f b).
  split; [split; assumption | right; exact Hbad].
Qed.

Lemma addition_output (s w : R) : Addition.p1 s -> Addition.p2 w ->
  Addition.p3 s w /\ Addition.p4 s w /\ Addition.p5 s w.
Proof.
  intros Hs Hw.
  split.
  - apply NNPP. intro Hbad. apply (Addition.l1 s w).
    split; [split; assumption | left; left; exact Hbad].
  - split; apply NNPP; intro Hbad; apply (Addition.l1 s w).
    + split; [split; assumption | left; right; exact Hbad].
    + split; [split; assumption | right; exact Hbad].
Qed.

Theorem product_target : ProductTarget.
Proof.
  intros factor base Hfirst Hsecond.
  pose proof (product_output factor base) as H.
  cbv delta [Product.p1 Product.p2 Product.p4 Product.f1 Product.f2 Product.i1 Product.f3 Product.i2 Product.f4 Product.i3] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 31) with (2147483648:R) in H by reflexivity.
  try replace (Raux.bpow radix2 128) with (340282366920938463463374607431768211456:R) in H by reflexivity.
  try replace (Raux.bpow radix2 159) with (730750818665451459101842416358141509827966271488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 160) with (1461501637330902918203684832716283019655932542976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 192) with (6277101735386680763835789423207666416102355444464034512896:R) in H by reflexivity.
  try replace (Raux.bpow radix2 193) with (12554203470773361527671578846415332832204710888928069025792:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  unfold FactorValid, WeightValid, StepBound, factorLimit, baseLimit,
    weightLimit, stride, sumLimit, intermediateLimit in *.
  specialize (H ltac:(lra) ltac:(lra)).
  change (0 <= Product._weight factor base <= 730750818665451459101842416358141509827966271488).
  exact H.
Qed.

Theorem addition_target : AdditionTarget.
Proof.
  intros sum weight Hfirst Hsecond.
  pose proof (addition_output sum weight) as H.
  cbv delta [Addition.p1 Addition.p2 Addition.p3 Addition.p4 Addition.p5 Addition.r1 Addition._raw Addition.f1 Addition.f2 Addition.i1 Addition.f3 Addition.i2 Addition.f4 Addition.i3 Addition.f5 Addition.f6 Addition.i4 Addition.f7 Addition.i5 Addition.f8 Addition.f9 Addition.i6 Addition.f10 Addition.i7] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 31) with (2147483648:R) in H by reflexivity.
  try replace (Raux.bpow radix2 128) with (340282366920938463463374607431768211456:R) in H by reflexivity.
  try replace (Raux.bpow radix2 159) with (730750818665451459101842416358141509827966271488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 160) with (1461501637330902918203684832716283019655932542976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 192) with (6277101735386680763835789423207666416102355444464034512896:R) in H by reflexivity.
  try replace (Raux.bpow radix2 193) with (12554203470773361527671578846415332832204710888928069025792:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  unfold FactorValid, WeightValid, StepBound, factorLimit, baseLimit,
    weightLimit, stride, sumLimit, intermediateLimit in *.
  specialize (H ltac:(lra) ltac:(lra)).
  change (0 <= sum+weight <= 12554203470773361527671578846415332832204710888928069025792 /\
    0 <= Addition._next sum weight <= 12554203470773361527671578846415332832204710888928069025792 /\
    Addition._next sum weight <= sum+1461501637330902918203684832716283019655932542976).
  lra.
Qed.

Lemma fold_bound (weights : list R) : forall initial processed,
  (0 <= processed)%Z ->
  (processed + Z.of_nat (length weights) <= countLimit)%Z ->
  0 <= initial <= IZR processed*stride -> Forall WeightValid weights ->
  0 <= accumulate weights initial <=
    IZR (processed + Z.of_nat (length weights))*stride.
Proof.
  induction weights as [ | weight rest IH]; intros initial processed Hprocessed Hcount Hinitial Hvalid.
  - cbn [length]. rewrite Z.add_0_r. exact Hinitial.
  - inversion Hvalid as [ | head tail Hweight Hrest]; subst.
    assert (Hdomain : 0 <= initial <= sumLimit).
    { apply (count_bound processed initial); [lia | exact Hinitial]. }
    pose proof (addition_target initial weight Hdomain Hweight) as Hstep.
    unfold StepBound in Hstep.
    assert (Hnext : 0 <= rn (initial+weight) <= IZR (processed+1)*stride).
    { rewrite plus_IZR. cbn [IZR]. unfold stride in *. lra. }
    cbn [length] in Hcount |- *.
    rewrite Nat2Z.inj_succ in Hcount |- *.
    specialize (IH (rn (initial+weight)) (processed+1)%Z ltac:(lia) ltac:(lia) Hnext Hrest).
    replace (processed + Z.succ (Z.of_nat (length rest)))%Z with
      (processed+1 + Z.of_nat (length rest))%Z by lia.
    exact IH.
Qed.

Theorem ordered_target : OrderedTarget.
Proof.
  intros weights Hcount Hvalid.
  pose proof (fold_bound weights 0 0%Z ltac:(lia) ltac:(lia) ltac:(cbn; lra) Hvalid) as H.
  rewrite Z.add_0_l in H. exact H.
Qed.

Lemma firstn_valid_count (weights : list R) : forall count,
  Forall WeightValid weights ->
  Forall WeightValid (firstn count weights) /\
  (length (firstn count weights) <= length weights)%nat.
Proof.
  induction weights as [ | weight rest IH]; intros count Hvalid.
  - destruct count; cbn; split; try constructor; lia.
  - destruct count as [ | count].
    + cbn. split; [constructor | lia].
    + inversion Hvalid as [ | head tail Hweight Hrest]; subst.
      destruct (IH count Hrest) as [Htake Hlength].
      cbn. split; [constructor; assumption | lia].
Qed.

Theorem prefix_target : PrefixTarget.
Proof.
  intros weights count Hcount Hvalid.
  destruct (firstn_valid_count weights count Hvalid) as [Htake Hlength].
  pose proof (ordered_target (firstn count weights) ltac:(lia) Htake) as H.
  apply (count_bound (Z.of_nat (length (firstn count weights)))); [lia | exact H].
Qed.

Theorem factor_sum_target : FactorSumTarget.
Proof.
  intros factors Hcount Hvalid.
  assert (Hweights : Forall WeightValid factors).
  { apply Forall_impl with (P := FactorValid); [ | exact Hvalid].
    intros factor Hfactor.
    unfold FactorValid, WeightValid, factorLimit, weightLimit in *. lra. }
  pose proof (ordered_target factors Hcount Hweights) as H.
  apply (count_bound (Z.of_nat (length factors))); [lia | exact H].
Qed.

Theorem full_weight_target : FullWeightTarget.
Proof.
  exact (conj product_target (conj addition_target (conj ordered_target
    (conj prefix_target factor_sum_target)))).
Qed.

Print Assumptions product_target.
Print Assumptions addition_target.
Print Assumptions ordered_target.
Print Assumptions prefix_target.
Print Assumptions factor_sum_target.
Print Assumptions full_weight_target.
