import Trees
open CoalescedTree
example : markRoots leaves = (.cons 1 { oldLeaf with refresh := true } .nil (.cons 2 oldLeaf .nil .nil)) := by decide +kernel
