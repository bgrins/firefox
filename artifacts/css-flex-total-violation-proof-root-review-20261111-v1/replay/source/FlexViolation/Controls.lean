import FlexViolation.Cases

namespace FlexViolation

def sumOnly : Int → List Item → Option Int
  | acc, [] => some acc
  | acc, item :: rest =>
    let next := acc + adjustment item
    if min32 ≤ next ∧ next ≤ max32 then sumOnly next rest else none

def differenceOnly : Int → List Item → Option Int
  | acc, [] => some acc
  | acc, item :: rest =>
    if min32 ≤ adjustment item ∧ adjustment item ≤ max32 then
      differenceOnly (acc + adjustment item) rest else none

def wrappedFrozen (items : List Item) : List Item :=
  items.filter (selected (kind (wrap32 (total items))))

def reversedFrozen (items : List Item) : List Item := (frozen items).reverse

theorem sum_only_wrong : sumOnly 0 subtractionWitness = some max32 := by decide

theorem difference_only_wrong : differenceOnly 0 positiveWitness = some 2400000000 := by decide

theorem wrapped_wrong : wrappedFrozen positiveWitness = [] := by decide

theorem reversed_wrong : (reversedFrozen positiveWitness).map Item.identity = [4,3,2,1] := by decide

theorem refute_sum_only : ¬ ∀ items, Acquired items → sumOnly 0 items = oldFold items := by
  intro h
  have hx := h subtractionWitness subtraction_acquired
  rw [sum_only_wrong, subtraction_old_refuses] at hx
  contradiction

theorem positive_old_refuses : oldFold positiveWitness = none := by decide

theorem refute_difference_only : ¬ ∀ items, Acquired items → differenceOnly 0 items = oldFold items := by
  intro h
  have hx := h positiveWitness positive_acquired
  rw [difference_only_wrong, positive_old_refuses] at hx
  contradiction

theorem refute_wrapped_progress :
    ¬ ∀ items, Acquired items → items ≠ [] → wrappedFrozen items ≠ [] := by
  intro h
  have hx := h positiveWitness positive_acquired (by decide)
  exact hx wrapped_wrong

theorem refute_reversed_selection :
    ¬ ∀ items, Acquired items → reversedFrozen items = frozen items := by
  intro h
  have hx := congrArg (List.map Item.identity) (h positiveWitness positive_acquired)
  rw [reversed_wrong, positive_selected] at hx
  contradiction

def finalFallbackItems : List Item :=
  [{identity := 0, before := 0, minimum := 1, maximum := 1},
   {identity := 1, before := 0, minimum := 0, maximum := 1}]

theorem final_fallback_boundary : Acquired finalFallbackItems ∧
    (frozen finalFallbackItems).map Item.identity = [0] ∧
    finalFallbackItems.map Item.identity = [0,1] := by
  constructor
  · simp [finalFallbackItems, Acquired, ValidItem, Fits32, min32, max32, maxCount]
  · decide

end FlexViolation
