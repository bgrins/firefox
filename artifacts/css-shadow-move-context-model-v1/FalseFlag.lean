import Context
open ShadowMove
example : (walk false outer [.light, .shadow 7 none 1]).isMove = true := by
  decide
