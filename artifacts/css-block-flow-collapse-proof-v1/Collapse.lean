import Std
set_option autoImplicit false
namespace Collapse

structure Summary where
  positive : Int
  negative : Int
  deriving DecidableEq

def join (a b : Summary) : Summary :=
  ⟨max a.positive b.positive, min a.negative b.negative⟩
def single (x : Int) : Summary := ⟨max 0 x, min 0 x⟩
def value (a : Summary) : Int := a.positive + a.negative

theorem join_comm (a b : Summary) : join a b = join b a := by
  cases a; cases b; simp only [join]; congr 1 <;> omega

theorem join_assoc (a b c : Summary) : join (join a b) c = join a (join b c) := by
  cases a; cases b; cases c; simp only [join]; congr 1 <;> omega

theorem join_idempotent (a : Summary) : join a a = a := by
  cases a; simp [join]

theorem single_bounds (x : Int) : 0 ≤ (single x).positive ∧ (single x).negative ≤ 0 := by
  simp only [single]; omega

theorem signed_information_needed :
    value (join (single 10) (single (-8))) = 2 ∧
    value (join (join (single 10) (single (-8))) (single 5)) = 2 ∧
    value (join (single 2) (single 5)) = 5 := by decide

def endpoint (basis : Int) : Int := max 0 (min basis (1000 - basis))
theorem endpoint_counterexample :
    endpoint 0 = 0 ∧ endpoint 1073741823 = 0 ∧ endpoint 100 = 100 := by decide

structure Dimensions where
  preferred : Option Nat
  minimum : Option Nat
  paddingStart : Nat
  paddingEnd : Nat
  deriving DecidableEq

def positive (x : Option Nat) : Bool := match x with
  | none => false
  | some n => n > 0

def separates (d : Dimensions) : Bool :=
  d.paddingStart != 0 || d.paddingEnd != 0 || positive d.preferred || positive d.minimum

def refine (old hidden : Bool) (d : Dimensions) : Bool := old && (hidden || !separates d)

theorem old_nonempty (hidden : Bool) (d : Dimensions) : refine false hidden d = false := by
  simp [refine]
theorem hidden_preserved (old : Bool) (d : Dimensions) : refine old true d = old := by
  simp [refine]
theorem no_separator_preserved (old hidden : Bool) (d : Dimensions) (h : separates d = false) :
    refine old hidden d = old := by simp [refine, h]
theorem positive_rejected (old : Bool) (d : Dimensions) (h : separates d = true) :
    refine old false d = false := by simp [refine, h]
theorem unknown_not_positive : positive none = false := rfl
theorem finite_maximum_positive : positive (some 1073741822) = true := by decide
theorem minimum_separator :
    refine true false ⟨none, some 1, 0, 0⟩ = false := by decide
theorem end_padding_separator :
    refine true false ⟨none, none, 0, 1⟩ = false := by decide

inductive Edge where
  | start (id : Nat) (margin : Int)
  | finish (id : Nat) (margin : Int)
  deriving DecidableEq

def edgeMargin : Edge → Int
  | .start _ n | .finish _ n => n

def aggregate : List Edge → Summary
  | [] => ⟨0, 0⟩
  | e :: rest => join (single (edgeMargin e)) (aggregate rest)

theorem aggregate_bounds (edges : List Edge) :
    0 ≤ (aggregate edges).positive ∧ (aggregate edges).negative ≤ 0 := by
  induction edges with
  | nil => simp [aggregate]
  | cons edge rest ih =>
    have h := single_bounds (edgeMargin edge)
    simp only [aggregate, join]
    constructor <;> omega

theorem aggregate_append (xs ys : List Edge) :
    aggregate (xs ++ ys) = join (aggregate xs) (aggregate ys) := by
  induction xs with
  | nil =>
    simp only [List.nil_append, aggregate]
    have h := aggregate_bounds ys
    cases eq : aggregate ys with
    | mk pos neg =>
      rw [eq] at h
      change 0 ≤ pos ∧ neg ≤ 0 at h
      simp only [join]
      congr 1 <;> omega
  | cons e rest ih =>
    simp only [List.cons_append, aggregate]
    rw [ih, join_assoc]

