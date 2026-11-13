Require Import Reals Ring.
Require Import Gappa.Gappa_library.
Section Generated_by_Gappa.
Variable _i : R.
Definition _f := (rounding_float rndNE (53)%positive (-1074)%Z) _i.
Variable _n : R.
Definition _raw := (_f / _n)%R.
Definition _prod := (rounding_float rndNE (53)%positive (-1074)%Z) _raw.
Definition r10 := float10R (Float10 (5) (-1)).
Definition r4 := (_prod + r10)%R.
Definition _added := (rounding_float rndNE (53)%positive (-1074)%Z) r4.
Definition _delta := (rounding_fixed rndDN (0)%Z) _added.
Definition _ideal := (_i / _n)%R.
Definition r1 := (_delta - _ideal)%R.
Definition r16 := (_delta - _added)%R.
Definition r17 := (_added - r4)%R.
Definition r15 := (r16 + r17)%R.
Definition r18 := (_prod - _raw)%R.
Definition r14 := (r15 + r18)%R.
Definition r20 := (_f - _i)%R.
Definition r19 := (r20 / _n)%R.
Definition r13 := (r14 + r19)%R.
Definition r12 := (r13 + r10)%R.
Lemma a1 : r1 = r12.
Proof.
 cbv delta [_f _raw _prod r10 r4 _added _delta _ideal r1 r16 r17 r15 r18 r14 r20 r19 r13 r12].
 cbv [Float1 IZR IPR]. unfold Rdiv. ring.
Qed.
Lemma b1 : r1 = r12.
 apply a1.
Qed.
Definition r21 := (r1 + _ideal)%R.
Lemma a2 : _delta = r21.
Proof.
 cbv delta [_f _raw _prod r10 r4 _added _delta _ideal r1 r16 r17 r15 r18 r14 r20 r19 r13 r12 r21].
 cbv [Float1 IZR IPR]. unfold Rdiv. ring.
Qed.
Lemma b2 : _delta = r21.
 apply a2.
Qed.
Definition r22 := (_delta - _i)%R.
Definition r24 := (_ideal - _i)%R.
Definition r23 := (r1 + r24)%R.
Lemma a3 : r22 = r23.
Proof.
 cbv delta [_f _raw _prod r10 r4 _added _delta _ideal r1 r16 r17 r15 r18 r14 r20 r19 r13 r12 r21 r22 r24 r23].
 cbv [Float1 IZR IPR]. unfold Rdiv. ring.
Qed.
Lemma b3 : r22 = r23.
 apply a3.
Qed.
Definition r28 := Float1 (1).
Definition r27 := (r28 / _n)%R.
Definition r26 := (r27 - r28)%R.
Definition r25 := (_i * r26)%R.
Lemma a4 : r24 = r25.
Proof.
 cbv delta [_f _raw _prod r10 r4 _added _delta _ideal r1 r16 r17 r15 r18 r14 r20 r19 r13 r12 r21 r22 r24 r23 r28 r27 r26 r25].
 cbv [Float1 IZR IPR]. unfold Rdiv. ring.
Qed.
Lemma b4 : r24 = r25.
 apply a4.
