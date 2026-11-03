import Trees
open CoalescedTree
example : coherent 2 double (.cons 1 { oldLeaf with refresh := true } .nil (.cons 2 oldLeaf .nil .nil)) := by decide +kernel
