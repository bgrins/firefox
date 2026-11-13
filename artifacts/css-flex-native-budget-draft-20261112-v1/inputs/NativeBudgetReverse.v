Require Import Reals ZArith List Bool Lia Psatz.
Require Import ReverseTarget SignModel NativeFloatModel NativeState NativeProducerModel NativeReverseModel.
Require Import NativeProducerRows NativeContraction NativeProjectionAlgebra NativeBudgetArithmetic.
Import ListNotations.
Module NativeBudgetReverse.
Import NativeSchedule NativeBudgetArithmetic.
Open Scope Z_scope.
Definition deltaMass (es : list NativeReverse.Event) :=
  fold_right (fun e sum => Z.abs (NativeReverse.delta e)+sum) 0 es.
Definition Input (p : nat*Row) := Good (snd p) /\ NativeProducerRows.Shared (snd p).
Definition Result (bound initialFree : Z) (out : NativeReverse.Result) :=
  Forall NativeReverse.FitsEvent (NativeReverse.events out) /\
  Forall (fun e => Z.abs (NativeReverse.totalAfter e)<=bound) (NativeReverse.events out) /\
  Z.abs (NativeReverse.violation out)+Z.abs (NativeReverse.finalFree out)<=bound /\
  deltaMass (NativeReverse.events out)+Z.abs (NativeReverse.finalFree out)=Z.abs initialFree /\
  Forall (fun p => Good (snd p)) (NativeReverse.indexedRows out).
Lemma delta_mass_map : forall es,
  deltaMass es=SignHistory.sumZ (map (fun e=>Z.abs (NativeReverse.delta e)) es).
Proof. induction es; cbn [deltaMass SignHistory.sumZ map fold_right]; [reflexivity|rewrite IHes; reflexivity]. Qed.
Lemma loop_budget : forall rs grow largest left count free acc reports out bound,
  0<=bound<=cap -> Z.abs acc+Z.abs free<=bound -> Forall Input rs ->
  NativeReverse.loop grow true largest left count free acc reports rs=Some out -> Result bound free out.
