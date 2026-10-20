import Std

namespace RectangleNumeric

def grid (au : Int) : Int := (au * 32768 + 15) / 30

def appRound (scaled : Int) : Int := (scaled + 2147483648) / 4294967296

theorem app_round_exact_iff (scaled original : Int) :
    appRound scaled = original ↔
      4294967296 * original - 2147483648 ≤ scaled ∧
      scaled < 4294967296 * original + 2147483648 := by
  unfold appRound
  omega

theorem app_round_components_preserve_edge (sx sw x w : Int)
    (hx : 4294967296*x-2147483648 ≤ sx ∧ sx < 4294967296*x+2147483648)
    (hw : 4294967296*w-2147483648 ≤ sw ∧ sw < 4294967296*w+2147483648) :
    appRound sx + appRound sw = x + w := by
  rw [(app_round_exact_iff sx x).mpr hx, (app_round_exact_iff sw w).mpr hw]

theorem half_tie_is_not_even : appRound 2147483648 = 1 := by decide

theorem negative_half_tie_moves_up : appRound (-2147483648) = 0 := by decide

def quantum (ticks : Int) : Nat := 2 ^ (ticks.natAbs.log2 + 1 - 24)

def narrow (ticks : Int) : Int :=
  let q : Int := quantum ticks
  let k := ticks / q
  let r := ticks % q
  if 2 * r < q then k * q
  else if 2 * r > q then (k + 1) * q
  else if k % 2 = 0 then k * q else (k + 1) * q

def observe (round : Int → Int) (start finish : Int) : Int :=
  round start + round (finish - start)

def error (round : Int → Int) (n : Int) := round n - n

theorem edge_error_decomposition (round : Int → Int) (start finish : Int) :
    observe round start finish =
      finish + error round start + error round (finish - start) := by
  unfold observe error
  omega

theorem exact_edge_iff_cancel (round : Int → Int) (start finish : Int) :
    observe round start finish = finish ↔
      error round start + error round (finish - start) = 0 := by
  rw [edge_error_decomposition]
  omega

theorem fixed_components_preserve (round : Int → Int) (start finish : Int)
    (hx : round start = start) (hw : round (finish - start) = finish - start) :
    observe round start finish = finish := by
  unfold observe
  rw [hx, hw]
  omega

theorem exact_original_edge_iff (round : Int → Int) (start finish originalAu : Int) :
    60 * observe round start finish = 65536 * originalAu ↔
      60 * (error round start + error round (finish - start)) =
        65536 * originalAu - 60 * finish := by
  rw [edge_error_decomposition]
  omega

theorem repaired_integer_edge_is_not_alone_sufficient :
    observe (fun n => n + 1) (-20) 100 ≠ 100 := by decide

theorem grid_exact_multiple (k : Int) : grid (15 * k) = 16384 * k := by
  unfold grid
  omega

theorem fixed_grid_components_preserve (round : Int → Int) (x k : Int)
    (hx : round (grid x) = grid x)
    (hw : round (grid (15 * k) - grid x) = grid (15 * k) - grid x) :
    60 * observe round (grid x) (grid (15 * k)) = 65536 * (15 * k) := by
  rw [fixed_components_preserve round _ _ hx hw, grid_exact_multiple]
  omega

theorem quantized_small_fixed (n : Int) (h : quantum n = 1) : narrow n = n := by
  simp [narrow, h]

theorem representable_fixed (n : Int) (h : n % (quantum n : Int) = 0)
    (positive : 0 < (quantum n : Int)) : narrow n = n := by
  unfold narrow
  simp only [h, Int.mul_zero]
  rw [ite_eq_left positive]
  have hh := Int.emod_add_ediv_mul n (quantum n : Int)
  omega

theorem representable_components_exact (x k : Int)
    (hx : grid x % (quantum (grid x) : Int) = 0)
    (hw : (grid (15*k) - grid x) % (quantum (grid (15*k) - grid x) : Int) = 0)
    (px : 0 < (quantum (grid x) : Int))
    (pw : 0 < (quantum (grid (15*k) - grid x) : Int)) :
    60 * observe narrow (grid x) (grid (15*k)) = 65536 * (15*k) := by
  apply fixed_grid_components_preserve
  · exact representable_fixed _ hx px
  · exact representable_fixed _ hw pw

theorem local_domains_join_exact_edge (sx sw x w k : Int)
    (hx : 4294967296*x-2147483648 ≤ sx ∧ sx < 4294967296*x+2147483648)
    (hw : 4294967296*w-2147483648 ≤ sw ∧ sw < 4294967296*w+2147483648)
    (edge : x+w = 15*k)
    (rx : grid x % (quantum (grid x) : Int) = 0)
    (rw : (grid (15*k)-grid x) % (quantum (grid (15*k)-grid x) : Int) = 0)
    (px : 0 < (quantum (grid x) : Int))
    (pw : 0 < (quantum (grid (15*k)-grid x) : Int)) :
    60 * observe narrow (grid (appRound sx)) (grid (appRound sx+appRound sw)) =
      65536*(x+w) := by
  rw [(app_round_exact_iff sx x).mpr hx, (app_round_exact_iff sw w).mpr hw, edge]
  exact representable_components_exact x k rx rw px pw

theorem zero_width (round : Int → Int) (x : Int) (h : round 0 = 0) :
    observe round x x = round x := by simp [observe, h]

theorem input_edge : (-8382488 : Int) + 8388488 = 6000 := by decide

theorem retained_integer_edge : (-8382488 : Int) + 8388489 = 6001 := by decide

theorem direct_dom_control :
    observe narrow (grid (-8382488)) (grid 6000) = 6553600 := by decide

theorem roundtrip_dom_counterexample :
    observe narrow (grid (-8382488)) (grid 6001) = 6554624 := by decide

theorem observed_residual : (6554624 : Int) - 6553600 = 1024 := by decide

theorem small_control :
    observe narrow (grid (-1208)) (grid 6000) = 6553600 := by decide

theorem coordinate_grid_can_change_an_edge : grid 1 * 60 ≠ 65536 := by decide

theorem double_storage_does_not_undo_narrowing :
    narrow (grid 6001 - grid (-8382488)) ≠ grid 6001 - grid (-8382488) := by decide

theorem exact_appunits_still_lose_edge :
    observe narrow (grid (-7858324)) (grid 6000) = 6553088 := by decide

theorem cancellation_is_not_universal :
    error narrow (grid (-7858324)) +
      error narrow (grid 6000 - grid (-7858324)) = -512 := by decide

end RectangleNumeric

open RectangleNumeric
example : appRound 2147483648 = 0 := by decide
