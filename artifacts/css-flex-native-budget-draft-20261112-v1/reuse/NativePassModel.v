Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel.
Require Import InputTarget ConversionTarget EntryModel EntryAllocation SignModel SignTarget PrefixTarget ReverseTarget BranchTarget.
Require Import Reals ZArith List Bool .
Import ListNotations.
Module NativePass.
Import NativeSchedule.
Open Scope Z_scope.
Record Config := { spaceAvailable : Z; growing : bool; itemLimit : nat }.
Record Reset := { resetRows : list Row; freeSpace : Z; resetEvents : list ArithmeticEvent }.
Fixpoint reset (index : nat) (free : Z) (rs : list Row) : Reset :=
  match rs with
  | [] => {| resetRows := []; freeSpace := free; resetEvents := [] |}
  | r::tail =>
    let next := if frozen r then r else replaceMain r (baseSize (seed r)) in
    let result := reset (S index) (free-main next) tail in
    {| resetRows := next::resetRows result; freeSpace := freeSpace result;
       resetEvents := {| eventPhase := Acquiring; eventOrdinal := index;
         leftOperand := free; rightOperand := main next; resultValue := free-main next |}::resetEvents result |}
  end.
Inductive Branch := NoSpace | NoWeight | FiniteDistribution | NonfiniteDistribution.
Record Prepared := { acquisition : Reset; preparedRows : list Row;
  producer : option NativeProducer.Produced; captured : option Z;
  entryFree : Z; usedAdjustment : bool; branch : Branch }.
Definition prepare (config : Config) (state : State) : option Prepared :=
  let acquired := reset O (spaceAvailable config) (rows state) in
  let free := freeSpace acquired in
  if Z.eqb free 0 then Some {| acquisition := acquired; preparedRows := resetRows acquired;
    producer := None; captured := original state; entryFree := free;
    usedAdjustment := false; branch := NoSpace |}
  else
    let captured := match original state with None => Some free | Some z => Some z end in
    let produced := NativeProducer.run (growing config) (resetRows acquired) (frozenCount state) in
    if NativeFloat.equal (NativeProducer.weightSum produced) NativeFloat.zero then
      Some {| acquisition := acquired; preparedRows := NativeProducer.producedRows produced;
        producer := Some produced; captured := captured; entryFree := free;
        usedAdjustment := false; branch := NoWeight |}
    else
      let adjusted := NativeFloat.less (NativeProducer.factorSum produced) NativeFloat.one in
      let desired := if adjusted then NativeFloat.scale (saved captured) (NativeProducer.factorSum produced)
                     else Some free in
      match desired with None => None | Some wanted =>
        Some {| acquisition := acquired; preparedRows := NativeProducer.producedRows produced;
          producer := Some produced; captured := captured;
          entryFree := if adjusted then if Z.ltb 0 free then Z.min free wanted else Z.max free wanted else free;
          usedAdjustment := adjusted;
          branch := if NativeFloat.finite (NativeProducer.weightSum produced)
                    then FiniteDistribution else NonfiniteDistribution |} end.
Definition distributes (p : Prepared) :=
  match branch p with FiniteDistribution | NonfiniteDistribution => true | _ => false end.
Record Pass := { prepared : Prepared; reverse : option NativeReverse.Result;
  clamped : NativeClamp.Result; selection : NativeClamp.Selection; next : State }.
Definition finish (config : Config) (state : State) (p : Prepared)
    (revResult : option NativeReverse.Result) : Pass :=
  let afterReverse := match revResult with None => preparedRows p | Some r => NativeReverse.restored r end in
  let total := match revResult with None => 0 | Some r => NativeReverse.violation r end in
  let reportRows := match revResult with None => reports state | Some r => NativeReverse.reportsAfter r end in
  let clamped := NativeClamp.loop (length afterReverse-frozenCount state)%nat O total afterReverse in
  let selected := NativeClamp.select (Nat.eqb (S (iteration state)) (itemLimit config))
    (NativeClamp.total clamped) (length afterReverse-frozenCount state)%nat O
    (frozenCount state) (NativeClamp.clampedRows clamped) in
  {| prepared := p; reverse := revResult; clamped := clamped; selection := selected;
     next := {| rows := NativeClamp.selectedRows selected;
       frozenCount := NativeClamp.frozenAfter selected; original := captured p;
       reports := reportRows; reportMode := reportMode state; iteration := S (iteration state) |} |}.
Definition step (config : Config) (state : State) : option Pass :=
  match prepare config state with
  | None => None
  | Some p => if distributes p then
      match producer p with
      | None => None
      | Some prod => match NativeReverse.run (growing config) prod (frozenCount state)
          (entryFree p) (reports state) with
        | None => None | Some r => Some (finish config state p (Some r)) end
      end
    else Some (finish config state p None)
  end.
Definition canStep (config : Config) (state : State) : bool :=
  Nat.ltb (iteration state) (itemLimit config) &&
  (Nat.ltb (frozenCount state) (length (rows state)) ||
    (Nat.eqb (iteration state) O && match reports state with None => false | Some _ => true end)).
Inductive History (config : Config) (initial : State) : State -> Prop :=
| history_initial : History config initial initial
| history_step : forall state result,
    History config initial state -> canStep config state = true -> step config state = Some result ->
    History config initial (next result).
Definition FitsPass (p : Pass) :=
  Forall NativeSchedule.FitsEvent (resetEvents (acquisition (prepared p))) /\
  Fits64 (entryFree (prepared p)) /\
  (match reverse p with None => True | Some result =>
    Forall NativeReverse.FitsEvent (NativeReverse.events result) /\
    Fits64 (NativeReverse.finalFree result) end) /\
  Forall NativeClamp.FitsEvent (NativeClamp.events (clamped p)).
Record RunResult := { finalState : State; passes : list Pass }.
Fixpoint run (fuel : nat) (config : Config) (state : State) : option RunResult :=
  if canStep config state then
    match fuel with
    | O => Some {| finalState := state; passes := [] |}
    | S n => match step config state with
      | None => None | Some p => match run n config (next p) with
        | None => None | Some result => Some {| finalState := finalState result; passes := p::passes result |}
        end end
    end
  else Some {| finalState := state; passes := [] |}.
End NativePass.