theorem duplicate_trace_invariant (edges : List Edge) :
    aggregate (edges ++ edges) = aggregate edges := by
  rw [aggregate_append, join_idempotent]

theorem chunk_order_invariant (xs ys : List Edge) :
    aggregate (xs ++ ys) = aggregate (ys ++ xs) := by
  rw [aggregate_append, aggregate_append, join_comm]

structure Frame where
  id : Nat
  start : Int
  finish : Int
  selfEmpty : Bool
  fallbackEmpty : Bool
  hidden : Bool
  marginRoot : Bool
  dimensions : Dimensions
  deriving DecidableEq

mutual
inductive Tree where
  | frame (data : Frame) (children : Forest)
  deriving DecidableEq
inductive Forest where
  | nil
  | child (tree : Tree) (rest : Forest)
  | inline (empty : Bool) (rest : Forest)
  | clearance (amount : Int) (rest : Forest)
  deriving DecidableEq
end

structure Result where
  edges : List Edge
  through : Bool
  deriving DecidableEq

def startOf : Tree → Edge
  | .frame f _ => .start f.id f.start
def endOf : Tree → Edge
  | .frame f _ => .finish f.id f.finish

def finishFrame (revised : Bool) (f : Frame) (r : Result) : Result :=
  ⟨.start f.id f.start :: r.edges, if revised then refine (f.selfEmpty && r.through) f.hidden f.dimensions else f.selfEmpty && r.through⟩
def fallbackFrame (revised : Bool) (f : Frame) : Result :=
  ⟨[.start f.id f.start], if revised then refine f.fallbackEmpty f.hidden f.dimensions else f.fallbackEmpty⟩

mutual
def visitWith (revised : Bool) : Tree → Result
  | .frame f children =>
    if f.marginRoot || f.dimensions.paddingStart != 0 then fallbackFrame revised f
    else finishFrame revised f (childrenWith revised children)
def childrenWith (revised : Bool) : Forest → Result
  | .nil => ⟨[], true⟩
  | .child t rest =>
    let child := visitWith revised t
    if child.through then
      let later := childrenWith revised rest
      ⟨child.edges ++ [endOf t] ++ later.edges, later.through⟩
    else child
  | .inline empty rest => if empty then childrenWith revised rest else ⟨[], false⟩
  | .clearance _ _ => ⟨[], false⟩
end

def visit := visitWith true
def visitChildren := childrenWith true

theorem own_start_preserved (t : Tree) : (visit t).edges.head? = some (startOf t) := by
  cases t with
  | frame f children => simp only [visit, visitWith]; split <;> rfl

theorem positive_parent_keeps_child_start (f : Frame) (children : Forest)
    (root : f.marginRoot = false) (padding : f.dimensions.paddingStart = 0) :
    (visit (.frame f children)).edges = .start f.id f.start :: (visitChildren children).edges := by
  simp [visit, visitWith, root, padding, finishFrame, visitChildren]

theorem next_sibling_only_after_through (t : Tree) (rest : Forest)
    (h : (visit t).through = false) :
    visitChildren (.child t rest) = visit t := by
  simp only [visit] at h
  simp [visitChildren, childrenWith, visit, h]

theorem through_admits_end_and_rest (t : Tree) (rest : Forest)
    (h : (visit t).through = true) :
    (visitChildren (.child t rest)).edges =
      (visit t).edges ++ [endOf t] ++ (visitChildren rest).edges := by
  simp only [visit] at h
  simp [visitChildren, childrenWith, visit, h]

theorem nonempty_suppresses_only_future (t : Tree) (rest : Forest)
    (h : (visit t).through = false) :
    (visitChildren (.child t rest)).edges = (visit t).edges := by
  rw [next_sibling_only_after_through t rest h]

theorem separating_frame_reports_nonempty (f : Frame) (children : Forest)
    (hidden : f.hidden = false) (separation : separates f.dimensions = true) :
    (visit (.frame f children)).through = false := by
  simp only [visit, visitWith]
  split <;> simp [fallbackFrame, finishFrame, refine, hidden, separation]

theorem positive_child_suppresses_end_and_later (f : Frame) (children rest : Forest)
    (hidden : f.hidden = false) (separation : separates f.dimensions = true) :
    visitChildren (.child (.frame f children) rest) = visit (.frame f children) :=
  next_sibling_only_after_through _ _ (separating_frame_reports_nonempty f children hidden separation)

