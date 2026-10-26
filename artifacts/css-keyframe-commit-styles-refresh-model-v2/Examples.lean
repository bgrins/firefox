import Bridge

namespace CommitRefresh

inductive Effect where
  | lower | top | higher
  deriving DecidableEq

def resolve (context : Rat) : Cache Effect Rat
  | .lower => fun base => base + context
  | .top => fun base => base + 10
  | .higher => fun _ => 999

def stack : List Effect := [.lower, .top]
def old : Cache Effect Rat := resolve 100

theorem top_only_insufficient :
    compose stack (refresh resolve 200 [.top] old) 0 ≠
      compose stack (resolve 200) 0 := by decide +kernel

example : compose stack (refresh resolve 200 [.top] old) 0 = 110 := by decide +kernel
example : compose stack (refresh resolve 200 stack old) 0 = 210 := by decide +kernel
example : compose stack (refresh resolve 200 [.top, .lower, .top] old) 0 = 210 := by decide +kernel
example : compose stack (refresh resolve 200 [.higher, .lower, .top] old) 0 = 210 := by decide +kernel
example : compose (stack ++ [.higher]) (refresh resolve 200 [.lower, .top, .higher] old) 0 =
    999 := by decide +kernel
example : compose stack (refresh resolve 100 stack old) 0 ≠
    compose stack (resolve 200) 0 := by decide +kernel

end CommitRefresh
