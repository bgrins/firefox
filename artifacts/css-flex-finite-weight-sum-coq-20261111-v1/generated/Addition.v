Require Import Gappa.Gappa_library.
Section Generated_by_Gappa.
Variable _sum : R.
Variable _weight : R.
Definition _raw := (_sum + _weight)%R.
Definition _next := (rounding_float rndNE (53)%positive (-1074)%Z) _raw.
Definition r1 := (_next - _sum)%R.
Definition r7 := (_next - _raw)%R.
Definition r6 := (r7 + _weight)%R.
Hypothesis a1 : r1 = r6.
Lemma b1 : r1 = r6.
 apply a1.
Qed.
Definition f1 := Float2 (0) (0).
Definition f2 := Float2 (1) (192).
Definition i1 := makepairF f1 f2.
Definition p1 := BND _sum i1. (* BND(sum, [0, 6.27711e+57]) *)
Definition f3 := Float2 (1) (159).
Definition i2 := makepairF f1 f3.
Definition p2 := BND _weight i2. (* BND(weight, [0, 7.30751e+47]) *)
Definition s2 := p1 /\ p2.
Definition f4 := Float2 (1) (193).
Definition i3 := makepairF f1 f4.
Definition p3 := BND _raw i3. (* BND(raw, [0, 1.25543e+58]) *)
Definition s5 := not p3.
Definition p4 := BND _next i3. (* BND(next, [0, 1.25543e+58]) *)
Definition s6 := not p4.
Definition s4 := s5 \/ s6.
Definition f5 := Float2 (-1) (160).
Definition f6 := Float2 (1) (160).
Definition i4 := makepairF f5 f6.
Definition p5 := BND r1 i4. (* BND(next - sum, [-1.46151e+48, 1.46151e+48]) *)
Definition s7 := not p5.
Definition s3 := s4 \/ s7.
Definition s1 := s2 /\ s3.
Definition s8 := s6 \/ s7.
Lemma l4 : s1 -> s3.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj2 h1).
Qed.
Definition f7 := Float2 (8589934593) (159).
Definition i5 := makepairF f1 f7.
Definition p6 := BND _raw i5. (* BND(raw, [0, 6.27711e+57]) *)
Lemma l7 : s1 -> s2.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj1 h1).
Qed.
Lemma l6 : s1 -> p1 (* BND(sum, [0, 6.27711e+57]) *).
Proof.
 intros h0.
 assert (h1 := l7 h0).
 exact (proj1 h1).
Qed.
Lemma l8 : s1 -> p2 (* BND(weight, [0, 7.30751e+47]) *).
Proof.
 intros h0.
 assert (h1 := l7 h0).
 exact (proj2 h1).
Qed.
Lemma t1 : p1 -> p2 -> p6.
Proof.
 intros h0 h1.
 refine (add _sum _weight i1 i2 i5 h0 h1 _) ; finalize.
Qed.
Lemma l5 : s1 -> p6 (* BND(raw, [0, 6.27711e+57]) *).
Proof.
 intros h0.
 assert (h1 := l6 h0).
 assert (h2 := l8 h0).
 apply t1. exact h1. exact h2.
Qed.
Lemma l3 : s1 -> s8.
Proof.
 intros h0.
 assert (h1 := l4 h0).
 assert (h2 := l5 h0).
 refine (simplify (Ttree false (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i3))) (Tatom false (Abnd 2%nat i4))) (Ttree false (Tatom false (Abnd 1%nat i3)) (Tatom false (Abnd 2%nat i4))) (Abnd 0%nat i5) (List.cons _raw (List.cons _next (List.cons r1 List.nil))) h2 h1 _) ; finalize.
Qed.
Definition p7 := BND _next i5. (* BND(next, [0, 6.27711e+57]) *)
Lemma t2 : p6 -> p7.
Proof.
 intros h0.
 refine (float_round_ne _ _ _raw i5 i5 h0 _) ; finalize.
Qed.
Lemma l9 : s1 -> p7 (* BND(next, [0, 6.27711e+57]) *).
Proof.
 intros h0.
 assert (h1 := l5 h0).
 apply t2. exact h1.
Qed.
Lemma l2 : s1 -> s7.
Proof.
 intros h0.
 assert (h1 := l3 h0).
 assert (h2 := l9 h0).
 refine (simplify (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i4))) (Tatom false (Abnd 1%nat i4)) (Abnd 0%nat i5) (List.cons _next (List.cons r1 List.nil)) h2 h1 _) ; finalize.
