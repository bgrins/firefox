import Normalization

namespace ContainerAxes

abbrev PositiveZoom := { zoom : Nat // zoom ≠ 0 }

structure Dimension (Length : Type) where
  source : Nat
  zoom : PositiveZoom
  raw : Length
  deriving DecidableEq

structure Axes (Length : Type) where
  width : Option (Dimension Length)
  height : Option (Dimension Length)
  deriving DecidableEq

def first {A : Type} (near far : Option A) : Option A :=
  match near with
  | some value => some value
  | none => far

def merge {L : Type} (near far : Axes L) : Axes L :=
  ⟨first near.width far.width, first near.height far.height⟩

theorem selected_dimension_keeps_source_and_zoom {L : Type}
    (value : Dimension L) (far : Option (Dimension L)) :
    first (some value) far = some value := rfl

def normalize {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (dimension : Dimension L) : Nat × L :=
  (dimension.source, scaling.remove dimension.zoom dimension.raw)

theorem normalize_first {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (near far : Option (Dimension L)) :
    (first near far).map (normalize scaling) =
      first (near.map (normalize scaling)) (far.map (normalize scaling)) := by
  cases near <;> rfl

theorem normalize_merge {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (near far : Axes L) :
    ((merge near far).width.map (normalize scaling),
     (merge near far).height.map (normalize scaling)) =
    (first (near.width.map (normalize scaling)) (far.width.map (normalize scaling)),
     first (near.height.map (normalize scaling)) (far.height.map (normalize scaling))) := by
  simp only [merge, normalize_first]

def fromCanonical {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (source : Nat) (zoom : PositiveZoom) (value : L) : Dimension L :=
  ⟨source, zoom, scaling.apply zoom value⟩

theorem recover_source_value {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (source : Nat) (zoom : PositiveZoom) (value : L) :
    normalize scaling (fromCanonical scaling source zoom value) = (source, value) := by
  simp only [normalize, fromCanonical, scaling.cancel]

def resolve {L : Type} (scaling : RegisteredZoom.Scaling PositiveZoom L)
    (canonicalViewport : L) (dimension : Option (Dimension L)) : L :=
  match dimension with
  | none => canonicalViewport
  | some value => (normalize scaling value).2

theorem viewport_is_already_canonical {L : Type}
    (scaling : RegisteredZoom.Scaling PositiveZoom L) (viewport : L) :
    resolve scaling viewport none = viewport := rfl

def bounds (scaling : RegisteredZoom.Scaling PositiveZoom Nat) (viewportWidth viewportHeight : Nat)
    (axes : Axes Nat) : Nat × Nat :=
  let width := resolve scaling viewportWidth axes.width
  let height := resolve scaling viewportHeight axes.height
  (min width height, max width height)

theorem normalized_bounds {S : RegisteredZoom.Scaling PositiveZoom Nat}
    (widthSource heightSource : Nat) (widthZoom heightZoom : PositiveZoom)
    (width height viewportWidth viewportHeight : Nat) :
    bounds S viewportWidth viewportHeight
      ⟨some (fromCanonical S widthSource widthZoom width),
       some (fromCanonical S heightSource heightZoom height)⟩ =
      (min width height, max width height) := by
  simp only [bounds, resolve, recover_source_value]

def exactNaturalScaling : RegisteredZoom.Scaling PositiveZoom Nat where
  apply zoom value := zoom.val * value
  remove zoom raw := raw / zoom.val
  cancel zoom value := Nat.mul_div_cancel_left value (Nat.pos_of_ne_zero zoom.property)

def guardedZoom (zoom : Nat) : PositiveZoom :=
  if nonzero : zoom ≠ 0 then ⟨zoom, nonzero⟩ else ⟨1, by decide⟩

theorem zero_guard_is_identity_scale : (guardedZoom 0).val = 1 := by decide +kernel

def outerWidth : Dimension Nat := ⟨1, ⟨2, by decide⟩, 640⟩
def innerHeight : Dimension Nat := ⟨2, ⟨1, by decide⟩, 120⟩
def mergedExample : Axes Nat := merge ⟨none, some innerHeight⟩ ⟨some outerWidth, none⟩

example : mergedExample.width = some outerWidth ∧ mergedExample.height = some innerHeight := by decide +kernel
example : bounds exactNaturalScaling 1366 683 mergedExample = (120, 320) := by decide +kernel
example : (640 / 2, 120 / 2) = (320, 60) := by decide +kernel

end ContainerAxes
