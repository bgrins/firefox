import Examples
open RegisteredNumber RegisteredNumber.Examples
example : (withCyclePolicy (fun _ => .invalidate) (.ready ratio true)).2 = (withCyclePolicy (fun _ => .retain) (.ready ratio true)).2 := by
  decide +kernel
