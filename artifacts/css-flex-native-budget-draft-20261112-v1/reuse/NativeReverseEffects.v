Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel.
Require Import NativeProjectionFlags NativeReversePositions NativeIndexed.
Import ListNotations.
Module NativeReverseEffects.
Import NativeSchedule.
Open Scope Z_scope.
Definition atDelta (i : nat) (es : list NativeReverse.Event) :=
  fold_right (fun e acc => (if Nat.eqb (NativeReverse.ordinal e) i then NativeReverse.delta e else 0)+acc) 0 es.
Definition effect (es : list NativeReverse.Event) (p : nat*Row) :=
  (fst p, if frozen (snd p) then snd p else
    NativeProjectionFlags.projected (snd p) (main (snd p)+atDelta (fst p) es)).
Definition ActiveFits (r : Row) := frozen r=false -> -2147483648 <= main r <= 2147483647.
Lemma project_identity : forall r,
  -2147483648 <= main r <= 2147483647 -> NativeProjectionFlags.projected r (main r)=r.
Proof.
  intros [s m f share lo hi] Bounds.
  unfold NativeProjectionFlags.projected,project32; cbn in *.
  rewrite Z.min_l,Z.max_r by lia.
  assert (L : Z.ltb m (-2147483648)=false) by (apply Z.ltb_ge; lia).
  assert (H : Z.ltb 2147483647 m=false) by (apply Z.ltb_ge; lia).
  rewrite L,H,!Bool.orb_false_r; reflexivity.
Qed.
Lemma empty_effect : forall rs,
  Forall (fun p => ActiveFits (snd p)) rs -> map (effect []) rs=rs.
Proof.
  intros rs Fits; induction Fits; cbn [map]; [reflexivity|].
  destruct x as [i r]. unfold effect; cbn [fst snd atDelta fold_right].
  rewrite Z.add_0_r. destruct (frozen r) eqn:F; rewrite IHFits; [reflexivity|].
  rewrite project_identity by (apply H; exact F). reflexivity.
Qed.
Lemma delta_absent : forall es i,
  ~ In i (map NativeReverse.ordinal es) -> atDelta i es=0.
Proof.
  induction es as [|e tail IH]; intros i Absent; [reflexivity|].
  cbn [atDelta fold_right]. destruct (Nat.eqb (NativeReverse.ordinal e) i) eqn:E.
  - apply Nat.eqb_eq in E. exfalso; apply Absent; left; exact E.
  - rewrite IH; [lia|intro Member; apply Absent; right; exact Member].
Qed.
Lemma delta_head_other : forall e es i,
  NativeReverse.ordinal e <> i -> atDelta i (e::es)=atDelta i es.
Proof.
  intros e es i Different. unfold atDelta; cbn.
  assert (E : Nat.eqb (NativeReverse.ordinal e) i=false) by (apply Nat.eqb_neq; exact Different).
  rewrite E; lia.
Qed.
Lemma loop_rows : forall rs grow finite largest left count free acc reports out,
  NoDup (map fst rs) -> Forall (fun p => ActiveFits (snd p)) rs ->
  NativeReverse.loop grow finite largest left count free acc reports rs=Some out ->
  NativeReverse.indexedRows out=map (effect (NativeReverse.events out)) rs.
Proof.
  induction rs as [|[i r] tail IH]; intros grow finite largest left count free acc reports out Unique Fits Run.
  - destruct left; inversion Run; reflexivity.
  - destruct left as [|k].
    + inversion Run; subst out; cbn; symmetry; apply empty_effect; exact Fits.
    + inversion Unique as [|head rest Absent TailUnique]; subst.
      inversion Fits as [|head rest HeadFits TailFits]; subst.
      cbn [NativeReverse.loop] in Run. destruct (frozen r) eqn:Frozen.
      * destruct (NativeReverse.loop grow finite largest (S k) count free acc reports tail)
          as [next|] eqn:Next; [|discriminate].
        pose proof (IH grow finite largest (S k) count free acc reports next TailUnique TailFits Next) as Rows.
        inversion Run; subst out; cbn [map effect fst snd]; rewrite Frozen,Rows; reflexivity.
      * destruct (NativeReverse.deltaFor grow finite largest count free r)
          as [[d remaining]|] eqn:Delta; [|discriminate].
        destruct (NativeReverse.loop grow finite largest k remaining (free-d)
          (acc+(project32 (main r+d)-(main r+d))) (updateReport i d reports) tail)
          as [next|] eqn:Next; [|discriminate].
        pose proof (IH grow finite largest k remaining (free-d)
          (acc+(project32 (main r+d)-(main r+d))) (updateReport i d reports) next TailUnique TailFits Next) as Rows.
        pose proof (NativeReversePositions.loop_event_membership tail grow finite largest k remaining
          (free-d) (acc+(project32 (main r+d)-(main r+d))) (updateReport i d reports) next Next) as Members.
        assert (NoHead : atDelta i (NativeReverse.events next)=0).
        { apply delta_absent. intro Member. apply in_map_iff in Member.
          destruct Member as [e [E Hin]]. rewrite Forall_forall in Members.
          apply Absent. rewrite <- E. exact (Members e Hin). }
        inversion Run; subst out; cbn [map]. f_equal.
        -- unfold effect; cbn [fst snd]. rewrite Frozen.
           cbn [atDelta fold_right NativeReverse.ordinal NativeReverse.delta]. rewrite Nat.eqb_refl.
           fold (atDelta i (NativeReverse.events next)). rewrite NoHead,Z.add_0_r. reflexivity.
        -- rewrite Rows. apply map_ext_in.
           intros [j row] Member. unfold effect; cbn [fst snd].
           f_equal. destruct (frozen row); [reflexivity|].
           rewrite delta_head_other; [reflexivity|]. cbn. intro E; subst j.
           apply Absent. apply in_map. exact Member.
Qed.
Lemma run_rows : forall grow produced count free reports out,
  Forall ActiveFits (NativeProducer.producedRows produced) ->
  NativeReverse.run grow produced count free reports=Some out ->
  NativeReverse.restored out=map (fun p => snd (effect (NativeReverse.events out) p))
    (NativeIndexed.indexed (NativeProducer.producedRows produced)).
Proof.
  intros grow produced count free reports out Fits Run.
  assert (Unique : NoDup (map fst (rev (NativeIndexed.indexed (NativeProducer.producedRows produced))))).
  { rewrite map_rev. apply NoDup_rev. apply NativeIndexed.unique. }
  assert (Pairs : Forall (fun p => ActiveFits (snd p))
    (rev (NativeIndexed.indexed (NativeProducer.producedRows produced)))).
  { apply Forall_rev. apply Forall_forall. intros [i r] Member.
    apply in_combine_r in Member. rewrite Forall_forall in Fits. apply Fits; exact Member. }
  pose proof (loop_rows _ _ _ _ _ _ _ _ _ _ Unique Pairs Run) as Rows.
  unfold NativeReverse.restored. rewrite Rows,<-map_rev,rev_involutive,map_map. reflexivity.
Qed.
Print Assumptions project_identity.
Print Assumptions empty_effect.
Print Assumptions delta_absent.
Print Assumptions delta_head_other.
Print Assumptions loop_rows.
Print Assumptions run_rows.
End NativeReverseEffects.
