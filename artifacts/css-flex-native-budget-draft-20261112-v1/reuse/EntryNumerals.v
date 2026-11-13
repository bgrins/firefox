Require Import Arith PeanoNat ZArith Lia.
Ltac entry_numerals :=
  cbv [Init.Nat.of_num_uint Init.Nat.of_uint Init.Nat.of_uint_acc] in *;
  repeat rewrite Nat.tail_mul_spec in *.
Lemma entry_half_max : forall x : nat, 2*x<=4294967295 -> x<=2147483647.
Proof. intros x H. entry_numerals. lia. Qed.
Print Assumptions entry_half_max.

Lemma entry_pow32_spec : forall n : nat, (n<2^32)%nat <-> (Z.of_nat n<4294967296)%Z.
Proof. intro n. rewrite Nat2Z.inj_lt, Nat2Z.inj_pow. reflexivity. Qed.
Lemma entry_pow31_spec : forall n : nat, (n<2^31)%nat <-> (Z.of_nat n<2147483648)%Z.
Proof. intro n. rewrite Nat2Z.inj_lt, Nat2Z.inj_pow. reflexivity. Qed.
Print Assumptions entry_pow32_spec.
Print Assumptions entry_pow31_spec.
