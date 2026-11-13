Require Import Gappa.Gappa_library.
Section Generated_by_Gappa.
Variable _i : R.
Definition f1 := Float2 (-1) (59).
Definition f2 := Float2 (1) (59).
Definition i1 := makepairF f1 f2.
Definition p1 := BND _i i1. (* BND(i, [-5.76461e+17, 5.76461e+17]) *)
Variable _s : R.
Definition f3 := Float2 (0) (0).
Definition f4 := Float2 (1) (0).
Definition i2 := makepairF f3 f4.
Definition p2 := BND _s i2. (* BND(s, [0, 1]) *)
Definition s2 := p1 /\ p2.
Definition _f := (rounding_float rndNE (53)%positive (-1074)%Z) _i.
Definition p3 := BND _f i1. (* BND(f, [-5.76461e+17, 5.76461e+17]) *)
Definition s8 := not p3.
Definition _raw := (_f * _s)%R.
Definition p4 := BND _raw i1. (* BND(raw, [-5.76461e+17, 5.76461e+17]) *)
Definition s9 := not p4.
Definition s7 := s8 \/ s9.
Definition _prod := (rounding_float rndNE (53)%positive (-1074)%Z) _raw.
Definition p5 := BND _prod i1. (* BND(prod, [-5.76461e+17, 5.76461e+17]) *)
Definition s10 := not p5.
Definition s6 := s7 \/ s10.
Definition r7 := float10R (Float10 (5) (-1)).
Definition r6 := (_prod + r7)%R.
Definition f5 := Float2 (-1) (60).
Definition f6 := Float2 (1) (60).
Definition i3 := makepairF f5 f6.
Definition p6 := BND r6 i3. (* BND(prod + 5e-1, [-1.15293e+18, 1.15293e+18]) *)
Definition s11 := not p6.
Definition s5 := s6 \/ s11.
Definition _added := (rounding_float rndNE (53)%positive (-1074)%Z) r6.
Definition p7 := BND _added i1. (* BND(added, [-5.76461e+17, 5.76461e+17]) *)
Definition s12 := not p7.
Definition s4 := s5 \/ s12.
Definition _delta := (rounding_fixed rndDN (0)%Z) _added.
Definition p8 := BND _delta i1. (* BND(delta, [-5.76461e+17, 5.76461e+17]) *)
Definition s13 := not p8.
Definition s3 := s4 \/ s13.
Definition s1 := s2 /\ s3.
Definition s14 := s12 \/ s13.
Definition s16 := s11 \/ s12.
Definition s15 := s16 \/ s13.
Definition s19 := s10 \/ s11.
Definition s18 := s19 \/ s12.
Definition s17 := s18 \/ s13.
Definition s23 := s9 \/ s10.
Definition s22 := s23 \/ s11.
Definition s21 := s22 \/ s12.
Definition s20 := s21 \/ s13.
Lemma l7 : s1 -> s3.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj2 h1).
Qed.
Lemma l10 : s1 -> s2.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj1 h1).
Qed.
Lemma l9 : s1 -> p1 (* BND(i, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l10 h0).
 exact (proj1 h1).
Qed.
Lemma t1 : p1 -> p3.
Proof.
 intros h0.
 refine (float_round_ne _ _ _i i1 i1 h0 _) ; finalize.
Qed.
Lemma l8 : s1 -> p3 (* BND(f, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l9 h0).
 apply t1. exact h1.
Qed.
Lemma l6 : s1 -> s20.
Proof.
 intros h0.
 assert (h1 := l7 h0).
 assert (h2 := l8 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i1)) (Tatom false (Abnd 1%nat i1))) (Tatom false (Abnd 2%nat i1))) (Tatom false (Abnd 3%nat i3))) (Tatom false (Abnd 4%nat i1))) (Tatom false (Abnd 5%nat i1))) (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i1)) (Tatom false (Abnd 2%nat i1))) (Tatom false (Abnd 3%nat i3))) (Tatom false (Abnd 4%nat i1))) (Tatom false (Abnd 5%nat i1))) (Abnd 0%nat i1) (List.cons _f (List.cons _raw (List.cons _prod (List.cons r6 (List.cons _added (List.cons _delta List.nil)))))) h2 h1 _) ; finalize.
Qed.
Lemma l12 : s1 -> p2 (* BND(s, [0, 1]) *).
Proof.
 intros h0.
 assert (h1 := l10 h0).
 exact (proj2 h1).
Qed.
Lemma t2 : p3 -> p2 -> p4.
Proof.
 intros h0 h1.
 refine (mul_op _f _s i1 i2 i1 h0 h1 _) ; finalize.
