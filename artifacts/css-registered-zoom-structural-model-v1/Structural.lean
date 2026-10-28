import Normalization

namespace RegisteredZoom.Structural

inductive Value (Length Percentage Color Atom : Type) where
  | length (value : Length)
  | percentage (value : Percentage)
  | color (value : Color)
  | opaque (value : Atom)
  | lengthPercentage (length : Length) (percentage : Percentage)
  | math (operator : Atom) (left right : Value Length Percentage Color Atom)
  | listNil
  | listCons (head tail : Value Length Percentage Color Atom)
  | transform (operation : Atom) (arguments : Value Length Percentage Color Atom)
  | image (kind : Atom) (arguments : Value Length Percentage Color Atom)
  deriving DecidableEq, Repr

def mapLengths {L M P C A : Type} (f : L → M) : Value L P C A → Value M P C A
  | .length value => .length (f value)
  | .percentage value => .percentage value
  | .color value => .color value
  | .opaque value => .opaque value
  | .lengthPercentage length percentage => .lengthPercentage (f length) percentage
  | .math operator left right => .math operator (mapLengths f left) (mapLengths f right)
  | .listNil => .listNil
  | .listCons head tail => .listCons (mapLengths f head) (mapLengths f tail)
  | .transform operation arguments => .transform operation (mapLengths f arguments)
  | .image kind arguments => .image kind (mapLengths f arguments)

theorem map_identity {L P C A : Type} (value : Value L P C A) :
    mapLengths id value = value := by
  induction value <;> simp_all [mapLengths]

theorem map_composition {L M N P C A : Type} (f : L → M) (g : M → N)
    (value : Value L P C A) :
    mapLengths g (mapLengths f value) = mapLengths (fun x => g (f x)) value := by
  induction value <;> simp_all [mapLengths]

theorem map_left_inverse {L M P C A : Type} (f : L → M) (g : M → L)
    (inverse : ∀ x, g (f x) = x) (value : Value L P C A) :
    mapLengths g (mapLengths f value) = value := by
  induction value <;> simp_all [mapLengths]

def nonLengths {L P C A : Type} (value : Value L P C A) : Value Unit P C A :=
  mapLengths (fun _ => ()) value

theorem nonlength_data_preserved {L M P C A : Type} (f : L → M)
    (value : Value L P C A) :
    nonLengths (mapLengths f value) = nonLengths value := by
  simp only [nonLengths, map_composition]

def liftScaling {S L P C A : Type} (scaling : Scaling S L) :
    Scaling S (Value L P C A) where
  apply scale := mapLengths (scaling.apply scale)
  remove scale := mapLengths (scaling.remove scale)
  cancel scale value := map_left_inverse _ _ (scaling.cancel scale) value

theorem structured_scale_unscale {S L P C A : Type} (scaling : Scaling S L)
    (scale : S) (value : Value L P C A) :
    (liftScaling scaling).remove scale ((liftScaling scaling).apply scale value) = value :=
  (liftScaling scaling).cancel scale value

theorem structured_storage_canonical {S I L P C A : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I (Value L P C A) (liftScaling scaling))
    (scale : S) (source : Source I (Value L P C A)) :
    store (liftScaling scaling) evaluation scale source = canonical evaluation source :=
  stored_canonical (liftScaling scaling) evaluation scale source

end RegisteredZoom.Structural
