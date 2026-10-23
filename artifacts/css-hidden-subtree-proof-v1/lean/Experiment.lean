import Std
inductive Tree where
  | node (dirty table : Bool) (children : List Tree)
  deriving Repr

mutual
 def allDirty : Tree → Bool
   | .node d _ cs => d && allDirtyList cs
 def allDirtyList : List Tree → Bool
   | [] => true
   | t :: ts => allDirty t && allDirtyList ts
end

def markDesc : Tree → Tree
  | .node d t cs => if d || t then .node d t cs else .node true t (cs.map markDesc)

def markRoot : Tree → Tree
  | .node d t cs => if d then .node d t cs else .node true t (cs.map markDesc)

#check Tree.rec
