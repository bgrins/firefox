import StickyJoined

namespace StickyAdmission
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle StickyUpdate StickyJoined

instance representableDecidable (x : Int) : Decidable (Representable x) := by
  unfold Representable
  infer_instance

instance pointSafeDecidable (p : Point) : Decidable (PointSafe p) := by
  unfold PointSafe Representable
  infer_instance

instance rectSafeDecidable (r : Rect) : Decidable (RectSafe r) := by
  unfold RectSafe Representable
  infer_instance

instance computeSafeDecidable (w : World) (i : Nat) (space : Space) :
    Decidable (ComputeSafe w i space) := by unfold ComputeSafe; infer_instance

instance loopSafeDecidable (w : World) (ids : List Nat) (d : Point) :
    Decidable (LoopSafe w ids d) := by unfold LoopSafe; infer_instance

instance continuationSafeDecidable (w : World) (i : Nat) (ids : List Nat) :
    Decidable (ContinuationSafe w i ids) := by unfold ContinuationSafe; infer_instance

instance translationSafeDecidable (w : World) (i : Nat) :
    Decidable (TranslationSafe w i) := by unfold TranslationSafe; infer_instance

instance frameSafeDecidable (w : World) (i : Nat) :
    Decidable (FrameSafe w i) := by unfold FrameSafe; infer_instance

instance chainDecidable (a : Array Node) (start : Option Nat) (ids : List Nat) :
    Decidable (Chain a start ids) :=
  match start, ids with
  | none, [] => isTrue trivial
  | some _, [] => isFalse id
  | none, _ :: _ => isFalse id
  | some j, i :: rest => by
    unfold Chain
    let _ := chainDecidable a a[j]!.next rest
    infer_instance

instance overflowDecidable (a : Array Node) (start : Option Nat) (ids : List Nat) :
    Decidable (OverflowPath a start ids) :=
  match start, ids with
  | none, [] => isTrue trivial
  | some _, [] => isFalse id
  | none, _ :: _ => isFalse id
  | some j, i :: rest => by
    unfold OverflowPath
    let _ := overflowDecidable a (if j = a.size then none else a[j]!.next) rest
    infer_instance

instance primaryReadyDecidable (nodes : Array Node) (reflow : Bool) (i : Nat)
    (ids over : List Nat) : Decidable (PrimaryReady nodes reflow i ids over) := by
  unfold PrimaryReady
  infer_instance

instance readyListDecidable (nodes : Array Node) (reflow : Bool) (chains overs : Nat → List Nat)
    (primaries : List Nat) : Decidable (ReadyList nodes reflow chains overs primaries) := by
  unfold ReadyList
  infer_instance

instance batchDecidable (reflow : Bool) (chains : Nat → List Nat)
    (nodes : Array Node) (ids : List Nat) : Decidable (BatchSafe reflow chains nodes ids) :=
  match ids with
  | [] => isTrue trivial
  | i :: rest => by
    unfold BatchSafe
    let _ := batchDecidable reflow chains (primaryReference nodes reflow i (chains i)) rest
    infer_instance

instance actionDecidable (w : World) (input : Input) (chains overs : Nat → List Nat) :
    Decidable (ActionSafe w input chains overs) := by
  unfold ActionSafe
  split <;> infer_instance

def chainIndices (nodes : Array Node) : Nat → Option Nat → List Nat
  | 0, _ => []
  | _, none => []
  | fuel + 1, some i => i :: chainIndices nodes fuel nodes[i]!.next

def overflowIndices (nodes : Array Node) : Nat → Option Nat → List Nat
  | 0, _ => []
  | _, none => []
  | fuel + 1, some i => i ::
      overflowIndices nodes fuel (if i = nodes.size then none else nodes[i]!.next)

def chains (nodes : Array Node) (i : Nat) : List Nat :=
  chainIndices nodes (nodes.size + 1) (some i)

def overs (nodes : Array Node) (i : Nat) : List Nat :=
  overflowIndices nodes (nodes.size + 1) nodes[i]!.parent

def admitted (input : Input) : Bool :=
  decide (ActionSafe ⟨input.nodes, #[], false⟩ input (chains input.nodes) (overs input.nodes))

theorem admitted_full_machine (input : Input) (h : admitted input = true) :
    machineRun true input = run orderedPosition true input := by
  apply full_run_machine_refinement true input (chains input.nodes) (overs input.nodes)
  exact of_decide_eq_true h

def independentObservation (input : Input) : Option Point × Array Node :=
  let w : World := ⟨input.nodes, #[], false⟩
  match input.action with
  | 0 => (some (computedReference w input.target .current), input.nodes)
  | 1 => (some (computedReference w input.target .ignoreScroll), input.nodes)
  | 2 => (some (canonicalReference w input.target), input.nodes)
  | 3 => (none, continuationReference w input.target (chains input.nodes input.target))
  | 4 => (none, updateReference input.reflow (chains input.nodes) input.nodes input.primaries)
  | 5 => (some (frameReference w input.target), input.nodes)
  | _ => (some ⟨if (computedReference w input.target .current).y !=
      (observedNormal input.nodes[input.target]!).y then 1 else 0, 0⟩, input.nodes)

end StickyAdmission
