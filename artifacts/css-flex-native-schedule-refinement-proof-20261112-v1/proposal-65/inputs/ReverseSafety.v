Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import ConversionTarget PrefixTarget ReverseTarget ReverseSign ReverseBinding.
Import ListNotations.
Open Scope R_scope.

Lemma domain_fits : forall free, FreeDomain free -> Fits64 free.
Proof. unfold FreeDomain, Fits64. intros. lia. Qed.
Lemma loop_safety : forall xs left free,
  Forall (fun p => frozen (snd p) = false -> 0 <= stored (snd p) <= 1) xs ->
  FreeDomain free ->
  Forall BoundEvent (events (reverseLoop left free xs)) /\
  FreeDomain (finalFree (reverseLoop left free xs)) /\ Fits64 (finalFree (reverseLoop left free xs)).
Proof.
  induction xs as [|[i x] xs IH]; intros left free Hvalid Hfree; destruct left;
    cbn [reverseLoop events finalFree]; try (split; [constructor|split; [exact Hfree|apply domain_fits; exact Hfree]]).
  inversion Hvalid as [|p ps Hhead Htail]; subst.
  destruct (frozen x) eqn:Hx; cbn [events finalFree].
  - exact (IH (S left) free Htail Hfree).
  - assert (Hrange : 0 <= stored x <= 1) by (apply Hhead; exact Hx).
    destruct (remainder_target free (stored x) Hfree Hrange) as [Hbound [Hnext [Hd Ha]]].
    destruct (delta_envelope free (stored x) Hfree Hrange) as [Henv Hfit].
    specialize (IH left (free - producedDelta free x)%Z Htail Hnext).
    destruct IH as [He [Hf Hff]]. split; [|split; assumption].
    constructor; [|exact He]. unfold BoundEvent. cbn [beforeFree afterFree delta].
    split; [exact Hfree|]. split; [exact Hnext|]. split; [exact Henv|]. split; [exact Hd|exact Ha].
Qed.
Theorem reverse_safety_target : ReverseSafetyTarget.
Proof.
  intros xs free Ha Hfree. unfold reverseRun. destruct (Req_EM_T (total (run xs)) 0).
  - cbn [events finalFree]. split; [constructor|split; [exact Hfree|apply domain_fits; exact Hfree]].
  - apply loop_safety; [apply produced_ranges; exact Ha|exact Hfree].
Qed.

Print Assumptions reverse_safety_target.
