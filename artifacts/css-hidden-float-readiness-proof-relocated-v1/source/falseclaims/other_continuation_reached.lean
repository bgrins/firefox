import FloatReady
open FloatReady
example : ((markOwner true false noPushed fixture).nextContinuation[0]?).any Subtree.eligible = true := by decide