Proof.
  induction rs as [|[i r] tail IH]; intros grow largest left count free acc reports out bound Bound Budget GoodRows Run.
  - destruct left; inversion Run; subst out; unfold Result; cbn; repeat split; try constructor; lia.
  - destruct left as [|k].
    + inversion Run; subst out; unfold Result; cbn. split; [constructor|]. split; [constructor|].
      split; [exact Budget|]. split; [lia|]. eapply Forall_impl; [|exact GoodRows].
      intros pair G; exact (proj1 G).
    + inversion GoodRows as [|head rest Head Tail]; subst. destruct Head as [Good Shared].
      cbn [NativeReverse.loop] in Run. destruct (frozen r) eqn:Frozen.
      * destruct (NativeReverse.loop grow true largest (S k) count free acc reports tail)
          as [next|] eqn:Next; [|discriminate].
        destruct (IH grow largest (S k) count free acc reports next bound Bound Budget Tail Next)
          as [Events [Prefixes [Terminal [Mass Rows]]]].
        inversion Run; subst out; unfold Result; cbn. repeat split; try assumption.
        constructor; assumption.
      * specialize (Shared ltac:(assumption || reflexivity)). destruct Shared as [Finite Range].
        cbn [NativeReverse.deltaFor] in Run.
        destruct (NativeFloat.fractionDelta free (share r)) as [d|] eqn:Delta; [|discriminate].
        assert (Domain : ReverseTarget.FreeDomain free).
        { apply abs_domain. pose proof (Z.abs_nonneg acc); lia. }
        destruct (NativeContraction.delta_contraction free (share r) d Domain Finite Range Delta)
          as [Step [Remainder Split]].
        pose proof (NativeProjectionAlgebra.projection_correction_bound (main r) d (proj2 Good)) as Correction.
        set (raw := main r+d) in *.
        set (stored := project32 raw) in *.
        set (nextAcc := acc+(stored-raw)) in *.
        assert (NextBudget : Z.abs nextAcc+Z.abs (free-d)<=bound).
        { unfold nextAcc. pose proof (Z.abs_triangle acc (stored-raw)); lia. }
        destruct (NativeReverse.loop grow true largest k count (free-d) nextAcc (updateReport i d reports) tail)
          as [next|] eqn:Next; [|discriminate].
        destruct (IH grow largest k count (free-d) nextAcc (updateReport i d reports) next bound
          Bound NextBudget Tail Next) as [Events [Prefixes [Terminal [Mass Rows]]]].
        assert (FitsFree : Fits64 free) by (apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg acc); lia).
        assert (FitsDelta : Fits64 d) by (apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg acc); pose proof (Z.abs_nonneg (free-d)); lia).
        assert (FitsRemainder : Fits64 (free-d)) by (apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg acc); pose proof (Z.abs_nonneg d); lia).
        assert (FitsBefore : Fits64 (main r)) by (apply acquired_fits; exact (proj2 Good)).
        assert (FitsStored : Fits64 stored) by (apply acquired_fits; apply project_bounds).
        assert (FitsRaw : Fits64 raw).
        { apply abs_fits. pose proof (acquired_abs (main r) (proj2 Good)).
          pose proof (Z.abs_triangle (main r) d). unfold raw,cap in *.
          pose proof (Z.abs_nonneg acc); pose proof (Z.abs_nonneg (free-d)); lia. }
        assert (FitsCorrection : Fits64 (stored-raw)).
        { apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg acc); pose proof (Z.abs_nonneg (free-d)); lia. }
        assert (FitsAcc : Fits64 acc) by (apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg free); lia).
        assert (FitsNext : Fits64 nextAcc) by (apply abs_fits; unfold cap in Bound; pose proof (Z.abs_nonneg (free-d)); lia).
        inversion Run; subst out; unfold Result; cbn [NativeReverse.events NativeReverse.violation
          NativeReverse.finalFree NativeReverse.indexedRows deltaMass fold_right].
        split.
        -- constructor; [unfold NativeReverse.FitsEvent; cbn; repeat (constructor; [assumption|]); constructor|exact Events].
        -- split.
           ++ constructor; [cbn; pose proof (Z.abs_nonneg (free-d)); lia|exact Prefixes].
           ++ split; [exact Terminal|]. split; [lia|]. constructor; [|exact Rows].
              split; [exact (proj1 Good)|apply project_bounds].
Qed.
Lemma run_budget : forall grow produced count free reports out,
  Forall Good (NativeProducer.producedRows produced) ->
  Forall NativeProducerRows.Shared (NativeProducer.producedRows produced) ->
  NativeFloat.finite (NativeProducer.weightSum produced)=true -> ReverseTarget.FreeDomain free ->
  NativeReverse.run grow produced count free reports=Some out -> Result (Z.abs free) free out.
Proof.
  intros grow produced count free reports out GoodRows Shares Finite Domain Run.
  unfold NativeReverse.run in Run; rewrite Finite in Run.
  apply (loop_budget _ grow (NativeProducer.largest produced) _ _ free 0 reports out (Z.abs free)).
  - split; [apply Z.abs_nonneg|apply domain_abs; exact Domain].
  - cbn; lia.
  - apply Forall_rev. apply Forall_forall. intros [i r] Member.
    apply in_combine_r in Member. unfold Input; cbn. rewrite Forall_forall in GoodRows,Shares; split; auto.
  - exact Run.
Qed.
Lemma restored_good : forall bound free out, Result bound free out -> Forall Good (NativeReverse.restored out).
Proof.
  intros bound free out [_ [_ [_ [_ Rows]]]]. unfold NativeReverse.restored.
  apply Forall_map. apply Forall_rev. exact Rows.
Qed.
Print Assumptions delta_mass_map.
Print Assumptions loop_budget.
Print Assumptions run_budget.
Print Assumptions restored_good.
End NativeBudgetReverse.
