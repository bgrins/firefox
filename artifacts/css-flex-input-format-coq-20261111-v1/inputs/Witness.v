Require Import Gappa.Gappa_library.
Section Generated_by_Gappa.
Definition _i := Float1 (576460752303423487).
Definition _f := (rounding_float rndNE (53)%positive (-1074)%Z) _i.
Definition r8 := Float1 (1).
Definition r5 := (_f / r8)%R.
Definition _prod := (rounding_float rndNE (53)%positive (-1074)%Z) r5.
Definition r9 := float10R (Float10 (5) (-1)).
Definition r3 := (_prod + r9)%R.
Definition _added := (rounding_float rndNE (53)%positive (-1074)%Z) r3.
Definition _delta := (rounding_fixed rndDN (0)%Z) _added.
Definition f1 := Float2 (1) (59).
Definition i1 := makepairF f1 f1.
Definition p1 := BND _delta i1. (* BND(delta, [5.7646e+17, 5.76461e+17]) *)
Definition s2 := not p1.
Definition r10 := (_delta - _i)%R.
Definition f2 := Float2 (1) (0).
Definition i2 := makepairF f2 f2.
Definition p2 := BND r10 i2. (* BND(delta - i, [1, 1]) *)
Definition s3 := not p2.
Definition s1 := s2 \/ s3.
Definition p3 := BND _added i1. (* BND(added, [5.7646e+17, 5.76461e+17]) *)
Definition f3 := Float2 (9007199254740993) (6).
Definition i3 := makepairF f1 f3.
Definition p4 := BND r3 i3. (* BND(prod + 5e-1, [5.7646e+17, 5.76461e+17]) *)
Definition p5 := BND _prod i1. (* BND(prod, [5.7646e+17, 5.76461e+17]) *)
Definition p6 := BND r5 i1. (* BND(f / 1, [5.7646e+17, 5.76461e+17]) *)
Definition p7 := BND _f i1. (* BND(f, [5.7646e+17, 5.76461e+17]) *)
Definition f4 := Float2 (576460752303423487) (0).
Definition i4 := makepairF f4 f4.
Definition p8 := BND _i i4. (* BND(i, [5.7646e+17, 5.76461e+17]) *)
Lemma t1 : p8.
Proof.
 refine (constant1 _ i4 _) ; finalize.
Qed.
Lemma l9 : s1 -> p8 (* BND(i, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 apply t1.
Qed.
Definition f5 := Float2 (18014398509481983) (5).
Definition i5 := makepairF f5 f1.
Definition p9 := BND _i i5. (* BND(i, [5.7646e+17, 5.76461e+17]) *)
Lemma t2 : p9 -> p7.
Proof.
 intros h0.
 refine (float_round_ne _ _ _i i5 i1 h0 _) ; finalize.
Qed.
Lemma l8 : s1 -> p7 (* BND(f, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l9 h0).
 apply t2. refine (subset _i i4 i5 h1 _) ; finalize.
Qed.
Definition p10 := BND r8 i2. (* BND(1, [1, 1]) *)
Lemma t3 : p10.
Proof.
 refine (constant1 _ i2 _) ; finalize.
Qed.
Lemma l10 : s1 -> p10 (* BND(1, [1, 1]) *).
Proof.
 intros h0.
 apply t3.
Qed.
Lemma t4 : p7 -> p10 -> p6.
Proof.
 intros h0 h1.
 refine (div_pp _f r8 i1 i2 i1 h0 h1 _) ; finalize.
Qed.
Lemma l7 : s1 -> p6 (* BND(f / 1, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l8 h0).
 assert (h2 := l10 h0).
 apply t4. exact h1. exact h2.
Qed.
Lemma t5 : p6 -> p5.
Proof.
 intros h0.
 refine (float_round_ne _ _ r5 i1 i1 h0 _) ; finalize.
Qed.
Lemma l6 : s1 -> p5 (* BND(prod, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l7 h0).
 apply t5. exact h1.
Qed.
Definition f6 := Float2 (1) (-1).
Definition i6 := makepairF f6 f2.
Definition p11 := BND r9 i6. (* BND(5e-1, [0.5, 1]) *)
Lemma t6 : p11.
Proof.
 refine (constant10 _ i6 _) ; finalize.
Qed.
Lemma l11 : s1 -> p11 (* BND(5e-1, [0.5, 1]) *).
Proof.
 intros h0.
 apply t6.
Qed.
Lemma t7 : p5 -> p11 -> p4.
Proof.
 intros h0 h1.
 refine (add _prod r9 i1 i6 i3 h0 h1 _) ; finalize.
Qed.
Lemma l5 : s1 -> p4 (* BND(prod + 5e-1, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l6 h0).
 assert (h2 := l11 h0).
 apply t7. exact h1. exact h2.
Qed.
Lemma t8 : p4 -> p3.
Proof.
 intros h0.
 refine (float_round_ne _ _ r3 i3 i1 h0 _) ; finalize.
Qed.
Lemma l4 : s1 -> p3 (* BND(added, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l5 h0).
 apply t8. exact h1.
Qed.
Lemma t9 : p3 -> p1.
Proof.
 intros h0.
 refine (fixed_round_dn _ _added i1 i1 h0 _) ; finalize.
Qed.
Lemma l3 : s1 -> p1 (* BND(delta, [5.7646e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l4 h0).
 apply t9. exact h1.
Qed.
Lemma l2 : s1 -> s3.
Proof.
 intros h0.
 assert (h1 := h0).
 assert (h2 := l3 h0).
 refine (simplify (Ttree false (Tatom false (Abnd 0%nat i1)) (Tatom false (Abnd 1%nat i2))) (Tatom false (Abnd 1%nat i2)) (Abnd 0%nat i1) (List.cons _delta (List.cons r10 List.nil)) h2 h1 _) ; finalize.
Qed.
Lemma t10 : p1 -> p8 -> p2.
Proof.
 intros h0 h1.
 refine (sub _delta _i i1 i4 i2 h0 h1 _) ; finalize.
Qed.
Lemma l12 : s1 -> p2 (* BND(delta - i, [1, 1]) *).
Proof.
 intros h0.
 assert (h1 := l3 h0).
 assert (h2 := l9 h0).
 apply t10. exact h1. exact h2.
Qed.
Lemma l1 : s1 -> False.
Proof.
 intros h0.
 assert (h1 := l2 h0).
 assert (h2 := l12 h0).
 refine (simplify (Tatom false (Abnd 0%nat i2)) Tfalse (Abnd 0%nat i2) (List.cons r10 List.nil) h2 h1 _) ; finalize.
Qed.
End Generated_by_Gappa.