Qed.
Lemma l11 : s1 -> p4 (* BND(raw, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l8 h0).
 assert (h2 := l12 h0).
 apply t2. exact h1. exact h2.
Qed.
Lemma l5 : s1 -> s17.
Proof.
 intros h0.
 assert (h1 := l6 h0).
 assert (h2 := l11 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i1)) (Tatom false (Abnd 1%nat i1))) (Tatom false (Abnd 2%nat i3))) (Tatom false (Abnd 3%nat i1))) (Tatom false (Abnd 4%nat i1))) (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i1)) (Tatom false (Abnd 2%nat i3))) (Tatom false (Abnd 3%nat i1))) (Tatom false (Abnd 4%nat i1))) (Abnd 0%nat i1) (List.cons _raw (List.cons _prod (List.cons r6 (List.cons _added (List.cons _delta List.nil))))) h2 h1 _) ; finalize.
Qed.
Lemma t3 : p4 -> p5.
Proof.
 intros h0.
 refine (float_round_ne _ _ _raw i1 i1 h0 _) ; finalize.
Qed.
Lemma l13 : s1 -> p5 (* BND(prod, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l11 h0).
 apply t3. exact h1.
Qed.
Lemma l4 : s1 -> s15.
Proof.
 intros h0.
 assert (h1 := l5 h0).
 assert (h2 := l13 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i1)) (Tatom false (Abnd 1%nat i3))) (Tatom false (Abnd 2%nat i1))) (Tatom false (Abnd 3%nat i1))) (Ttree false (Ttree false (Tatom false (Abnd 1%nat i3)) (Tatom false (Abnd 2%nat i1))) (Tatom false (Abnd 3%nat i1))) (Abnd 0%nat i1) (List.cons _prod (List.cons r6 (List.cons _added (List.cons _delta List.nil)))) h2 h1 _) ; finalize.
Qed.
Definition f7 := Float2 (-1152921504606846975) (-1).
Definition f8 := Float2 (576460752303423489) (0).
Definition i4 := makepairF f7 f8.
Definition p9 := BND r6 i4. (* BND(prod + 5e-1, [-5.76461e+17, 5.76461e+17]) *)
Definition f9 := Float2 (1) (-1).
Definition i5 := makepairF f9 f4.
Definition p10 := BND r7 i5. (* BND(5e-1, [0.5, 1]) *)
Lemma t4 : p10.
Proof.
 refine (constant10 _ i5 _) ; finalize.
Qed.
Lemma l15 : s1 -> p10 (* BND(5e-1, [0.5, 1]) *).
Proof.
 intros h0.
 apply t4.
Qed.
Lemma t5 : p5 -> p10 -> p9.
Proof.
 intros h0 h1.
 refine (add _prod r7 i1 i5 i4 h0 h1 _) ; finalize.
Qed.
Lemma l14 : s1 -> p9 (* BND(prod + 5e-1, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l13 h0).
 assert (h2 := l15 h0).
 apply t5. exact h1. exact h2.
Qed.
Lemma l3 : s1 -> s14.
Proof.
 intros h0.
 assert (h1 := l4 h0).
 assert (h2 := l14 h0).
 refine (simplify (Ttree false (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i1))) (Tatom false (Abnd 2%nat i1))) (Ttree false (Tatom false (Abnd 1%nat i1)) (Tatom false (Abnd 2%nat i1))) (Abnd 0%nat i4) (List.cons r6 (List.cons _added (List.cons _delta List.nil))) h2 h1 _) ; finalize.
Qed.
Definition f10 := Float2 (9007199254740993) (6).
Definition i6 := makepairF f1 f10.
Definition p11 := BND r6 i6. (* BND(prod + 5e-1, [-5.76461e+17, 5.76461e+17]) *)
Lemma t6 : p11 -> p7.
Proof.
 intros h0.
 refine (float_round_ne _ _ r6 i6 i1 h0 _) ; finalize.
Qed.
Lemma l16 : s1 -> p7 (* BND(added, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l14 h0).
 apply t6. refine (subset r6 i4 i6 h1 _) ; finalize.
Qed.
Lemma l2 : s1 -> s13.
Proof.
 intros h0.
 assert (h1 := l3 h0).
 assert (h2 := l16 h0).
 refine (simplify (Ttree false (Tatom false (Abnd 0%nat i1)) (Tatom false (Abnd 1%nat i1))) (Tatom false (Abnd 1%nat i1)) (Abnd 0%nat i1) (List.cons _added (List.cons _delta List.nil)) h2 h1 _) ; finalize.
Qed.
Lemma t7 : p7 -> p8.
Proof.
 intros h0.
 refine (fixed_round_dn _ _added i1 i1 h0 _) ; finalize.
Qed.
Lemma l17 : s1 -> p8 (* BND(delta, [-5.76461e+17, 5.76461e+17]) *).
Proof.
 intros h0.
 assert (h1 := l16 h0).
 apply t7. exact h1.
Qed.
Lemma l1 : s1 -> False.
Proof.
 intros h0.
 assert (h1 := l2 h0).
 assert (h2 := l17 h0).
 refine (simplify (Tatom false (Abnd 0%nat i1)) Tfalse (Abnd 0%nat i1) (List.cons _delta List.nil) h2 h1 _) ; finalize.
Qed.
End Generated_by_Gappa.
Print Assumptions l1.
Check l1.
