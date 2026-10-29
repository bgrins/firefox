import Context
open ShadowMove
example : (enter true outer (.shadow 7 none 1)).facts.localRoot = outer.facts.localRoot := by
  decide
