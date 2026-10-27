import Examples
open RegisteredNumber RegisteredNumber.Examples
example : plan env (.reference 1 (.value (.number 7))) = .ready (.number 7) false := by
  decide +kernel
