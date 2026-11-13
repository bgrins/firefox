Require Import Reals ZArith List Bool.
Require Import InputTarget PrefixTarget ReverseTarget EntryAllocation EntryModel.
Import ListNotations.
Module SignHistory.
Open Scope Z_scope.
Record Seed := {
  seedId : nat;
  seedFactor : Float32;
  seedBase : Z;
  seedMin : Z;
  seedMax : Z;
  seedFrozen : bool;
  seedShare : R
}.
Record Row := { seed : Seed; main : Z; isFrozen : bool; share : R }.
Record State := { rows : list Row; saved : Z }.
Definition clamp (s : Seed) (value : Z) := Z.max (seedMin s) (Z.min value (seedMax s)).
Definition hypothetical (s : Seed) := clamp s (seedBase s).
Definition sumZ (xs : list Z) := fold_right Z.add 0 xs.
Definition fixed (line : EntryAcquisition.Line) :=
  EntryAcquisition.mbpTotal line + EntryAcquisition.gap line.
Definition mode (line : EntryAcquisition.Line) (seeds : list Seed) :=
  Z.ltb (fixed line + sumZ (map hypothetical seeds)) (EntryAcquisition.inner line).
Definition build (s : Seed) : Row :=
  {| seed := s; main := hypothetical s; isFrozen := seedFrozen s; share := seedShare s |}.
Definition early (grow : bool) (row : Row) : Row :=
  if isFrozen row then row else
  let s := seed row in
  let zero := if Req_EM_T (value32 (seedFactor s)) 0 then true else false in
  let wrong := if grow then Z.ltb (hypothetical s) (seedBase s)
               else Z.ltb (seedBase s) (hypothetical s) in
  {| seed := s; main := main row; isFrozen := zero || wrong; share := share row |}.
Definition initial (line : EntryAcquisition.Line) (seeds : list Seed) : State :=
  {| rows := map (early (mode line seeds)) (map build seeds); saved := 0 |}.
Definition asItem (grow : bool) (row : Row) : Item :=
  {| itemId := seedId (seed row);
     payload := {| factor := seedFactor (seed row); base := seedBase (seed row); growing := grow |};
     frozen := isFrozen row; stored := share row |}.
Definition itemRows (grow : bool) (state : State) := map (asItem grow) (rows state).
Definition currentSize (row : Row) := if isFrozen row then main row else seedBase (seed row).
Definition asRound (grow : bool) (state : State) : EntryAcquisition.Round :=
  {| EntryAcquisition.used := map currentSize (rows state);
     EntryAcquisition.items := itemRows grow state |}.
Definition free (line : EntryAcquisition.Line) (grow : bool) (state : State) :=
  EntryAcquisition.roundFree line (asRound grow state).
Definition balance (line : EntryAcquisition.Line) (state : State) :=
  fixed line + sumZ (map (fun row => if isFrozen row then main row else hypothetical (seed row)) (rows state)).
Definition Balanced (line : EntryAcquisition.Line) (grow : bool) (state : State) : Prop :=
  if grow then balance line state <= EntryAcquisition.inner line
  else EntryAcquisition.inner line <= balance line state.
Definition Direction (grow : bool) (value : Z) : Prop := if grow then 0 <= value else value <= 0.
Definition ActiveBase (grow : bool) (row : Row) : Prop := isFrozen row = false ->
  if grow then seedBase (seed row) <= hypothetical (seed row)
  else hypothetical (seed row) <= seedBase (seed row).
Definition SeedValid (s : Seed) : Prop :=
  0 <= seedMin s <= seedMax s /\ EntryAcquisition.Acquired32 (seedMax s) /\
  (seedFrozen s = false -> FactorInput (seedFactor s) /\ EntryAcquisition.Acquired32 (seedBase s)).
Definition InputValid (e : nat) (line : EntryAcquisition.Line) (seeds : list Seed) : Prop :=
  EntryAcquisition.LineAdmitted e line /\
  map seedId seeds = EntryAllocation.tokens (EntryAcquisition.allocation line) /\
  Forall SeedValid seeds.
Definition prepared (line : EntryAcquisition.Line) (grow : bool) (state : State) :=
  EntryAcquisition.prepare line (saved state) (asRound grow state).
