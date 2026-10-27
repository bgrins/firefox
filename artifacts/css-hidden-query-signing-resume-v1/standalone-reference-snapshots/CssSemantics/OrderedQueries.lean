import CssSemantics.ScopedSelectors
import CssSemantics.ContentPreorder

namespace CssSemantics.OrderedQueries

inductive Selected {Node : Type} (predicate : Node → Prop) : List Node → List Node → Prop
  | nil : Selected predicate [] []
  | keep {node rest result} : predicate node → Selected predicate rest result →
      Selected predicate (node :: rest) (node :: result)
  | skip {node rest result} : ¬ predicate node → Selected predicate rest result →
      Selected predicate (node :: rest) result

theorem Selected.result {Node : Type} {predicate : Node → Prop} (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node)
    {input output : List Node} (h : Selected predicate input output) : input.filter test = output := by
  induction h with
  | nil => rfl
  | keep yes _ ih => simp [ (correspondence _).mpr yes, ih]
  | skip no _ ih =>
      have ht : test _ = false := Bool.eq_false_iff.mpr fun h => no ((correspondence _).mp h)
      simp [ ht, ih]

theorem selected_spec {Node : Type} (predicate : Node → Prop) (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node) (input : List Node) :
    Selected predicate input (input.filter test) := by
  induction input with
  | nil => exact .nil
  | cons node rest ih =>
      cases ht : test node with
      | true => simpa [List.filter_cons, ht] using Selected.keep ((correspondence _).mp ht) ih
      | false =>
          have hn : ¬ predicate node := fun h => by simpa [ht] using (correspondence _).mpr h
          simpa [List.filter_cons, ht] using Selected.skip hn ih

theorem selected_iff {Node : Type} (predicate : Node → Prop) (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node) (input output : List Node) :
    Selected predicate input output ↔ input.filter test = output := by
  constructor
  · exact Selected.result test correspondence
  · intro h; rw [← h]; exact selected_spec predicate test correspondence input

inductive FirstMatch {Node : Type} (predicate : Node → Prop) : List Node → Option Node → Prop
  | nil : FirstMatch predicate [] none
  | here {node rest} : predicate node → FirstMatch predicate (node :: rest) (some node)
  | skip {node rest result} : ¬ predicate node → FirstMatch predicate rest result →
      FirstMatch predicate (node :: rest) result

theorem FirstMatch.result {Node : Type} {predicate : Node → Prop} (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node)
    {input : List Node} {output : Option Node} (h : FirstMatch predicate input output) :
    (input.filter test).head? = output := by
  induction h with
  | nil => rfl
  | here yes => simp [ (correspondence _).mpr yes]
  | skip no _ ih =>
      have ht : test _ = false := Bool.eq_false_iff.mpr fun h => no ((correspondence _).mp h)
      simp [ ht, ih]

theorem firstMatch_spec {Node : Type} (predicate : Node → Prop) (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node) (input : List Node) :
    FirstMatch predicate input (input.filter test).head? := by
  induction input with
  | nil => exact .nil
  | cons node rest ih =>
      cases ht : test node with
      | true => simpa [List.filter_cons, ht] using FirstMatch.here (rest := rest) ((correspondence _).mp ht)
      | false =>
          have hn : ¬ predicate node := fun h => by simpa [ht] using (correspondence _).mpr h
          simpa [List.filter_cons, ht] using FirstMatch.skip hn ih

theorem firstMatch_iff {Node : Type} (predicate : Node → Prop) (test : Node → Bool)
    (correspondence : ∀ node, test node = true ↔ predicate node) (input : List Node) (output : Option Node) :
    FirstMatch predicate input output ↔ (input.filter test).head? = output := by
  constructor
  · exact FirstMatch.result test correspondence
  · intro h; rw [← h]; exact firstMatch_spec predicate test correspondence input

def all {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) : List Node :=
  (ContentPreorder.descendants context receiver).filter
    (ScopedSyntax.matchesBool context profile (.singleton receiver) selector)

def first {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) : Option Node :=
  (all context profile selector receiver).head?

def AllResults {Node : Type} (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : List Node) : Prop :=
  Selected (ScopedSyntax.Matches context profile (.singleton receiver) selector)
    (ContentPreorder.descendants context receiver) result

def FirstResult {Node : Type} (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : Option Node) : Prop :=
  FirstMatch (ScopedSyntax.Matches context profile (.singleton receiver) selector)
    (ContentPreorder.descendants context receiver) result

