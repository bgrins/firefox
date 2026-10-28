import Init

set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

namespace WritingModeFlags

def contains (source flag : Nat) : Bool := source &&& flag == flag

def remove (remaining flag : Nat) : Nat := remaining &&& (511 ^^^ flag)

def iter (source : Nat) (definitions : List Nat) : List Nat :=
  ((definitions.foldl (fun state flag =>
    if contains source flag && state.1 &&& flag != 0 then
      (remove state.1 flag, state.2 ++ [flag])
    else state) (source, [])) : Nat × List Nat).2

def historical : List Nat := [1, 2, 4, 8, 16, 261, 10, 271, 32, 64, 128, 256]
def corrected : List Nat := [1, 2, 4, 8, 16, 256, 261, 10, 271, 32, 64, 128]
def singletons : List Nat := [1, 2, 4, 8, 16, 256, 32, 64, 128]
def expected (source : Nat) : List Nat := singletons.filter (contains source)

theorem historical_composite_witness : iter 261 historical = [1, 4, 261] := by
  decide +kernel

theorem corrected_witness : iter 261 corrected = [1, 4, 256] := by
  decide +kernel

theorem every_defined_mask_exact : ∀ source : Fin 512,
    iter source.val corrected = expected source.val := by
  decide +kernel

def isSingleton (flag : Nat) : Bool := flag != 0 && flag &&& (flag - 1) == 0

def coveredBeforeComposites (definitions : List Nat) : Bool :=
  ((definitions.foldl (fun state flag =>
    if isSingleton flag then (state.1 ||| flag, state.2)
    else (state.1, state.2 && contains state.1 flag)) (0, true)) : Nat × Bool).2

theorem corrected_order : coveredBeforeComposites corrected = true := by
  decide +kernel

theorem historical_order_fails : coveredBeforeComposites historical = false := by
  decide +kernel

end WritingModeFlags
