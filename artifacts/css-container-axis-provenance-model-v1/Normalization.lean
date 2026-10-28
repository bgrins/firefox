namespace RegisteredZoom

structure Scaling (Scale Length : Type) where
  apply : Scale → Length → Length
  remove : Scale → Length → Length
  cancel : ∀ scale value, remove scale (apply scale value) = value

structure Evaluation (Scale Input Length : Type) (scaling : Scaling Scale Length) where
  canonical : Input → Length
  raw : Scale → Input → Length
  factors : ∀ scale input, raw scale input = scaling.apply scale (canonical input)

inductive Source (Input Length : Type) where
  | localValue (input : Input)
  | initial (canonicalValue : Length)
  | inherited (canonicalValue : Length)

def canonical {S I L : Type} {scaling : Scaling S L}
    (evaluation : Evaluation S I L scaling) : Source I L → L
  | .localValue input => evaluation.canonical input
  | .initial value | .inherited value => value

def store {S I L : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I L scaling) (computationScale : S) : Source I L → L
  | .localValue input => scaling.remove computationScale (evaluation.raw computationScale input)
  | .initial value | .inherited value => value

theorem stored_canonical {S I L : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I L scaling) (scale : S) (source : Source I L) :
    store scaling evaluation scale source = canonical evaluation source := by
  cases source with
  | localValue input => simp only [store, canonical, evaluation.factors, scaling.cancel]
  | initial value => rfl
  | inherited value => rfl

def cssom {L : Type} (stored : L) : L := stored
def tokens {L : Type} (stored : L) : L := stored

theorem exports_agree {S I L : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I L scaling) (scale : S) (source : Source I L) :
    cssom (store scaling evaluation scale source) = canonical evaluation source ∧
    tokens (store scaling evaluation scale source) = canonical evaluation source := by
  exact ⟨stored_canonical scaling evaluation scale source,
    stored_canonical scaling evaluation scale source⟩

def consume {S L : Type} (scaling : Scaling S L) (consumerScale : S) (stored : L) : L :=
  scaling.apply consumerScale (tokens stored)

theorem consumer_scales_once {S I L : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I L scaling) (computationScale consumerScale : S)
    (source : Source I L) :
    consume scaling consumerScale (store scaling evaluation computationScale source) =
      scaling.apply consumerScale (canonical evaluation source) := by
  simp only [consume, tokens, stored_canonical]

theorem computation_scale_independent {S I L : Type} (scaling : Scaling S L)
    (evaluation : Evaluation S I L scaling) (first second : S) (source : Source I L) :
    store scaling evaluation first source = store scaling evaluation second source := by
  rw [stored_canonical, stored_canonical]

end RegisteredZoom
