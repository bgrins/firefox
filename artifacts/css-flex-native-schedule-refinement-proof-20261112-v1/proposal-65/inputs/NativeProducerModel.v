Require Import NativeFloatModel NativeState.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativeProducer.
Import NativeSchedule.
Open Scope Z_scope.
Record FloatEvent := {
  floatOrdinal : nat; eventWeight : NativeFloat.F64;
  weightBefore : NativeFloat.F64; weightAfter : NativeFloat.F64;
  factorBefore : NativeFloat.F64; factorAfter : NativeFloat.F64;
  oldShare : NativeFloat.F64; newShare : NativeFloat.F64; wroteShare : bool
}.
Record Produced := {
  producedRows : list Row; remaining : nat; visited : nat;
  weightSum : NativeFloat.F64; factorSum : NativeFloat.F64;
  largest : NativeFloat.F64; ties : nat; floatEvents : list FloatEvent
}.
Fixpoint loop (grow : bool) (left index : nat)
    (sum factors largestWeight : NativeFloat.F64) (largestCount : nat)
    (rs : list Row) : Produced :=
  match left,rs with
  | O,_ => {| producedRows := rs; remaining := O; visited := O;
      weightSum := sum; factorSum := factors; largest := largestWeight;
      ties := largestCount; floatEvents := [] |}
  | S k,[] => {| producedRows := []; remaining := S k; visited := O;
      weightSum := sum; factorSum := factors; largest := largestWeight;
      ties := largestCount; floatEvents := [] |}
  | S k,r::tail =>
      if frozen r then
        let result := loop grow (S k) (S index) sum factors largestWeight largestCount tail in
        {| producedRows := r::producedRows result; remaining := remaining result;
           visited := S (visited result); weightSum := weightSum result;
           factorSum := factorSum result; largest := largest result;
           ties := ties result; floatEvents := floatEvents result |}
      else
        let w := weight grow r in
        let nextWeight := NativeFloat.add sum w in
        let nextFactors := NativeFloat.add factors (NativeFloat.promote (factor grow (seed r))) in
        let write := NativeFloat.finite nextWeight in
        let nextShare := if write then
          if NativeFloat.equal w NativeFloat.zero then NativeFloat.zero
          else NativeFloat.divide w nextWeight else share r in
        let bigger := NativeFloat.less largestWeight w in
        let nextLargest := if bigger then w else largestWeight in
        let nextCount := if bigger then 1%nat else
          if NativeFloat.equal w largestWeight then S largestCount else largestCount in
        let result := loop grow k (S index) nextWeight nextFactors nextLargest nextCount tail in
        {| producedRows := replaceShare r nextShare :: producedRows result;
           remaining := remaining result; visited := S (visited result);
           weightSum := weightSum result; factorSum := factorSum result;
           largest := largest result; ties := ties result;
           floatEvents := {| floatOrdinal := index; eventWeight := w;
             weightBefore := sum; weightAfter := nextWeight;
             factorBefore := factors; factorAfter := nextFactors;
             oldShare := share r; newShare := nextShare; wroteShare := write |} :: floatEvents result |}
  end.
Definition run (grow : bool) (rs : list Row) (count : nat) :=
  loop grow (length rs-count)%nat O NativeFloat.zero NativeFloat.zero NativeFloat.zero O rs.
End NativeProducer.