Qed.
Definition f1 := Float2 (-1) (60).
Definition f2 := Float2 (0) (0).
Definition i1 := makepairF f1 f2.
Definition p1 := BND _i i1. (* BND(i, [-1.15293e+18, 0]) *)
Definition f3 := Float2 (1) (0).
Definition f4 := Float2 (1) (27).
Definition i2 := makepairF f3 f4.
Definition p2 := BND _n i2. (* BND(n, [1, 1.34218e+08]) *)
Definition s2 := p1 /\ p2.
Definition f5 := Float2 (1) (60).
Definition i3 := makepairF f1 f5.
Definition p3 := BND _f i3. (* BND(f, [-1.15293e+18, 1.15293e+18]) *)
Definition s11 := not p3.
Definition p4 := BND _raw i3. (* BND(raw, [-1.15293e+18, 1.15293e+18]) *)
Definition s12 := not p4.
Definition s10 := s11 \/ s12.
Definition p5 := BND _prod i3. (* BND(prod, [-1.15293e+18, 1.15293e+18]) *)
Definition s13 := not p5.
Definition s9 := s10 \/ s13.
Definition f6 := Float2 (-1) (61).
Definition f7 := Float2 (1) (61).
Definition i4 := makepairF f6 f7.
Definition p6 := BND r4 i4. (* BND(prod + 5e-1, [-2.30585e+18, 2.30585e+18]) *)
Definition s14 := not p6.
Definition s8 := s9 \/ s14.
Definition p7 := BND _added i4. (* BND(added, [-2.30585e+18, 2.30585e+18]) *)
Definition s15 := not p7.
Definition s7 := s8 \/ s15.
Definition p8 := BND _delta i4. (* BND(delta, [-2.30585e+18, 2.30585e+18]) *)
Definition s16 := not p8.
Definition s6 := s7 \/ s16.
Definition f8 := Float2 (-1) (20).
Definition f9 := Float2 (1) (20).
Definition i5 := makepairF f8 f9.
Definition p9 := BND r1 i5. (* BND(delta - ideal, [-1.04858e+06, 1.04858e+06]) *)
Definition s17 := not p9.
Definition s5 := s6 \/ s17.
Definition i6 := makepairF f6 f9.
Definition p10 := BND _delta i6. (* BND(delta, [-2.30585e+18, 1.04858e+06]) *)
Definition s18 := not p10.
Definition s4 := s5 \/ s18.
Definition i7 := makepairF f8 f7.
Definition p11 := BND r22 i7. (* BND(delta - i, [-1.04858e+06, 2.30585e+18]) *)
Definition s19 := not p11.
Definition s3 := s4 \/ s19.
Definition s1 := s2 /\ s3.
Definition s20 := s17 \/ s19.
Definition s23 := s16 \/ s17.
Definition s22 := s23 \/ s18.
Definition s21 := s22 \/ s19.
Definition s27 := s15 \/ s16.
Definition s26 := s27 \/ s17.
Definition s25 := s26 \/ s18.
Definition s24 := s25 \/ s19.
Definition s32 := s14 \/ s15.
Definition s31 := s32 \/ s16.
Definition s30 := s31 \/ s17.
Definition s29 := s30 \/ s18.
Definition s28 := s29 \/ s19.
Definition s38 := s13 \/ s14.
Definition s37 := s38 \/ s15.
Definition s36 := s37 \/ s16.
Definition s35 := s36 \/ s17.
Definition s34 := s35 \/ s18.
Definition s33 := s34 \/ s19.
Definition s45 := s12 \/ s13.
Definition s44 := s45 \/ s14.
Definition s43 := s44 \/ s15.
Definition s42 := s43 \/ s16.
Definition s41 := s42 \/ s17.
Definition s40 := s41 \/ s18.
Definition s39 := s40 \/ s19.
Lemma l9 : s1 -> s3.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj2 h1).
Qed.
Definition p12 := BND _f i1. (* BND(f, [-1.15293e+18, 0]) *)
Lemma l12 : s1 -> s2.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj1 h1).
Qed.
Lemma l11 : s1 -> p1 (* BND(i, [-1.15293e+18, 0]) *).
Proof.
 intros h0.
 assert (h1 := l12 h0).
 exact (proj1 h1).
Qed.
Lemma t1 : p1 -> p12.
Proof.
 intros h0.
 refine (float_round_ne _ _ _i i1 i1 h0 _) ; finalize.
Qed.
Lemma l10 : s1 -> p12 (* BND(f, [-1.15293e+18, 0]) *).
Proof.
 intros h0.
 assert (h1 := l11 h0).
 apply t1. exact h1.