Qed.
Definition f8 := Float2 (-1) (139).
Definition f9 := Float2 (1048577) (139).
Definition i6 := makepairF f8 f9.
Definition p8 := BND r1 i6. (* BND(next - sum, [-6.96899e+41, 7.30752e+47]) *)
Definition p9 := r1 = r6. (* EQL(next - sum, next - raw + weight) *)
Lemma t3 : p9.
Proof.
 refine (b1) ; finalize.
Qed.
Lemma l11 : s1 -> p9 (* EQL(next - sum, next - raw + weight) *).
Proof.
 intros h0.
 apply t3.
Qed.
Definition p10 := BND r6 i6. (* BND(next - raw + weight, [-6.96899e+41, 7.30752e+47]) *)
Definition f10 := Float2 (1) (139).
Definition i7 := makepairF f8 f10.
Definition p11 := BND r7 i7. (* BND(next - raw, [-6.96899e+41, 6.96899e+41]) *)
Definition p12 := ABS _raw i3. (* ABS(raw, [0, 1.25543e+58]) *)
Definition p13 := ABS _sum i1. (* ABS(sum, [0, 6.27711e+57]) *)
Lemma t4 : p1 -> p13.
Proof.
 intros h0.
 refine (abs_of_bnd_p _sum i1 i1 h0 _) ; finalize.
Qed.
Lemma l15 : s1 -> p13 (* ABS(sum, [0, 6.27711e+57]) *).
Proof.
 intros h0.
 assert (h1 := l6 h0).
 apply t4. exact h1.
Qed.
Definition p14 := ABS _weight i2. (* ABS(weight, [0, 7.30751e+47]) *)
Lemma t5 : p2 -> p14.
Proof.
 intros h0.
 refine (abs_of_bnd_p _weight i2 i2 h0 _) ; finalize.
Qed.
Lemma l16 : s1 -> p14 (* ABS(weight, [0, 7.30751e+47]) *).
Proof.
 intros h0.
 assert (h1 := l8 h0).
 apply t5. exact h1.
Qed.
Lemma t6 : p13 -> p14 -> p12.
Proof.
 intros h0 h1.
 refine (add_aa_o _sum _weight i1 i2 i3 h0 h1 _) ; finalize.
Qed.
Lemma l14 : s1 -> p12 (* ABS(raw, [0, 1.25543e+58]) *).
Proof.
 intros h0.
 assert (h1 := l15 h0).
 assert (h2 := l16 h0).
 apply t6. exact h1. exact h2.
Qed.
Lemma t7 : p12 -> p11.
Proof.
 intros h0.
 refine (float_absolute_wide_ne _ _ _raw i3 i7 h0 _) ; finalize.
Qed.
Lemma l13 : s1 -> p11 (* BND(next - raw, [-6.96899e+41, 6.96899e+41]) *).
Proof.
 intros h0.
 assert (h1 := l14 h0).
 apply t7. exact h1.
Qed.
Lemma t8 : p11 -> p2 -> p10.
Proof.
 intros h0 h1.
 refine (add r7 _weight i7 i2 i6 h0 h1 _) ; finalize.
Qed.
Lemma l12 : s1 -> p10 (* BND(next - raw + weight, [-6.96899e+41, 7.30752e+47]) *).
Proof.
 intros h0.
 assert (h1 := l13 h0).
 assert (h2 := l8 h0).
 apply t8. exact h1. exact h2.
Qed.
Lemma t9 : p9 -> p10 -> p8.
Proof.
 intros h0 h1.
 refine (bnd_rewrite r1 r6 i6 h0 h1) ; finalize.
Qed.
Lemma l10 : s1 -> p8 (* BND(next - sum, [-6.96899e+41, 7.30752e+47]) *).
Proof.
 intros h0.
 assert (h1 := l11 h0).
 assert (h2 := l12 h0).
 apply t9. exact h1. exact h2.
Qed.
Lemma l1 : s1 -> False.
Proof.
 intros h0.
 assert (h1 := l2 h0).
 assert (h2 := l10 h0).
 refine (simplify (Tatom false (Abnd 0%nat i4)) Tfalse (Abnd 0%nat i6) (List.cons r1 List.nil) h2 h1 _) ; finalize.
Qed.
End Generated_by_Gappa.