theorem positive_child_start_retained (f : Frame) (children rest : Forest)
    (hidden : f.hidden = false) (separation : separates f.dimensions = true) :
    (visitChildren (.child (.frame f children) rest)).edges.head? = some (.start f.id f.start) := by
  rw [positive_child_suppresses_end_and_later f children rest hidden separation]
  exact own_start_preserved (.frame f children)

theorem positive_child_subtree_starts_retained (f : Frame) (children rest : Forest)
    (hidden : f.hidden = false) (separation : separates f.dimensions = true)
    (root : f.marginRoot = false) (padding : f.dimensions.paddingStart = 0) :
    (visitChildren (.child (.frame f children) rest)).edges =
      .start f.id f.start :: (visitChildren children).edges := by
  rw [positive_child_suppresses_end_and_later f children rest hidden separation]
  exact positive_parent_keeps_child_start f children root padding

theorem nonempty_inline_stops (rest : Forest) :
    visitChildren (.inline false rest) = ⟨[], false⟩ := rfl

theorem zero_clearance_is_present (rest : Forest) :
    visitChildren (.clearance 0 rest) = ⟨[], false⟩ := rfl

theorem empty_inline_preserves (rest : Forest) :
    visitChildren (.inline true rest) = visitChildren rest := rfl

def zeroDims : Dimensions := ⟨none, some 0, 0, 0⟩
def f (id : Nat) (start finish : Int) (dims : Dimensions) : Frame :=
  ⟨id, start, finish, true, true, false, false, dims⟩
def leaf (id : Nat) (start finish : Int) (dims : Dimensions) : Tree :=
  .frame (f id start finish dims) .nil

def witness (dims : Dimensions) : Tree :=
  .frame (f 0 0 0 zeroDims)
    (.child (leaf 1 10 20 dims) (.child (leaf 2 80 0 zeroDims) .nil))

theorem original_membership :
    (visitWith false (witness ⟨some 10, some 0, 0, 0⟩)).edges =
      [.start 0 0, .start 1 10, .finish 1 20, .start 2 80, .finish 2 0] := by decide

theorem repaired_membership :
    (visit (witness ⟨some 10, some 0, 0, 0⟩)).edges = [.start 0 0, .start 1 10] := by decide

theorem witness_values :
    value (aggregate (visitWith false (witness ⟨some 10, some 0, 0, 0⟩)).edges) = 80 ∧
    value (aggregate (visit (witness ⟨some 10, some 0, 0, 0⟩)).edges) = 10 := by decide

theorem late_guard_needed :
    let positiveParent := .frame (f 1 10 20 ⟨some 10, some 0, 0, 0⟩)
      (.child (leaf 2 40 0 zeroDims) .nil)
    (visit positiveParent).edges = [.start 1 10, .start 2 40, .finish 2 0] ∧
    (visit positiveParent).through = false := by decide

#print axioms join_comm
#print axioms join_assoc
#print axioms join_idempotent
#print axioms single_bounds
#print axioms signed_information_needed
#print axioms endpoint_counterexample
#print axioms old_nonempty
#print axioms hidden_preserved
#print axioms no_separator_preserved
#print axioms positive_rejected
#print axioms unknown_not_positive
#print axioms finite_maximum_positive
#print axioms minimum_separator
#print axioms end_padding_separator
#print axioms own_start_preserved
#print axioms positive_parent_keeps_child_start
#print axioms next_sibling_only_after_through
#print axioms through_admits_end_and_rest
#print axioms nonempty_suppresses_only_future
#print axioms nonempty_inline_stops
#print axioms zero_clearance_is_present
#print axioms empty_inline_preserves
#print axioms original_membership
#print axioms repaired_membership
#print axioms witness_values
#print axioms late_guard_needed
#print axioms aggregate_bounds
#print axioms aggregate_append
#print axioms duplicate_trace_invariant
#print axioms chunk_order_invariant
#print axioms separating_frame_reports_nonempty
#print axioms positive_child_suppresses_end_and_later
#print axioms positive_child_start_retained
#print axioms positive_child_subtree_starts_retained
end Collapse