Qed.
Lemma l8 : s1 -> s39.
Proof.
 intros h0.
 assert (h1 := l9 h0).
 assert (h2 := l10 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i3))) (Tatom false (Abnd 2%nat i3))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i4))) (Tatom false (Abnd 5%nat i4))) (Tatom false (Abnd 6%nat i5))) (Tatom false (Abnd 5%nat i6))) (Tatom false (Abnd 7%nat i7))) (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i3)) (Tatom false (Abnd 2%nat i3))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i4))) (Tatom false (Abnd 5%nat i4))) (Tatom false (Abnd 6%nat i5))) (Tatom false (Abnd 5%nat i6))) (Tatom false (Abnd 7%nat i7))) (Abnd 0%nat i1) (List.cons _f (List.cons _raw (List.cons _prod (List.cons r4 (List.cons _added (List.cons _delta (List.cons r1 (List.cons r22 List.nil)))))))) h2 h1 _) ; finalize.
Qed.
Definition p13 := BND _raw i1. (* BND(raw, [-1.15293e+18, 0]) *)
Lemma l14 : s1 -> p2 (* BND(n, [1, 1.34218e+08]) *).
Proof.
 intros h0.
 assert (h1 := l12 h0).
 exact (proj2 h1).
Qed.
Lemma t2 : p12 -> p2 -> p13.
Proof.
 intros h0 h1.
 refine (div_np _f _n i1 i2 i1 h0 h1 _) ; finalize.
Qed.
Lemma l13 : s1 -> p13 (* BND(raw, [-1.15293e+18, 0]) *).
Proof.
 intros h0.
 assert (h1 := l10 h0).
 assert (h2 := l14 h0).
 apply t2. exact h1. exact h2.
Qed.
Lemma l7 : s1 -> s33.
Proof.
 intros h0.
 assert (h1 := l8 h0).
 assert (h2 := l13 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i3))) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i4))) (Tatom false (Abnd 5%nat i5))) (Tatom false (Abnd 4%nat i6))) (Tatom false (Abnd 6%nat i7))) (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i3)) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i4))) (Tatom false (Abnd 5%nat i5))) (Tatom false (Abnd 4%nat i6))) (Tatom false (Abnd 6%nat i7))) (Abnd 0%nat i1) (List.cons _raw (List.cons _prod (List.cons r4 (List.cons _added (List.cons _delta (List.cons r1 (List.cons r22 List.nil))))))) h2 h1 _) ; finalize.
Qed.
Definition p14 := BND _prod i1. (* BND(prod, [-1.15293e+18, 0]) *)
Lemma t3 : p13 -> p14.
Proof.
 intros h0.
 refine (float_round_ne _ _ _raw i1 i1 h0 _) ; finalize.
Qed.
Lemma l15 : s1 -> p14 (* BND(prod, [-1.15293e+18, 0]) *).
Proof.
 intros h0.
 assert (h1 := l13 h0).
 apply t3. exact h1.
Qed.
Lemma l6 : s1 -> s28.
Proof.
 intros h0.
 assert (h1 := l7 h0).
 assert (h2 := l15 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i4))) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i5))) (Tatom false (Abnd 3%nat i6))) (Tatom false (Abnd 5%nat i7))) (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i4)) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i4))) (Tatom false (Abnd 4%nat i5))) (Tatom false (Abnd 3%nat i6))) (Tatom false (Abnd 5%nat i7))) (Abnd 0%nat i1) (List.cons _prod (List.cons r4 (List.cons _added (List.cons _delta (List.cons r1 (List.cons r22 List.nil)))))) h2 h1 _) ; finalize.
Qed.
Definition f10 := Float2 (1) (-1).
Definition i8 := makepairF f1 f10.
Definition p15 := BND r4 i8. (* BND(prod + 5e-1, [-1.15293e+18, 0.5]) *)
Definition i9 := makepairF f10 f10.
Definition p16 := BND r10 i9. (* BND(5e-1, [0.5, 0.5]) *)
Lemma t4 : p16.
Proof.
 refine (constant10 _ i9 _) ; finalize.
