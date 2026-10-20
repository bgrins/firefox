import Std
namespace WidenedInsets

def coordMax : Int := 1073741823
def InCoord (x : Int) : Prop := -coordMax ≤ x ∧ x ≤ coordMax
def In32 (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647
def In64 (x : Int) : Prop := -9223372036854775808 ≤ x ∧ x ≤ 9223372036854775807

instance (x : Int) : Decidable (In32 x) := by unfold In32; infer_instance

def view (port start ending : Int) : Int := port - start - ending

def nativeEnd (port box start ending : Int) : Int :=
  let extent := view port start ending
  if box > extent then ending - (box - extent) else ending

def referenceEnd (port box start ending : Int) : Int :=
  min ending (port - start - box)

theorem end_refines (port box start ending : Int) :
    nativeEnd port box start ending = referenceEnd port box start ending := by
  by_cases h : box > view port start ending
  all_goals simp only [nativeEnd,h,↓reduceIte]
  all_goals unfold referenceEnd
  all_goals unfold view at *
  all_goals omega

theorem view_fits_box (port box start ending : Int) :
    box ≤ port - start - nativeEnd port box start ending := by
  rw [end_refines]
  unfold referenceEnd
  omega

theorem end_never_increases (port box start ending : Int) :
    nativeEnd port box start ending ≤ ending := by
  rw [end_refines]
  unfold referenceEnd
  omega

theorem all_wide_intermediates (port box start ending : Int)
    (hp : In32 port) (hb : In32 box) (hs : In32 start) (he : In32 ending) :
    In64 (port-start) ∧ In64 (view port start ending) ∧
    In64 (box-view port start ending) ∧ In64 (ending-(box-view port start ending)) := by
  unfold In32 In64 view at *
  omega

theorem result_fits_storage (port box start ending : Int)
    (hp : 0 ≤ port ∧ port ≤ coordMax) (hb : 0 ≤ box ∧ box ≤ coordMax)
    (hs : InCoord start) (he : InCoord ending) :
    In32 (nativeEnd port box start ending) := by
  rw [end_refines]
  unfold referenceEnd In32 InCoord coordMax at *
  omega

theorem ordinary_unchanged (port box start ending : Int)
    (fits : box ≤ view port start ending) : nativeEnd port box start ending = ending := by
  simp [nativeEnd,show ¬box > view port start ending from by omega]

structure Edges where
  near : Int
  far : Int
  deriving DecidableEq, Repr

def setNear (r : Edges) (n : Int) : Edges := {r with near := n}
def setFar (r : Edges) (f : Int) : Edges := {r with far := f}

theorem independent_edges (r : Edges) (n f : Int) :
    setFar (setNear r n) f = ⟨n,f⟩ := rfl

theorem defined_extent_queries (n f : Int) (_difference : In32 (f-n))
    (_sum : In32 (n+(f-n))) : n+(f-n)=f := by omega

def position (normal : Int) (stick contain : Edges) : Int :=
  min (max normal (min stick.near contain.far)) (max stick.far contain.near)

theorem normal_inside_view (normal : Int) (stick contain : Edges)
    (hn : stick.near ≤ normal) (hf : normal ≤ stick.far) :
    position normal stick contain = normal := by
  unfold position
  omega

theorem wide_negative_normalization :
    nativeEnd 6000 600 (-1073741760) (-1073741760) = -1073741760 ∧
    ¬ In32 (view 6000 (-1073741760) (-1073741760)) := by
  decide +kernel

theorem endpoints_fit_but_extent_does_not :
    In32 (-1073741760) ∧ In32 1073747160 ∧
    ¬ In32 (1073747160 - (-1073741760)) := by
  decide +kernel

theorem regression_position :
    position 12000 ⟨-1073741760,1073747160⟩ ⟨0,59400⟩ = 12000 := by
  decide +kernel

end WidenedInsets
