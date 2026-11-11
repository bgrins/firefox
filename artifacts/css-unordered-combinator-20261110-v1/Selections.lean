import Std

namespace CssUnordered

def insertions (item : α) : List α → List (List α)
  | [] => [[item]]
  | head :: tail => (item :: head :: tail) :: (insertions item tail).map (head :: ·)

def orders : List α → List (List α)
  | [] => [[]]
  | head :: tail =>
    let smaller := orders tail
    smaller ++ smaller.flatMap (insertions head)

end CssUnordered
