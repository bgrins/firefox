Require Import Gappa.Gappa_library.
Section Generated_by_Gappa.
Variable _factor : R.
Definition f1 := Float2 (0) (0).
Definition f2 := Float2 (1) (128).
Definition i1 := makepairF f1 f2.
Definition p1 := BND _factor i1. (* BND(factor, [0, 3.40283e+38]) *)
Variable _base : R.
Definition f3 := Float2 (1) (31).
Definition i2 := makepairF f1 f3.
Definition p2 := BND _base i2. (* BND(base, [0, 2.14749e+09]) *)
Definition s2 := p1 /\ p2.
Definition r3 := (_factor * _base)%R.
Definition f4 := Float2 (1) (159).
Definition i3 := makepairF f1 f4.
Definition p3 := BND r3 i3. (* BND(factor * base, [0, 7.30751e+47]) *)
Definition s4 := not p3.
Definition _weight := (rounding_float rndNE (53)%positive (-1074)%Z) r3.
Definition p4 := BND _weight i3. (* BND(weight, [0, 7.30751e+47]) *)
Definition s5 := not p4.
Definition s3 := s4 \/ s5.
Definition s1 := s2 /\ s3.
Lemma l3 : s1 -> s3.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj2 h1).
Qed.
Lemma l6 : s1 -> s2.
Proof.
 intros h0.
 assert (h1 := h0).
 exact (proj1 h1).
Qed.
Lemma l5 : s1 -> p1 (* BND(factor, [0, 3.40283e+38]) *).
Proof.
 intros h0.
 assert (h1 := l6 h0).
 exact (proj1 h1).
Qed.
Lemma l7 : s1 -> p2 (* BND(base, [0, 2.14749e+09]) *).
Proof.
 intros h0.
 assert (h1 := l6 h0).
 exact (proj2 h1).
Qed.
Lemma t1 : p1 -> p2 -> p3.
Proof.
 intros h0 h1.
 refine (mul_pp _factor _base i1 i2 i3 h0 h1 _) ; finalize.
Qed.
Lemma l4 : s1 -> p3 (* BND(factor * base, [0, 7.30751e+47]) *).
Proof.
 intros h0.
 assert (h1 := l5 h0).
 assert (h2 := l7 h0).
 apply t1. exact h1. exact h2.
Qed.
Lemma l2 : s1 -> s5.
Proof.
 intros h0.
 assert (h1 := l3 h0).
 assert (h2 := l4 h0).
 refine (simplify (Ttree false (Tatom false (Abnd 0%nat i3)) (Tatom false (Abnd 1%nat i3))) (Tatom false (Abnd 1%nat i3)) (Abnd 0%nat i3) (List.cons r3 (List.cons _weight List.nil)) h2 h1 _) ; finalize.
Qed.
Lemma t2 : p3 -> p4.
Proof.
 intros h0.
 refine (float_round_ne _ _ r3 i3 i3 h0 _) ; finalize.
Qed.
Lemma l8 : s1 -> p4 (* BND(weight, [0, 7.30751e+47]) *).
Proof.
 intros h0.
 assert (h1 := l4 h0).
 apply t2. exact h1.
Qed.
Lemma l1 : s1 -> False.
Proof.
 intros h0.
 assert (h1 := l2 h0).
 assert (h2 := l8 h0).
 refine (simplify (Tatom false (Abnd 0%nat i3)) Tfalse (Abnd 0%nat i3) (List.cons _weight List.nil) h2 h1 _) ; finalize.
Qed.
End Generated_by_Gappa.