theorem all_iff {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : List Node) :
    all context profile selector receiver = result ↔ AllResults context profile selector receiver result := by
  exact (selected_iff _ _ (fun node => ScopedSyntax.matchesBool_iff context profile _ selector node) _ _).symm

theorem first_iff {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : Option Node) :
    first context profile selector receiver = result ↔ FirstResult context profile selector receiver result := by
  exact (firstMatch_iff _ _ (fun node => ScopedSyntax.matchesBool_iff context profile _ selector node) _ _).symm

theorem all_mem_iff {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver candidate : Node) :
    candidate ∈ all context profile selector receiver ↔
      ScopedElement.QueryMember context profile selector receiver candidate := by
  simp only [all, List.mem_filter, ContentPreorder.descendants_mem_iff, ScopedSyntax.matchesBool_iff]
  rfl

theorem all_nodup {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) :
    (all context profile selector receiver).Nodup := by
  exact List.filter_sublist.nodup (ContentPreorder.descendants_nodup context receiver)

theorem AllResults.unique {Node : Type} [DecidableEq Node] (context : ContentContext Node)
    (profile : EmptyProfile) (selector : ScopedSyntax) (receiver : Node) {left right : List Node}
    (hl : AllResults context profile selector receiver left) (hr : AllResults context profile selector receiver right) :
    left = right := by
  exact ((all_iff context profile selector receiver left).mpr hl).symm.trans
    ((all_iff context profile selector receiver right).mpr hr)

theorem FirstResult.unique {Node : Type} [DecidableEq Node] (context : ContentContext Node)
    (profile : EmptyProfile) (selector : ScopedSyntax) (receiver : Node) {left right : Option Node}
    (hl : FirstResult context profile selector receiver left) (hr : FirstResult context profile selector receiver right) :
    left = right := by
  exact ((first_iff context profile selector receiver left).mpr hl).symm.trans
    ((first_iff context profile selector receiver right).mpr hr)

theorem all_sublist {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) :
    (all context profile selector receiver).Sublist (ContentPreorder.descendants context receiver) :=
  List.filter_sublist

theorem first_none_iff {Node : Type} [DecidableEq Node] (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) :
    first context profile selector receiver = none ↔
      ∀ candidate, ¬ ScopedElement.QueryMember context profile selector receiver candidate := by
  simp only [first, all, List.head?_eq_none_iff, List.filter_eq_nil_iff,
    ContentPreorder.descendants_mem_iff, ScopedSyntax.matchesBool_iff]
  constructor
  · intro h candidate ⟨ancestor, matched⟩; exact h candidate ancestor matched
  · intro h candidate ancestor matched; exact h candidate ⟨ancestor, matched⟩

theorem allResults_iff_traversal {Node : Type} (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : List Node) :
    AllResults context profile selector receiver result ↔
      ∃ order, ContentPreorder.Traversal context receiver (receiver :: order) ∧
        Selected (ScopedSyntax.Matches context profile (.singleton receiver) selector) order result := by
  constructor
  · intro selected
    exact ⟨ContentPreorder.descendants context receiver,
      (ContentPreorder.inclusive_iff context receiver _).mp (ContentPreorder.inclusive_eq context receiver), selected⟩
  · rintro ⟨order, traversal, selected⟩
    have same := traversal.result
    rw [ContentPreorder.inclusive_eq] at same
    have order_eq : order = ContentPreorder.descendants context receiver := (List.cons.inj same).2
    simpa [AllResults, order_eq] using selected

theorem firstResult_iff_traversal {Node : Type} (context : ContentContext Node) (profile : EmptyProfile)
    (selector : ScopedSyntax) (receiver : Node) (result : Option Node) :
    FirstResult context profile selector receiver result ↔
      ∃ order, ContentPreorder.Traversal context receiver (receiver :: order) ∧
        FirstMatch (ScopedSyntax.Matches context profile (.singleton receiver) selector) order result := by
  constructor
  · intro selected
    exact ⟨ContentPreorder.descendants context receiver,
      (ContentPreorder.inclusive_iff context receiver _).mp (ContentPreorder.inclusive_eq context receiver), selected⟩
  · rintro ⟨order, traversal, selected⟩
    have same := traversal.result
    rw [ContentPreorder.inclusive_eq] at same
    have order_eq : order = ContentPreorder.descendants context receiver := (List.cons.inj same).2
    simpa [FirstResult, order_eq] using selected

end CssSemantics.OrderedQueries