Qed.
Lemma l17 : s1 -> p16 (* BND(5e-1, [0.5, 0.5]) *).
Proof.
 intros h0.
 apply t4.
Qed.
Lemma t5 : p14 -> p16 -> p15.
Proof.
 intros h0 h1.
 refine (add _prod r10 i1 i9 i8 h0 h1 _) ; finalize.
Qed.
Lemma l16 : s1 -> p15 (* BND(prod + 5e-1, [-1.15293e+18, 0.5]) *).
Proof.
 intros h0.
 assert (h1 := l15 h0).
 assert (h2 := l17 h0).
 apply t5. exact h1. exact h2.
Qed.
Lemma l5 : s1 -> s24.
Proof.
 intros h0.
 assert (h1 := l6 h0).
 assert (h2 := l16 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i4)) (Tatom false (Abnd 1%nat i4))) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i5))) (Tatom false (Abnd 2%nat i6))) (Tatom false (Abnd 4%nat i7))) (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i4)) (Tatom false (Abnd 2%nat i4))) (Tatom false (Abnd 3%nat i5))) (Tatom false (Abnd 2%nat i6))) (Tatom false (Abnd 4%nat i7))) (Abnd 0%nat i8) (List.cons r4 (List.cons _added (List.cons _delta (List.cons r1 (List.cons r22 List.nil))))) h2 h1 _) ; finalize.
Qed.
Definition p17 := BND _added i8. (* BND(added, [-1.15293e+18, 0.5]) *)
Lemma t6 : p15 -> p17.
Proof.
 intros h0.
 refine (float_round_ne _ _ r4 i8 i8 h0 _) ; finalize.
Qed.
Lemma l18 : s1 -> p17 (* BND(added, [-1.15293e+18, 0.5]) *).
Proof.
 intros h0.
 assert (h1 := l16 h0).
 apply t6. exact h1.
Qed.
Lemma l4 : s1 -> s21.
Proof.
 intros h0.
 assert (h1 := l5 h0).
 assert (h2 := l18 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i4)) (Tatom false (Abnd 1%nat i4))) (Tatom false (Abnd 2%nat i5))) (Tatom false (Abnd 1%nat i6))) (Tatom false (Abnd 3%nat i7))) (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 1%nat i4)) (Tatom false (Abnd 2%nat i5))) (Tatom false (Abnd 1%nat i6))) (Tatom false (Abnd 3%nat i7))) (Abnd 0%nat i8) (List.cons _added (List.cons _delta (List.cons r1 (List.cons r22 List.nil)))) h2 h1 _) ; finalize.
Qed.
Definition p18 := BND _delta i1. (* BND(delta, [-1.15293e+18, 0]) *)
Lemma t7 : p17 -> p18.
Proof.
 intros h0.
 refine (fixed_round_dn _ _added i8 i1 h0 _) ; finalize.
Qed.
Lemma l19 : s1 -> p18 (* BND(delta, [-1.15293e+18, 0]) *).
Proof.
 intros h0.
 assert (h1 := l18 h0).
 apply t7. exact h1.
Qed.
Lemma l3 : s1 -> s20.
Proof.
 intros h0.
 assert (h1 := l4 h0).
 assert (h2 := l19 h0).
 refine (simplify (Ttree false (Ttree false (Ttree false (Tatom false (Abnd 0%nat i4)) (Tatom false (Abnd 1%nat i5))) (Tatom false (Abnd 0%nat i6))) (Tatom false (Abnd 2%nat i7))) (Ttree false (Tatom false (Abnd 1%nat i5)) (Tatom false (Abnd 2%nat i7))) (Abnd 0%nat i1) (List.cons _delta (List.cons r1 (List.cons r22 List.nil))) h2 h1 _) ; finalize.
