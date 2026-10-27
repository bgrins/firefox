import Init

namespace CounterDelivery

abbrev Name := Nat
abbrev Owner := List Nat

structure Binding where
  scope : Nat
  value : Int
  deriving DecidableEq, Repr

abbrev Stack := List Binding

inductive Change where
  | reset (scope dropInner : Nat) (value : Int)
  | set (implicitScope : Nat) (value : Int)
  | increment (implicitScope : Nat) (delta : Int)
  | use
  deriving DecidableEq, Repr

def apply : Change → Stack → Stack
  | .reset scope dropInner value, stack => ⟨scope, value⟩ :: stack.drop dropInner
  | .set scope value, [] => [⟨scope, value⟩]
  | .set _ value, head :: tail => { head with value := value } :: tail
  | .increment scope delta, [] => [⟨scope, delta⟩]
  | .increment _ delta, head :: tail => { head with value := head.value + delta } :: tail
  | .use, stack => stack

structure Recipe where
  source : Option Nat
  change : Change
  deriving DecidableEq, Repr

abbrev Table := Name → List (Owner × Stack)

def read (recipe : Recipe) (rows : List (Owner × Stack)) : Stack :=
  match recipe.source with
  | none => []
  | some i => ((rows[i]?).map Prod.snd).getD []

def calculate (recipe : Recipe) (rows : List (Owner × Stack)) : Stack :=
  apply recipe.change (read recipe rows)

structure Edit where
  name : Name
  owner : Owner
  oldRecipe : Recipe
  newRecipe : Recipe
  deriving DecidableEq, Repr

def push (table : Table) (edit : Edit) (stack : Stack) : Table :=
  fun name => if name = edit.name then table name ++ [(edit.owner, stack)] else table name

def full (current : Bool) (table : Table) : List Edit → List Stack
  | [] => []
  | edit :: rest =>
    let value := calculate (if current then edit.newRecipe else edit.oldRecipe) (table edit.name)
    value :: full current (push table edit value) rest

def deliver (dirty : Name → Bool) (table : Table) : List Edit → List Stack → List Stack
  | [], _ => []
  | edit :: rest, cache =>
    let value := if dirty edit.name then calculate edit.newRecipe (table edit.name)
      else cache.headD []
    value :: deliver dirty (push table edit value) rest cache.tail

def CleanAgree (dirty : Name → Bool) (old current : Table) : Prop :=
  ∀ name, dirty name = false → old name = current name

def UnchangedClean (dirty : Name → Bool) (edits : List Edit) : Prop :=
  ∀ edit ∈ edits, dirty edit.name = false → edit.oldRecipe = edit.newRecipe

def ValidSource (table : Table) (edit : Edit) (recipe : Recipe) : Prop :=
  match recipe.source with
  | none => True
  | some i => ∃ sourceOwner stack, (table edit.name)[i]? = some (sourceOwner, stack) ∧
      sourceOwner.isPrefixOf edit.owner = true

def Ordered (current : Bool) (table : Table) : List Edit → Prop
  | [] => True
  | edit :: rest =>
    let recipe := if current then edit.newRecipe else edit.oldRecipe
    ValidSource table edit recipe ∧
      Ordered current (push table edit (calculate recipe (table edit.name))) rest

def counter (stack : Stack) : Int := (stack.headD ⟨0, 0⟩).value

def counters (stack : Stack) : List Int := (stack.map Binding.value).reverse

theorem set_preserves_existing_scope (id : Nat) (value : Int) (head : Binding) (tail : Stack) :
    (apply (.set id value) (head :: tail)).map Binding.scope = (head :: tail).map Binding.scope := by
  rfl

theorem increment_preserves_outer (id : Nat) (delta : Int) (head : Binding) (tail : Stack) :
    (apply (.increment id delta) (head :: tail)).tail = tail := by
  rfl

theorem increment_counter (id : Nat) (delta : Int) (head : Binding) (tail : Stack) :
    counter (apply (.increment id delta) (head :: tail)) = head.value + delta := by
  rfl

