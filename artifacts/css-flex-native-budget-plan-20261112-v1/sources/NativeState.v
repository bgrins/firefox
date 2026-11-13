Require Import NativeFloatModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool SignModel.
Import ListNotations.
Module NativeSchedule.
Open Scope Z_scope.
Record Seed := {
  identity : nat; growFactor : Float32; shrinkFactor : Float32;
  baseSize : Z; minimum : Z; maximum : Z; initiallyFrozen : bool;
  initialShare : NativeFloat.F64; initialMinFlag : bool; initialMaxFlag : bool;
  isStrut : bool; measuredMBP : Z; measuredOuter : Z
}.
Definition factor (grow : bool) (s : Seed) := if grow then growFactor s else shrinkFactor s.
Definition clamp (s : Seed) (v : Z) := Z.max (minimum s) (Z.min v (maximum s)).
Definition project32 (v : Z) := Z.max (-2147483648) (Z.min v 2147483647).
Record Row := { seed : Seed; main : Z; frozen : bool;
  share : NativeFloat.F64; minFlag : bool; maxFlag : bool }.
Definition construct (s : Seed) : Row :=
  {| seed := s; main := clamp s (baseSize s); frozen := initiallyFrozen s;
     share := initialShare s;
     minFlag := if initiallyFrozen s then initialMinFlag s else false;
     maxFlag := if initiallyFrozen s then initialMaxFlag s else false |}.
Definition replaceMain (r : Row) (v : Z) : Row :=
  {| seed := seed r; main := v; frozen := frozen r; share := share r;
     minFlag := minFlag r; maxFlag := maxFlag r |}.
Definition replaceShare (r : Row) (v : NativeFloat.F64) : Row :=
  {| seed := seed r; main := main r; frozen := frozen r; share := v;
     minFlag := minFlag r; maxFlag := maxFlag r |}.
Definition setFlags (r : Row) (lo hi : bool) : Row :=
  {| seed := seed r; main := main r; frozen := frozen r; share := share r;
     minFlag := lo; maxFlag := hi |}.
Definition freeze (r : Row) : Row :=
  {| seed := seed r; main := main r; frozen := true; share := share r;
     minFlag := false; maxFlag := false |}.
Definition selectedFlags (total : Z) (r : Row) :=
  if Z.eqb total 0 then true else if Z.ltb 0 total then minFlag r else maxFlag r.
Record Report := { reportIdentity : nat; reportBase : Z; reportDelta : Z }.
Definition reportsFor (rs : list Row) := map (fun r =>
  {| reportIdentity := identity (seed r); reportBase := baseSize (seed r); reportDelta := 0 |}) rs.
Record State := { rows : list Row; frozenCount : nat; original : option Z;
  reports : option (list Report); reportMode : option bool; iteration : nat }.
Definition saved (o : option Z) := match o with None => 0 | Some z => z end.
Definition projectedSeed (grow : bool) (s : Seed) : SignHistory.Seed :=
  {| SignHistory.seedId := identity s; SignHistory.seedFactor := factor grow s;
     SignHistory.seedBase := baseSize s; SignHistory.seedMin := minimum s;
     SignHistory.seedMax := maximum s; SignHistory.seedFrozen := initiallyFrozen s;
     SignHistory.seedShare := NativeFloat.value (initialShare s) |}.
Definition projectedRow (grow : bool) (r : Row) : SignHistory.Row :=
  {| SignHistory.seed := projectedSeed grow (seed r); SignHistory.main := main r;
     SignHistory.isFrozen := frozen r; SignHistory.share := NativeFloat.value (share r) |}.
Definition projectedState (grow : bool) (s : State) : SignHistory.State :=
  {| SignHistory.rows := map (projectedRow grow) (rows s); SignHistory.saved := saved (original s) |}.
Definition weight (grow : bool) (r : Row) : NativeFloat.F64 :=
  if grow then NativeFloat.promote (factor grow (seed r)) else
  if Z.eqb (baseSize (seed r)) 0 then NativeFloat.zero else
  NativeFloat.multiply (NativeFloat.promote (factor grow (seed r))) (NativeFloat.integer (baseSize (seed r))).
Definition active (rs : list Row) := length (filter (fun r => negb (frozen r)) rs).
Definition earlyOne (grow : bool) (r : Row) :=
  if frozen r then r else
  let wrong := if grow then Z.ltb (main r) (baseSize (seed r))
                         else Z.ltb (baseSize (seed r)) (main r) in
  if NativeFloat.equal (NativeFloat.promote (factor grow (seed r))) NativeFloat.zero || wrong
  then setFlags (freeze r) (Z.ltb (baseSize (seed r)) (main r)) (Z.ltb (main r) (baseSize (seed r)))
  else r.
Fixpoint earlyLoop (grow : bool) (left count : nat) (rs : list Row) : list Row * nat :=
  match left,rs with
  | O,_ => (rs,count)
  | _,[] => ([],count)
  | S k,r::tail =>
      if frozen r then let out := earlyLoop grow (S k) count tail in (r::fst out,snd out)
      else let updated := earlyOne grow r in
        let out := earlyLoop grow k (if frozen updated then S count else count) tail in
        (updated::fst out,snd out)
  end.
Definition initialize (grow info : bool) (rs : list Row) (count : nat) : State :=
  let out := earlyLoop grow (length rs-count)%nat count rs in
  {| rows := fst out; frozenCount := snd out; original := None;
     reports := if info then Some (reportsFor rs) else None; reportMode := if info then Some grow else None; iteration := O |}.
Inductive Phase := Acquiring | Correcting | Clamping.
Record ArithmeticEvent := { eventPhase : Phase; eventOrdinal : nat;
  leftOperand : Z; rightOperand : Z; resultValue : Z }.
Definition FitsEvent (e : ArithmeticEvent) := Fits64 (leftOperand e) /\ Fits64 (rightOperand e) /\ Fits64 (resultValue e).
Definition updateReport (i : nat) (d : Z) (rs : option (list Report)) :=
  match rs with None => None | Some xs => Some (map (fun pair =>
    if Nat.eqb (fst pair) i then
      {| reportIdentity := reportIdentity (snd pair); reportBase := reportBase (snd pair); reportDelta := d |}
    else snd pair) (combine (seq 0 (length xs)) xs)) end.
End NativeSchedule.
