import Std

example : (2147483647 : Nat) * 2 = 4294967294 ∧
    4294967294 < 4294967296 ∧
    (4294967294 : Int) - 4294967296 = -2 ∧
    (3 : Int) - (-2) = 5 := by decide +kernel

example : (1431655766 : Nat) * 3 = 4294967298 ∧
    4294967298 % 4294967296 = 2 ∧
    (3 : Int) - 2 = 1 := by decide +kernel

example : (2147483647 : Nat) * 2 + 1 + 1 = 4294967296 ∧
    4294967296 % 4294967296 = 0 ∧
    (3 : Int) - 0 = 3 := by decide +kernel

example : (["a", "b"] ++ ["a", "b"]).take 3 = ["a", "b", "a"] ∧
    (["a", "b", "c"] ++ ["a", "b", "c"]).take 3 = ["a", "b", "c"] ∧
    (["a", "b"] ++ ["a", "b"] ++ ["x", "y"]).take 3 = ["a", "b", "a"] := by decide +kernel