Definition distributed (line : EntryAcquisition.Line) (grow : bool) (state : State) :=
  EntryAcquisition.execute line (saved state) (asRound grow state).
Definition deltaFor (i : nat) (result : ReverseResult) :=
  sumZ (map (fun event => if Nat.eqb (ordinal event) i then delta event else 0) (events result)).
Definition rawAt (result : ReverseResult) (i : nat) (row : Row) :=
  if isFrozen row then main row else seedBase (seed row) + deltaFor i result.
Definition boundedAt (result : ReverseResult) (i : nat) (row : Row) :=
  if isFrozen row then main row else clamp (seed row) (rawAt result i row).
Definition indexed (xs : list Row) := combine (seq 0 (length xs)) xs.
Definition violation (result : ReverseResult) (state : State) :=
  sumZ (map (fun pair => if isFrozen (snd pair) then 0
    else boundedAt result (fst pair) (snd pair) - rawAt result (fst pair) (snd pair)) (indexed (rows state))).
Definition selected (total raw bounded : Z) :=
  if Z.eqb total 0 then true else if Z.ltb 0 total then Z.ltb raw bounded else Z.ltb bounded raw.
Definition shareAfter (line : EntryAcquisition.Line) (grow : bool) (state : State)
    (i : nat) (row : Row) : R :=
  match EntryAcquisition.selectedBranch (prepared line grow state) with
  | EntryAcquisition.NoSpace => share row
  | _ => match nth_error (PrefixTarget.rows (PrefixTarget.run (itemRows grow state))) i with
         | Some produced => stored produced | None => share row end
  end.
Definition commit (line : EntryAcquisition.Line) (grow : bool) (state : State) (result : ReverseResult) (total : Z) (final : bool) (pair : nat * Row) : Row :=
  let row := snd pair in if isFrozen row then row else
  let raw := rawAt result (fst pair) row in
  let bounded := boundedAt result (fst pair) row in
  {| seed := seed row; main := bounded; isFrozen := selected total raw bounded || final;
     share := shareAfter line grow state (fst pair) row |}.
Record Pass := {
  next : State;
  totalViolation : Z;
  usedFallback : bool;
  reverseResult : ReverseResult
}.
Definition pass (line : EntryAcquisition.Line) (grow : bool) (limit iteration : nat) (state : State) : Pass :=
  let result := distributed line grow state in
  let total := violation result state in
  let final := Nat.eqb (S iteration) limit in
  {| next := {| rows := map (commit line grow state result total final) (indexed (rows state));
                saved := EntryAcquisition.originalAfter (prepared line grow state) |};
     totalViolation := total;
     usedFallback := final && existsb (fun pair => negb (isFrozen (snd pair)) &&
       negb (selected total (rawAt result (fst pair) (snd pair))
         (boundedAt result (fst pair) (snd pair)))) (indexed (rows state));
     reverseResult := result |}.
Definition ActiveCount (state : State) := length (filter (fun row => negb (isFrozen row)) (rows state)).
Definition CanStep (lineInfo : bool) (seeds : list Seed) (iteration : nat) (state : State) : Prop :=
  (iteration < length seeds)%nat /\
  ((0 < ActiveCount state)%nat \/ (iteration = O /\ lineInfo = true)).
Inductive History (line : EntryAcquisition.Line) (seeds : list Seed) (lineInfo : bool) : nat -> State -> Prop :=
  | history_initial : History line seeds lineInfo O (initial line seeds)
  | history_step : forall iteration state,
      History line seeds lineInfo iteration state -> CanStep lineInfo seeds iteration state ->
      History line seeds lineInfo (S iteration)
        (next (pass line (mode line seeds) (length seeds) iteration state)).
Definition normativeAmount (line : EntryAcquisition.Line) (grow : bool) (state : State) :=
  let current := free line grow state in
  if Z.eq_dec current 0 then current else
  let xs := itemRows grow state in
  if Req_EM_T (PrefixTarget.total (PrefixTarget.run xs)) 0 then current else
  let factors := EntryAcquisition.factorTotal (EntryAcquisition.factorRun xs) in
  if Rlt_dec factors 1 then
    let desired := ConversionTarget.integerDelta (EntryAcquisition.capture (saved state) current)
      (Target.Fraction factors) in
    if Z.ltb (Z.abs desired) (Z.abs current) then desired else current
  else current.
End SignHistory.
