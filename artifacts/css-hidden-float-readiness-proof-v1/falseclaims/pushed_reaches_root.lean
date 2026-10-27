import FloatReady
open FloatReady
example : floatEligible 0 [] (markOwner true false (fun _ => true) fixture) = true := by decide
