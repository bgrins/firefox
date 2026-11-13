Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativeClamp.
Import NativeSchedule.
Open Scope Z_scope.
Record Event := { ordinal : nat; beforeRow : Row; afterRow : Row;
  difference : Z; totalBefore : Z; totalAfter : Z }.
Record Result := { clampedRows : list Row; total : Z; remaining : nat;
  visited : nat; events : list Event }.
Definition one (r : Row) : Row*Z :=
  if Z.ltb (main r) (minimum (seed r)) then
    (setFlags (replaceMain r (minimum (seed r))) true (maxFlag r), minimum (seed r)-main r)
  else if Z.ltb (maximum (seed r)) (main r) then
    (setFlags (replaceMain r (maximum (seed r))) (minFlag r) true, maximum (seed r)-main r)
  else (r,0).
Fixpoint loop (left index : nat) (acc : Z) (rs : list Row) : Result :=
  match left,rs with
  | O,_ => {| clampedRows := rs; total := acc; remaining := O; visited := O; events := [] |}
  | S k,[] => {| clampedRows := []; total := acc; remaining := S k; visited := O; events := [] |}
  | S k,r::tail =>
    if frozen r then let result := loop (S k) (S index) acc tail in
      {| clampedRows := r::clampedRows result; total := total result;
         remaining := remaining result; visited := S (visited result); events := events result |}
    else let pair := one r in let result := loop k (S index) (acc+snd pair) tail in
      {| clampedRows := fst pair::clampedRows result; total := total result;
         remaining := remaining result; visited := S (visited result);
         events := {| ordinal := index; beforeRow := r; afterRow := fst pair;
           difference := snd pair; totalBefore := acc; totalAfter := acc+snd pair |}::events result |}
  end.
Record Selection := { selectedRows : list Row; frozenAfter : nat;
  remainingActiveVisits : nat; selectionVisited : nat; fallbackOrdinals : list nat }.
Fixpoint select (final : bool) (violation : Z) (left index count : nat) (rs : list Row) : Selection :=
  match left,rs with
  | O,_ => {| selectedRows := rs; frozenAfter := count; remainingActiveVisits := O;
      selectionVisited := O; fallbackOrdinals := [] |}
  | S k,[] => {| selectedRows := []; frozenAfter := count; remainingActiveVisits := S k;
      selectionVisited := O; fallbackOrdinals := [] |}
  | S k,r::tail =>
    if frozen r then let result := select final violation (S k) (S index) count tail in
      {| selectedRows := r::selectedRows result; frozenAfter := frozenAfter result;
         remainingActiveVisits := remainingActiveVisits result;
         selectionVisited := S (selectionVisited result); fallbackOrdinals := fallbackOrdinals result |}
    else
      let selected := selectedFlags violation r in
      let next := if selected then setFlags (freeze r) (minFlag r) (negb (minFlag r) && maxFlag r)
                  else if final then freeze r else setFlags r false false in
      let result := select final violation k (S index) (if selected || final then S count else count) tail in
      {| selectedRows := next::selectedRows result; frozenAfter := frozenAfter result;
         remainingActiveVisits := remainingActiveVisits result;
         selectionVisited := S (selectionVisited result);
         fallbackOrdinals := if negb selected && final then index::fallbackOrdinals result
                             else fallbackOrdinals result |}
  end.
Definition FitsEvent (e : Event) :=
  Forall Fits64 [main (beforeRow e); main (afterRow e); difference e; totalBefore e; totalAfter e].
End NativeClamp.
