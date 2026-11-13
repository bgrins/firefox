import FlexViolationCaller.Target

open FlexViolationCaller

#eval (twoPassControl.map fun (first, second, final) =>
  (first.after.frozenCount, remaining first.after, second.helper.fallback,
    final.iteration, final.line.frozenCount, final.finished,
    final.line.items.map (fun (item : ItemState) => (item.fields.identity, item.current))))

#eval ((start earlySeeds false false).line.frozenCount,
  (start earlySeeds false false).line.items.map (·.frozen),
  (start earlySeeds true false).line.frozenCount,
  (start earlySeeds true false).line.items.map (·.frozen))

#eval ((start [strutSeed 0] true false).finished,
  (start [strutSeed 0] true true).finished,
  (runPass 0 (start [strutSeed 0] true true).line [123]).map fun pass =>
    (pass.after == (start [strutSeed 0] true true).line, pass.helper.fallback,
      (advance (start [strutSeed 0] true true) pass).finished))

#eval ((start [] false false).finished, (start [] false true).finished,
  runPass 0 (start twoSeeds true false).line [0] == none)

#eval (runPass 1 (start [normalSeed 0 0 0 1, normalSeed 1 0 0 1] true false).line [-1,0]).map
  fun pass => (pass.after.frozenCount, pass.helper.fallback)

#eval (runPass 0 { (start twoSeeds true false).line with frozenCount := 2 } [-1,5]).map
  fun pass => (remaining pass.after, pass.clamped.violation, pass.helper.newlyFrozen)

#eval (boundedDelta (2 ^ 40), boundedDelta (-(2 ^ 40)))