theorem reset_retains_selected_outer (id dropInner : Nat) (value : Int) (stack : Stack) :
    counters (apply (.reset id dropInner value) stack) =
      counters (stack.drop dropInner) ++ [value] := by
  simp [counters, apply]

theorem use_preserves_stack (stack : Stack) : apply .use stack = stack := by rfl

theorem clean_calculation (dirty : Name → Bool) (old current : Table)
    (edit : Edit) (agree : CleanAgree dirty old current)
    (clean : dirty edit.name = false) (same : edit.oldRecipe = edit.newRecipe) :
    calculate edit.oldRecipe (old edit.name) = calculate edit.newRecipe (current edit.name) := by
  rw [same, agree edit.name clean]

theorem push_clean_agree (dirty : Name → Bool) (old current : Table)
    (edit : Edit) (oldValue currentValue : Stack)
    (agree : CleanAgree dirty old current)
    (same : dirty edit.name = false → oldValue = currentValue) :
    CleanAgree dirty (push old edit oldValue) (push current edit currentValue) := by
  intro name clean
  by_cases eq : name = edit.name
  · subst name
    simp only [push, ↓reduceIte]
    rw [agree edit.name clean, same clean]
  · simp only [push, ite_eq_right eq]
    exact agree name clean

theorem dirty_delivery_equals_current (dirty : Name → Bool) (old current : Table)
    (edits : List Edit) (agree : CleanAgree dirty old current)
    (unchanged : UnchangedClean dirty edits) :
    deliver dirty current edits (full false old edits) = full true current edits := by
  induction edits generalizing old current with
  | nil => rfl
  | cons edit rest ih =>
    have equalClean : dirty edit.name = false →
        calculate edit.oldRecipe (old edit.name) = calculate edit.newRecipe (current edit.name) := by
      intro clean
      exact clean_calculation dirty old current edit agree clean
        (unchanged edit (by simp) clean)
    have choice : (if dirty edit.name then calculate edit.newRecipe (current edit.name)
        else calculate edit.oldRecipe (old edit.name)) =
        calculate edit.newRecipe (current edit.name) := by
      cases h : dirty edit.name with
      | false => simp [equalClean h]
      | true => simp
    simp only [full, Bool.false_eq_true, ↓reduceIte, List.headD_cons,
      deliver, List.tail_cons]
    rw [choice]
    congr 1
    apply ih
    · exact push_clean_agree dirty old current edit _ _ agree equalClean
    · intro entry member clean
      exact unchanged entry (by simp [member]) clean

theorem all_names_delivery (table : Table) (edits : List Edit) :
    deliver (fun _ => true) table edits (full false table edits) = full true table edits := by
  apply dirty_delivery_equals_current
  · intro name impossible
    contradiction
  · intro edit member impossible
    contradiction

theorem no_dirty_no_edit (table : Table) (edits : List Edit)
    (unchanged : UnchangedClean (fun _ => false) edits) :
    deliver (fun _ => false) table edits (full false table edits) = full true table edits := by
  apply dirty_delivery_equals_current
  · intro name clean
    rfl
  · exact unchanged

theorem append_preserves_clean (dirty : Name → Bool) (table : Table)
    (edit : Edit) (marked : dirty edit.name = true) (value : Stack) :
    CleanAgree dirty table (push table edit value) := by
  intro name clean
  have different : name ≠ edit.name := by
    intro equal
    subst name
    rw [marked] at clean
    contradiction
  simp [push, different]

theorem append_then_deliver (dirty : Name → Bool) (table : Table)
    (parent : Edit) (marked : dirty parent.name = true) (descendants : List Edit)
    (unchanged : UnchangedClean dirty descendants) :
    let updated := push table parent (calculate parent.newRecipe (table parent.name))
    deliver dirty updated descendants (full false table descendants) =
      full true updated descendants := by
  apply dirty_delivery_equals_current
  · exact append_preserves_clean dirty table parent marked _
  · exact unchanged

theorem childless_fastpath (dirty : Name → Bool) (table : Table) (parent : Edit) :
    deliver dirty (push table parent (calculate parent.newRecipe (table parent.name))) [] [] = [] := by
  rfl

end CounterDelivery
