import Trace
namespace Rlh

def mutantRead (m : Nat) (w : World) (foreignOwner : Owner) (foreignValue : Rat) : Observation :=
  let b := if m = 5 ∧ w.base = .inherited then
      (Source.current w.consumer, w.current.stored.value * w.inheritanceZoom)
    else if m = 10 ∧ w.base = .inherited then
      (Source.inherited w.parent, w.inherited.stored.value)
    else builderValue w
  let (source,value,used) := match w.role with
    | .root => if m = 4 then (.initial w.initial,w.initialStored.value,false)
      else (b.1,if m = 1 then b.2 * w.consumerZoom.value else b.2,false)
    | .media => (.initial w.initial,w.initialStored.value * w.consumerZoom.value,false)
    | .descendant => if m = 6 then (.cache foreignOwner,foreignValue * w.consumerZoom.value,true)
      else (.cache w.root,if m = 2 then w.cache.value else w.cache.value * w.consumerZoom.value,true)
  let c := if m = 8 then 1 else w.coefficient.value
  let scaled := if m = 9 then (value * c) * c else value * c
  {source,scaled,exposed := scaled / w.consumerZoom.value,coefficient := c,cacheUsed := used}

def mutantPublish (m count : Nat) (s : State) : State :=
  if m = 7 ∧ count > 0 then {s with published := true}
  else if m = 3 then
    {s with cache := some ⟨s.root.owner,s.root.provider.stored.value⟩,published := true}
  else publishNative s

theorem mutant_zero_read (w : World) (o : Owner) (v : Rat) :
    mutantRead 0 w o v = implementation w := by
  cases hr : w.role <;> simp [mutantRead,implementation,hr]
theorem mutant_one_original (w : World) (o : Owner) (v : Rat) :
    mutantRead 1 w o v = original w := by
  cases hr : w.role <;> simp [mutantRead,original,implementation,hr]
theorem mutant_zero_publish (n : Nat) (s : State) :
    mutantPublish 0 n s = publishNative s := by simp [mutantPublish]
theorem stale_mutant_keeps_schedule (n : Nat) (s : State) :
    (mutantPublish 7 n s).published = true := by
  by_cases h : n > 0 <;> simp [mutantPublish,publishNative,h]
theorem stale_mutant_keeps_cache (n : Nat) (s : State) (h : n > 0) :
    (mutantPublish 7 n s).cache = s.cache := by simp [mutantPublish,h]
end Rlh
