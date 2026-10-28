import Std

namespace RoundSmallStep

def distance (x y : Int) : Int := if x < y then y - x else x - y

structure Neighbors (allowed : Int → Prop) (p a n : Int) : Prop where
  center : allowed a
  lower : p < a
  upper : a < n
  gap : ∀ x, allowed x → x ≤ p ∨ x = a ∨ n ≤ x

def Cell (p a n y : Int) : Prop := p + a < 2 * y ∧ 2 * y < a + n

def NearestAt (allowed : Int → Prop) (project : Int → Int) (y : Int) : Prop :=
  allowed (project y) ∧ ∀ x, allowed x → distance (project y) y ≤ distance x y

structure Reconstruction (a b r t l u e₁ e₂ : Int) : Prop where
  positiveStep : 0 < b
  remainderLower : -b < r
  remainderUpper : r < b
  sign : if a < 0 then r ≤ 0 else 0 ≤ r
  error₁ : 0 ≤ e₁
  error₂ : 0 ≤ e₂
  subtractLower : a - r - e₁ ≤ t
  subtractUpper : t ≤ a - r + e₁
  lower : if a < 0 then t - b - e₂ ≤ l ∧ l ≤ t - b + e₂ else l = t
  upper : if a < 0 then u = t else t + b - e₂ ≤ u ∧ u ≤ t + b + e₂

def exactLower (a b r : Int) : Int := if a < 0 then a - r - b else a - r
def exactUpper (a b r : Int) : Int := if a < 0 then a - r else a - r + b

theorem cell_unique_nearest {allowed : Int → Prop} {p a n y : Int}
    (neighbors : Neighbors allowed p a n) (cell : Cell p a n y) :
    ∀ x, allowed x → x ≠ a → distance a y < distance x y := by
  intro x member different
  have lo := neighbors.lower
  have hi := neighbors.upper
  rcases neighbors.gap x member with left | same | right
  · unfold Cell at cell
    unfold distance
    split <;> split <;> omega
  · exact False.elim (different same)
  · unfold Cell at cell
    unfold distance
    split <;> split <;> omega

theorem reconstruction_cells {a b r t l u e₁ e₂ p n : Int}
    (h : Reconstruction a b r t l u e₁ e₂)
    (leftMargin : 2 * (b + e₁ + e₂) < a - p)
    (rightMargin : 2 * (b + e₁ + e₂) < n - a) :
    Cell p a n l ∧ Cell p a n u ∧
    Cell p a n (exactLower a b r) ∧ Cell p a n (exactUpper a b r) := by
  rcases h with ⟨positive, rlo, rhi, sign, e₁pos, e₂pos, tlo, thi, lower, upper⟩
  by_cases negative : a < 0
  · simp only [negative, ↓reduceIte] at sign lower upper
    simp only [Cell, exactLower, exactUpper, negative, ↓reduceIte]
    omega
  · simp only [negative, ↓reduceIte] at sign lower upper
    simp only [Cell, exactLower, exactUpper, negative, ↓reduceIte]
    omega

theorem small_step_projection {allowed : Int → Prop} {project : Int → Int}
    {a b r t l u e₁ e₂ p n chosen reference : Int}
    (neighbors : Neighbors allowed p a n)
    (projection : NearestAt allowed project l ∧ NearestAt allowed project u ∧
      NearestAt allowed project (exactLower a b r) ∧
      NearestAt allowed project (exactUpper a b r))
    (h : Reconstruction a b r t l u e₁ e₂)
    (leftMargin : 2 * (b + e₁ + e₂) < a - p)
    (rightMargin : 2 * (b + e₁ + e₂) < n - a)
    (selected : chosen = l ∨ chosen = u)
    (referenceSelected : reference = exactLower a b r ∨ reference = exactUpper a b r) :
    project chosen = a ∧ project reference = a := by
  have cells := reconstruction_cells h leftMargin rightMargin
  have projected (y : Int) (cell : Cell p a n y)
      (nearest : NearestAt allowed project y) : project y = a := by
    by_cases same : project y = a
    · exact same
    · have strict := cell_unique_nearest neighbors cell (project y) nearest.1 same
      have minimal := nearest.2 a neighbors.center
      omega
  constructor
  · rcases selected with rfl | rfl
    · exact projected _ cells.1 projection.1
    · exact projected _ cells.2.1 projection.2.1
  · rcases referenceSelected with rfl | rfl
    · exact projected _ cells.2.2.1 projection.2.2.1
    · exact projected _ cells.2.2.2 projection.2.2.2

example : Reconstruction (2^149) 5 2 (2^149) (2^149) (2^149) 2 5 := by
  constructor <;> decide

example :
    Cell ((2^149)-(2^125)) (2^149) ((2^149)+(2^126)) ((2^149)-2) ∧
    Cell ((2^149)-(2^125)) (2^149) ((2^149)+(2^126)) ((2^149)+3) := by
  constructor <;> unfold Cell <;> decide

example : 2 * ((5 : Int) + 2 + 5) < 2^125 ∧
    2 * ((5 : Int) + 2 + 5) < 2^126 := by decide

example : ¬ Cell 2 4 8 3 ∧ distance 4 3 = distance 2 3 := by
  unfold Cell
  decide

example : distance 8 5 < (16 - 8) / 2 ∧ distance 4 5 < distance 8 5 := by decide

example : Reconstruction 17 2 1 11 11 13 5 0 ∧
    2 * (2 : Int) < 17 - 9 ∧ 2 * (2 : Int) < 33 - 17 ∧
    distance 9 11 < distance 17 11 := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · constructor <;> decide
  all_goals decide

example : NearestAt (fun x : Int => x = 0) (fun y => if y = 0 then 0 else 1) 0 := by
  unfold NearestAt
  constructor
  · simp
  · intro x equal
    subst x
    simp [distance]

example : ¬ (∀ y, NearestAt (fun x : Int => x = 0)
    (fun z => if z = 0 then 0 else 1) y) := by
  intro total
  have impossible := (total 1).1
  simp at impossible

#print axioms cell_unique_nearest
#print axioms reconstruction_cells
#print axioms small_step_projection

end RoundSmallStep
