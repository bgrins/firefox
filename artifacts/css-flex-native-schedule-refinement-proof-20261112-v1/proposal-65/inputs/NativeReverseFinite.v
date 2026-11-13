Require Import Reals ZArith List Bool Lia.
Require Import PrefixTarget ReverseTarget ReverseSign SignModel.
Require Import NativeFloatModel NativeState NativeReverseModel NativeFloatProof NativeProducerRows NativeItemProjection NativeRefinementSpec.
Import ListNotations.
Module NativeReverseFinite.
Import NativeSchedule.
Definition items (grow : bool) (rs : list (nat*Row)) :=
  map (fun p => (fst p,NativeItemProjection.item grow (snd p))) rs.
Lemma loop_correspondence : forall rs grow left largest count free total reports,
  Forall (fun p => NativeProducerRows.Shared (snd p)) rs ->
  ReverseTarget.FreeDomain free ->
  exists out,
    NativeReverse.loop grow true largest left count free total reports rs = Some out /\
    Forall2 NativeRefinementTarget.EventMatches (NativeReverse.events out)
      (ReverseTarget.events (ReverseTarget.reverseLoop left free (items grow rs))) /\
    NativeReverse.finalFree out = ReverseTarget.finalFree (ReverseTarget.reverseLoop left free (items grow rs)) /\
    NativeReverse.left out = ReverseTarget.reverseRemaining (ReverseTarget.reverseLoop left free (items grow rs)).
Proof.
  induction rs as [|[i r] tail IH]; intros grow left largest count free total reports Shared Free.
  - destruct left; (eexists; split; [reflexivity|]; cbn; repeat split; constructor).
  - destruct left as [|k].
    + eexists; split; [reflexivity|]; cbn; repeat split; constructor.
    + inversion Shared as [|head rest Head Tail]; subst.
      destruct (frozen r) eqn:Frozen.
      * destruct (IH grow (S k) largest count free total reports Tail Free)
          as [out [Run [Events [Final Left]]]].
        cbn [NativeReverse.loop]; rewrite Frozen,Run; cbn.
        eexists; split; [reflexivity|].
        cbn [items map ReverseTarget.reverseLoop NativeItemProjection.item SignHistory.asItem projectedRow].
        rewrite Frozen; cbn. repeat split; assumption.
      * specialize (Head ltac:(assumption || reflexivity)). destruct Head as [Finite Range].
        pose proof (proj2 (proj2 NativeFloatProof.float_target) free (share r) Free Finite Range) as Delta.
        destruct (ReverseSign.remainder_target free (NativeFloat.value (share r)) Free Range)
          as [_ [NextFree _]].
        set (d := ReverseTarget.deltaAt free (NativeFloat.value (share r))) in *.
        set (raw := (main r+d)%Z).
        set (stored := project32 raw).
        destruct (IH grow k largest count (free-d)%Z (total+(stored-raw))%Z
          (updateReport i d reports) Tail NextFree) as [out [Run [Events [Final Left]]]].
        cbn [NativeReverse.loop]; rewrite Frozen.
        unfold NativeReverse.deltaFor; rewrite Delta; cbn. fold raw stored. rewrite Run.
        eexists; split; [reflexivity|].
        cbn [items map ReverseTarget.reverseLoop NativeItemProjection.item SignHistory.asItem projectedRow].
        rewrite Frozen; cbn.
        split.
        -- constructor; [unfold NativeRefinementTarget.EventMatches; cbn; repeat split; reflexivity|exact Events].
        -- split; assumption.
Qed.
Print Assumptions loop_correspondence.
End NativeReverseFinite.
