import FloatReady
open FloatReady
example : floatEligible 0 [0] (markOwner true false noPushed {fixture with otherLists := [.node 2 true false false [clean 3]]}) = true := by decide