Qed.
Definition f11 := Float2 (-385) (-1).
Definition f12 := Float2 (385) (-1).
Definition i10 := makepairF f11 f12.
Definition p19 := BND r1 i10. (* BND(delta - ideal, [-192.5, 192.5]) *)
Definition p20 := r1 = r12. (* EQL(delta - ideal, delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n + 5e-1) *)
Lemma t8 : p20.
Proof.
 refine (b1) ; finalize.
Qed.
Lemma l21 : s1 -> p20 (* EQL(delta - ideal, delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n + 5e-1) *).
Proof.
 intros h0.
 apply t8.
Qed.
Definition p21 := BND r12 i10. (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n + 5e-1, [-192.5, 192.5]) *)
Definition f13 := Float2 (-193) (0).
Definition f14 := Float2 (3) (6).
Definition i11 := makepairF f13 f14.
Definition p22 := BND r13 i11. (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n, [-193, 192]) *)
Definition f15 := Float2 (-129) (0).
Definition f16 := Float2 (1) (7).
Definition i12 := makepairF f15 f16.
Definition p23 := BND r14 i12. (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw), [-129, 128]) *)
Definition f17 := Float2 (-65) (0).
Definition f18 := Float2 (1) (6).
Definition i13 := makepairF f17 f18.
Definition p24 := BND r15 i13. (* BND(delta - added + (added - (prod + 5e-1)), [-65, 64]) *)
Definition f19 := Float2 (-1) (0).
Definition i14 := makepairF f19 f2.
Definition p25 := BND r16 i14. (* BND(delta - added, [-1, 0]) *)
Lemma t9 : p25.
Proof.
 refine (fixed_error_dn _ _ i14 _) ; finalize.
Qed.
Lemma l26 : s1 -> p25 (* BND(delta - added, [-1, 0]) *).
Proof.
 intros h0.
 apply t9.
Qed.
Definition f20 := Float2 (-1) (6).
Definition i15 := makepairF f20 f18.
Definition p26 := BND r17 i15. (* BND(added - (prod + 5e-1), [-64, 64]) *)
Definition f21 := Float2 (18014398509481985) (6).
Definition i16 := makepairF f2 f21.
Definition p27 := ABS r4 i16. (* ABS(prod + 5e-1, [0, 1.15293e+18]) *)
Definition i17 := makepairF f2 f5.
Definition p28 := ABS _prod i17. (* ABS(prod, [-0, 1.15293e+18]) *)
Lemma t10 : p14 -> p28.
Proof.
 intros h0.
 refine (abs_of_bnd_n _prod i1 i17 h0 _) ; finalize.
