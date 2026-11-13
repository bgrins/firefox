Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import InputTarget PrefixTarget PrefixProof ReverseTarget ReverseStructure.
Import ListNotations.
Open Scope R_scope.

Definition EmitsFrom (xs : list (nat * Item)) (e : Event) : Prop :=
  exists i x, In (i,x) xs /\ ordinal e = i /\ frozen x = false /\
    usedShare e = stored x /\ delta e = producedDelta (beforeFree e) x /\
    afterFree e = (beforeFree e - delta e)%Z.
Lemma emits_inclusion : forall xs ys e,
  incl xs ys -> EmitsFrom xs e -> EmitsFrom ys e.
Proof.
  intros xs ys e Hi [i [x [Hin Hrest]]]. exists i,x. split; [apply Hi; exact Hin|exact Hrest].
Qed.
Lemma loop_sources : forall xs left free,
  Forall (EmitsFrom xs) (events (reverseLoop left free xs)).
Proof.
  induction xs as [|[i x] xs IH]; intros left free; destruct left; cbn [reverseLoop events]; try constructor.
  destruct (frozen x) eqn:Hx; cbn [events].
  - eapply Forall_impl; [|exact (IH (S left) free)].
    intros e He. eapply emits_inclusion; [|exact He]. intros p Hp. right. exact Hp.
  - constructor.
    + exists i,x. cbn [ordinal usedShare delta beforeFree afterFree]. repeat split; try reflexivity; [left; reflexivity|exact Hx].
    + eapply Forall_impl; [|exact (IH left (free - producedDelta free x)%Z)].
      intros e He. eapply emits_inclusion; [|exact He]. intros p Hp. right. exact Hp.
Qed.
Lemma positioned_member : forall (xs : list Item) n i x,
  In (i,x) (combine (seq n (length xs)) xs) ->
  exists before after, xs = before ++ x :: after /\ i = (n + length before)%nat.
Proof.
  induction xs as [|a xs IH]; intros n i x Hin; cbn [length seq combine] in Hin; [contradiction|].
  destruct Hin as [Heq|Hin].
  - inversion Heq; subst. exists [],xs. split; [reflexivity|cbn; lia].
  - destruct (IH (S n) i x Hin) as [before [after [Heq Hindex]]].
    exists (a :: before),after. split; [cbn; rewrite Heq; reflexivity|cbn; lia].
Qed.
Lemma positioned_nth : forall xs i x,
  In (i,x) (positioned xs) -> nth_error xs i = Some x.
Proof.
  intros xs i x H. destruct (positioned_member xs 0 i x H) as [before [after [Heq Hi]]].
  cbn in Hi. subst xs i. rewrite nth_error_app2 by lia. rewrite Nat.sub_diag. reflexivity.
Qed.
Lemma original_output : forall xs i y,
  nth_error (rows (run xs)) i = Some y ->
  exists x, nth_error xs i = Some x /\ identity y = identity x.
Proof.
  intros xs i y Hy.
  pose proof (f_equal (fun ys => nth_error ys i) (proj1 (preservation_target xs))) as H.
  change (nth_error (map identity (rows (run xs))) i = nth_error (map identity xs) i) in H.
  rewrite !nth_error_map in H. rewrite Hy in H.
  destruct (nth_error xs i) as [x|] eqn:Hx; cbn in H; [|discriminate].
  exists x. split; [reflexivity|].
  exact (f_equal (fun o => match o with Some t => t | None => identity y end) H).
Qed.
Lemma emitted_binding : forall xs e,
  EmitsFrom (rev (positioned (rows (run xs)))) e -> EventBoundTo xs e.
Proof.
  intros xs e [i [y [Hin [Hi [Hfy [Hs [Hd Ha]]]]]]].
  apply (proj2 (in_rev (positioned (rows (run xs))) (i,y))) in Hin.
  pose proof (positioned_nth _ _ _ Hin) as Hy.
  destruct (original_output xs i y Hy) as [x [Hx Hid]].
  assert (Hfx : frozen x = false).
  { pose proof (f_equal (@snd (nat * WeightInput) bool) Hid) as Hflags.
    change (frozen y = frozen x) in Hflags. congruence. }
  destruct (nth_split xs i x Hx) as [before [after [Hxs Hlen]]].
  pose proof (prefix_target before x after Hfx) as Hp.
  rewrite <- Hxs, Hlen in Hp. rewrite Hy in Hp. inversion Hp; subst y.
  exists before,x,after,(setStored x (prefixShare before x)).
  repeat split; try assumption.
  - rewrite Hi. symmetry. exact Hlen.
  - rewrite Hi. exact Hy.
Qed.
Theorem event_binding_target : EventBindingTarget.
Proof.
  intros xs free. unfold reverseRun. destruct (Req_EM_T (total (run xs)) 0); [constructor|].
  eapply Forall_impl; [|apply loop_sources]. intros e He. apply emitted_binding. exact He.
Qed.
Lemma produced_ranges : forall xs,
  Admitted xs -> Forall (fun p => frozen (snd p) = false -> 0 <= stored (snd p) <= 1)
    (rev (positioned (rows (run xs)))).
Proof.
  intros xs Ha. apply Forall_forall. intros [i y] Hin Hfy.
  apply (proj2 (in_rev (positioned (rows (run xs))) (i,y))) in Hin.
  pose proof (positioned_nth _ _ _ Hin) as Hy.
  destruct (original_output xs i y Hy) as [x [Hx Hid]].
  assert (Hfx : frozen x = false).
  { pose proof (f_equal (@snd (nat * WeightInput) bool) Hid) as Hflags.
    change (frozen y = frozen x) in Hflags. cbn in Hfy. congruence. }
  exact (range_target xs i x y Ha Hx Hfx Hy).
Qed.

Print Assumptions event_binding_target.
Print Assumptions produced_ranges.