Qed.
Lemma l29 : s1 -> p28 (* ABS(prod, [-0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l15 h0).
 apply t10. exact h1.
Qed.
Definition i18 := makepairF f10 f3.
Definition p29 := ABS r10 i18. (* ABS(5e-1, [0.5, 1]) *)
Definition p30 := BND r10 i18. (* BND(5e-1, [0.5, 1]) *)
Lemma t11 : p30 -> p29.
Proof.
 intros h0.
 refine (abs_of_bnd_p r10 i18 i18 h0 _) ; finalize.
Qed.
Lemma l30 : s1 -> p29 (* ABS(5e-1, [0.5, 1]) *).
Proof.
 intros h0.
 assert (h1 := l17 h0).
 apply t11. refine (subset r10 i9 i18 h1 _) ; finalize.
Qed.
Lemma t12 : p28 -> p29 -> p27.
Proof.
 intros h0 h1.
 refine (add_aa_o _prod r10 i17 i18 i16 h0 h1 _) ; finalize.
Qed.
Lemma l28 : s1 -> p27 (* ABS(prod + 5e-1, [0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l29 h0).
 assert (h2 := l30 h0).
 apply t12. exact h1. exact h2.
Qed.
Lemma t13 : p27 -> p26.
Proof.
 intros h0.
 refine (float_absolute_wide_ne _ _ r4 i16 i15 h0 _) ; finalize.
Qed.
Lemma l27 : s1 -> p26 (* BND(added - (prod + 5e-1), [-64, 64]) *).
Proof.
 intros h0.
 assert (h1 := l28 h0).
 apply t13. exact h1.
Qed.
Lemma t14 : p25 -> p26 -> p24.
Proof.
 intros h0 h1.
 refine (add r16 r17 i14 i15 i13 h0 h1 _) ; finalize.
Qed.
Lemma l25 : s1 -> p24 (* BND(delta - added + (added - (prod + 5e-1)), [-65, 64]) *).
Proof.
 intros h0.
 assert (h1 := l26 h0).
 assert (h2 := l27 h0).
 apply t14. exact h1. exact h2.
Qed.
Definition p31 := BND r18 i15. (* BND(prod - raw, [-64, 64]) *)
Definition p32 := ABS _raw i17. (* ABS(raw, [-0, 1.15293e+18]) *)
Definition p33 := ABS _f i17. (* ABS(f, [-0, 1.15293e+18]) *)
Lemma t15 : p12 -> p33.
Proof.
 intros h0.
 refine (abs_of_bnd_n _f i1 i17 h0 _) ; finalize.
Qed.
Lemma l33 : s1 -> p33 (* ABS(f, [-0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l10 h0).
 apply t15. exact h1.
Qed.
Definition p34 := ABS _n i2. (* ABS(n, [1, 1.34218e+08]) *)
Lemma t16 : p2 -> p34.
Proof.
 intros h0.
 refine (abs_of_bnd_p _n i2 i2 h0 _) ; finalize.
Qed.
Lemma l34 : s1 -> p34 (* ABS(n, [1, 1.34218e+08]) *).
Proof.
 intros h0.
 assert (h1 := l14 h0).
 apply t16. exact h1.
Qed.
Lemma t17 : p33 -> p34 -> p32.
Proof.
 intros h0 h1.
 refine (div_aa _f _n i17 i2 i17 h0 h1 _) ; finalize.
Qed.
Lemma l32 : s1 -> p32 (* ABS(raw, [-0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l33 h0).
 assert (h2 := l34 h0).
 apply t17. exact h1. exact h2.
Qed.
Lemma t18 : p32 -> p31.
Proof.
 intros h0.
 refine (float_absolute_wide_ne _ _ _raw i17 i15 h0 _) ; finalize.
Qed.
Lemma l31 : s1 -> p31 (* BND(prod - raw, [-64, 64]) *).
Proof.
 intros h0.
 assert (h1 := l32 h0).
 apply t18. exact h1.
Qed.
Lemma t19 : p24 -> p31 -> p23.
Proof.
 intros h0 h1.
 refine (add r15 r18 i13 i15 i12 h0 h1 _) ; finalize.
Qed.
Lemma l24 : s1 -> p23 (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw), [-129, 128]) *).
Proof.
 intros h0.
 assert (h1 := l25 h0).
 assert (h2 := l31 h0).
 apply t19. exact h1. exact h2.
Qed.
Definition p35 := BND r19 i15. (* BND((f - i) / n, [-64, 64]) *)
Definition p36 := BND r20 i15. (* BND(f - i, [-64, 64]) *)
Definition p37 := ABS _i i17. (* ABS(i, [-0, 1.15293e+18]) *)
Lemma t20 : p1 -> p37.
Proof.
 intros h0.
 refine (abs_of_bnd_n _i i1 i17 h0 _) ; finalize.
Qed.
Lemma l37 : s1 -> p37 (* ABS(i, [-0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l11 h0).
 apply t20. exact h1.
Qed.
Lemma t21 : p37 -> p36.
Proof.
 intros h0.
 refine (float_absolute_wide_ne _ _ _i i17 i15 h0 _) ; finalize.
Qed.
Lemma l36 : s1 -> p36 (* BND(f - i, [-64, 64]) *).
Proof.
 intros h0.
 assert (h1 := l37 h0).
 apply t21. exact h1.
Qed.
Lemma t22 : p36 -> p2 -> p35.
Proof.
 intros h0 h1.
 refine (div_op r20 _n i15 i2 i15 h0 h1 _) ; finalize.
Qed.
Lemma l35 : s1 -> p35 (* BND((f - i) / n, [-64, 64]) *).
Proof.
 intros h0.
 assert (h1 := l36 h0).
 assert (h2 := l14 h0).
 apply t22. exact h1. exact h2.
Qed.
Lemma t23 : p23 -> p35 -> p22.
Proof.
 intros h0 h1.
 refine (add r14 r19 i12 i15 i11 h0 h1 _) ; finalize.
Qed.
Lemma l23 : s1 -> p22 (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n, [-193, 192]) *).
Proof.
 intros h0.
 assert (h1 := l24 h0).
 assert (h2 := l35 h0).
 apply t23. exact h1. exact h2.
Qed.
Lemma t24 : p22 -> p16 -> p21.
Proof.
 intros h0 h1.
 refine (add r13 r10 i11 i9 i10 h0 h1 _) ; finalize.
Qed.
Lemma l22 : s1 -> p21 (* BND(delta - added + (added - (prod + 5e-1)) + (prod - raw) + (f - i) / n + 5e-1, [-192.5, 192.5]) *).
Proof.
 intros h0.
 assert (h1 := l23 h0).
 assert (h2 := l17 h0).
 apply t24. exact h1. exact h2.
Qed.
Lemma t25 : p20 -> p21 -> p19.
Proof.
 intros h0 h1.
 refine (bnd_rewrite r1 r12 i10 h0 h1) ; finalize.
Qed.
Lemma l20 : s1 -> p19 (* BND(delta - ideal, [-192.5, 192.5]) *).
Proof.
 intros h0.
 assert (h1 := l21 h0).
 assert (h2 := l22 h0).
 apply t25. exact h1. exact h2.
Qed.
Lemma l2 : s1 -> s19.
Proof.
 intros h0.
 assert (h1 := l3 h0).
 assert (h2 := l20 h0).
 refine (simplify (Ttree false (Tatom false (Abnd 0%nat i5)) (Tatom false (Abnd 1%nat i7))) (Tatom false (Abnd 1%nat i7)) (Abnd 0%nat i10) (List.cons r1 (List.cons r22 List.nil)) h2 h1 _) ; finalize.
Qed.
Definition f22 := Float2 (1152921496016912577) (0).
Definition i19 := makepairF f11 f22.
Definition p38 := BND r22 i19. (* BND(delta - i, [-192.5, 1.15293e+18]) *)
Definition p39 := r22 = r23. (* EQL(delta - i, delta - ideal + (ideal - i)) *)
Lemma t26 : p39.
Proof.
 refine (b3) ; finalize.
Qed.
Lemma l39 : s1 -> p39 (* EQL(delta - i, delta - ideal + (ideal - i)) *).
Proof.
 intros h0.
 apply t26.
Qed.
Definition p40 := BND r23 i19. (* BND(delta - ideal + (ideal - i), [-192.5, 1.15293e+18]) *)
Definition f23 := Float2 (134217727) (33).
Definition i20 := makepairF f2 f23.
Definition p41 := BND r24 i20. (* BND(ideal - i, [0, 1.15293e+18]) *)
Definition p42 := r24 = r25. (* EQL(ideal - i, i * (1 / n - 1)) *)
Lemma t27 : p42.
Proof.
 refine (b4) ; finalize.
Qed.
Lemma l42 : s1 -> p42 (* EQL(ideal - i, i * (1 / n - 1)) *).
Proof.
 intros h0.
 apply t27.
Qed.
Definition p43 := BND r25 i20. (* BND(i * (1 / n - 1), [0, 1.15293e+18]) *)
Definition f24 := Float2 (-134217727) (-27).
Definition i21 := makepairF f24 f2.
Definition p44 := BND r26 i21. (* BND(1 / n - 1, [-1, 0]) *)
Definition f25 := Float2 (1) (-27).
Definition i22 := makepairF f25 f3.
Definition p45 := BND r27 i22. (* BND(1 / n, [7.45058e-09, 1]) *)
Definition i23 := makepairF f3 f3.
Definition p46 := BND r28 i23. (* BND(1, [1, 1]) *)
Lemma t28 : p46.
Proof.
 refine (constant1 _ i23 _) ; finalize.
Qed.
Lemma l46 : s1 -> p46 (* BND(1, [1, 1]) *).
Proof.
 intros h0.
 apply t28.
Qed.
Lemma t29 : p46 -> p2 -> p45.
Proof.
 intros h0 h1.
 refine (div_pp r28 _n i23 i2 i22 h0 h1 _) ; finalize.
Qed.
Lemma l45 : s1 -> p45 (* BND(1 / n, [7.45058e-09, 1]) *).
Proof.
 intros h0.
 assert (h1 := l46 h0).
 assert (h2 := l14 h0).
 apply t29. exact h1. exact h2.
Qed.
Lemma t30 : p45 -> p46 -> p44.
Proof.
 intros h0 h1.
 refine (sub r27 r28 i22 i23 i21 h0 h1 _) ; finalize.
Qed.
Lemma l44 : s1 -> p44 (* BND(1 / n - 1, [-1, 0]) *).
Proof.
 intros h0.
 assert (h1 := l45 h0).
 assert (h2 := l46 h0).
 apply t30. exact h1. exact h2.
Qed.
Lemma t31 : p1 -> p44 -> p43.
Proof.
 intros h0 h1.
 refine (mul_nn _i r26 i1 i21 i20 h0 h1 _) ; finalize.
Qed.
Lemma l43 : s1 -> p43 (* BND(i * (1 / n - 1), [0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l11 h0).
 assert (h2 := l44 h0).
 apply t31. exact h1. exact h2.
Qed.
Lemma t32 : p42 -> p43 -> p41.
Proof.
 intros h0 h1.
 refine (bnd_rewrite r24 r25 i20 h0 h1) ; finalize.
Qed.
Lemma l41 : s1 -> p41 (* BND(ideal - i, [0, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l42 h0).
 assert (h2 := l43 h0).
 apply t32. exact h1. exact h2.
Qed.
Definition f26 := Float2 (193) (0).
Definition i24 := makepairF f11 f26.
Definition p47 := BND r1 i24. (* BND(delta - ideal, [-192.5, 193]) *)
Lemma t33 : p47 -> p41 -> p40.
Proof.
 intros h0 h1.
 refine (add r1 r24 i24 i20 i19 h0 h1 _) ; finalize.
Qed.
Lemma l40 : s1 -> p40 (* BND(delta - ideal + (ideal - i), [-192.5, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l20 h0).
 assert (h2 := l41 h0).
 apply t33. refine (subset r1 i10 i24 h1 _) ; finalize. exact h2.
Qed.
Lemma t34 : p39 -> p40 -> p38.
Proof.
 intros h0 h1.
 refine (bnd_rewrite r22 r23 i19 h0 h1) ; finalize.
Qed.
Lemma l38 : s1 -> p38 (* BND(delta - i, [-192.5, 1.15293e+18]) *).
Proof.
 intros h0.
 assert (h1 := l39 h0).
 assert (h2 := l40 h0).
 apply t34. exact h1. exact h2.
Qed.
Lemma l1 : s1 -> False.
Proof.
 intros h0.
 assert (h1 := l2 h0).
 assert (h2 := l38 h0).
 refine (simplify (Tatom false (Abnd 0%nat i7)) Tfalse (Abnd 0%nat i19) (List.cons r22 List.nil) h2 h1 _) ; finalize.
Qed.
End Generated_by_Gappa.
Print Assumptions l1.
Check l1.
