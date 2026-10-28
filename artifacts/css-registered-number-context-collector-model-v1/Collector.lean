namespace NumberContext

inductive Demand where
  | font | lineHeight | rootFont | rootLineHeight
  deriving DecidableEq, Repr

structure Flags where
  font : Bool
  lineHeight : Bool
  rootFont : Bool
  rootLineHeight : Bool
  deriving DecidableEq, Repr

def empty : Flags := ⟨false, false, false, false⟩
def union (a b : Flags) : Flags :=
  ⟨a.font || b.font, a.lineHeight || b.lineHeight,
   a.rootFont || b.rootFont, a.rootLineHeight || b.rootLineHeight⟩
def singleton : Demand → Flags
  | .font => ⟨true, false, false, false⟩
  | .lineHeight => ⟨false, true, false, false⟩
  | .rootFont => ⟨false, false, true, false⟩
  | .rootLineHeight => ⟨false, false, false, true⟩
def has (f : Flags) : Demand → Bool
  | .font => f.font
  | .lineHeight => f.lineHeight
  | .rootFont => f.rootFont
  | .rootLineHeight => f.rootLineHeight

theorem union_assoc (a b c : Flags) : union (union a b) c = union a (union b c) := by
  cases a; cases b; cases c; simp [union, Bool.or_assoc]
theorem union_empty (a : Flags) : union a empty = a ∧ union empty a = a := by
  cases a; simp [union, empty]
theorem has_union (a b : Flags) (d : Demand) : has (union a b) d = (has a d || has b d) := by
  cases d <;> rfl

def merge : Option Flags → Option Flags → Option Flags
  | some a, some b => some (union a b)
  | _, _ => none

theorem merge_assoc (a b c : Option Flags) : merge (merge a b) c = merge a (merge b c) := by
  cases a <;> cases b <;> cases c <;> simp [merge, union_assoc]
theorem merge_empty (a : Option Flags) : merge a (some empty) = a ∧ merge (some empty) a = a := by
  cases a <;> simp [merge, union_empty]
theorem unknown_absorbs (a : Option Flags) : merge none a = none ∧ merge a none = none := by
  cases a <;> simp [merge]

inductive Leaf where
  | number | angle | time | resolution | absolute
  | font | lineHeight | rootFont | rootLineHeight
  | percentage | color | treeCount | randomKey | viewport | container | characterWidth
  deriving DecidableEq, Repr
inductive Unary where
  | negate | invert | sin | cos | tan | asin | acos | atan | sqrt | exp | abs | sign | log
  deriving DecidableEq, Repr
inductive Binary where
  | round | modRem | atan2 | pow | logBase
  deriving DecidableEq, Repr
inductive Ternary where
  | clamp | progress
  deriving DecidableEq, Repr
inductive Variadic where
  | sum | product | minMax | hypot
  deriving DecidableEq, Repr
inductive Unsupported where
  | random | anchor | anchorSize
  deriving DecidableEq, Repr
inductive Expr where
  | leaf (kind : Leaf)
  | unary (op : Unary) (child : Expr)
  | binary (op : Binary) (left right : Expr)
  | ternary (op : Ternary) (first second third : Expr)
  | variadic (op : Variadic) (children : List Expr)
  | unsupported (op : Unsupported)
  deriving Repr

def leafSummary : Leaf → Option Flags
  | .number | .angle | .time | .resolution | .absolute => some empty
  | .font => some (singleton .font)
  | .lineHeight => some (union (singleton .font) (singleton .lineHeight))
  | .rootFont => some (singleton .rootFont)
  | .rootLineHeight => some (union (singleton .rootFont) (singleton .rootLineHeight))
  | .percentage | .color | .treeCount | .randomKey | .viewport | .container | .characterWidth => none

mutual
 def summary : Expr → Option Flags
  | .leaf k => leafSummary k
  | .unary _ e => summary e
  | .binary _ a b => merge (summary a) (summary b)
  | .ternary _ a b c => merge (summary a) (merge (summary b) (summary c))
  | .variadic _ es => summaries es
  | .unsupported _ => none
 def summaries : List Expr → Option Flags
  | [] => some empty
  | e :: es => merge (summary e) (summaries es)
end

inductive Event where
  | read (demand : Demand)
  | unsupported
  deriving DecidableEq, Repr

def leafEvents : Leaf → List Event
  | .number | .angle | .time | .resolution | .absolute => []
  | .font => [.read .font]
  | .lineHeight => [.read .font, .read .lineHeight]
  | .rootFont => [.read .rootFont]
  | .rootLineHeight => [.read .rootFont, .read .rootLineHeight]
  | .percentage | .color | .treeCount | .randomKey | .viewport | .container | .characterWidth => [.unsupported]

mutual
 def events : Expr → List Event
  | .leaf k => leafEvents k
  | .unary _ e => events e
  | .binary _ a b => events a ++ events b
  | .ternary _ a b c => events a ++ events b ++ events c
  | .variadic _ es => eventsList es
  | .unsupported _ => [.unsupported]
 def eventsList : List Expr → List Event
  | [] => []
  | e :: es => events e ++ eventsList es
end

def eventSummary : Event → Option Flags
  | .read d => some (singleton d)
  | .unsupported => none

def summarizeEvents : List Event → Option Flags
  | [] => some empty
  | x :: xs => merge (eventSummary x) (summarizeEvents xs)

theorem summarize_append (a b : List Event) :
    summarizeEvents (a ++ b) = merge (summarizeEvents a) (summarizeEvents b) := by
  induction a with
  | nil => simp [summarizeEvents, merge_empty]
  | cons x xs ih => simp [summarizeEvents, ih, merge_assoc]

theorem leaf_correspondence (k : Leaf) : leafSummary k = summarizeEvents (leafEvents k) := by
  cases k <;> decide

theorem summary_correspondence (e : Expr) : summary e = summarizeEvents (events e) := by
  apply Expr.rec
    (motive_1 := fun e => summary e = summarizeEvents (events e))
    (motive_2 := fun es => summaries es = summarizeEvents (eventsList es))
  · intro k; exact leaf_correspondence k
  · intro op e ih; exact ih
  · intro op a b ha hb; simp [summary, events, summarize_append, ha, hb]
  · intro op a b c ha hb hc
    simp [summary, events, summarize_append, ha, hb, hc]
  · intro op es ih; exact ih
  · intro op; rfl
  · rfl
  · intro e es he hes; simp [summaries, eventsList, summarize_append, he, hes]

theorem events_unknown_iff (xs : List Event) :
    summarizeEvents xs = none ↔ Event.unsupported ∈ xs := by
  induction xs with
  | nil => simp [summarizeEvents]
  | cons x xs ih =>
    cases x with
    | unsupported => simp [summarizeEvents, eventSummary, merge]
    | read d =>
      cases h : summarizeEvents xs <;> simp_all [summarizeEvents, eventSummary, merge]

theorem summary_unknown_iff (e : Expr) :
    summary e = none ↔ Event.unsupported ∈ events e := by
  rw [summary_correspondence]; exact events_unknown_iff _

theorem events_read_exact (xs : List Event) (f : Flags)
    (h : summarizeEvents xs = some f) (d : Demand) :
    has f d = true ↔ Event.read d ∈ xs := by
  induction xs generalizing f with
  | nil => simp [summarizeEvents] at h; cases h; cases d <;> simp [has, empty]
  | cons x xs ih =>
    cases x with
    | unsupported => simp [summarizeEvents, eventSummary, merge] at h
    | read a =>
      cases hs : summarizeEvents xs with
      | none => simp [summarizeEvents, eventSummary, hs, merge] at h
      | some g =>
        simp [summarizeEvents, eventSummary, hs, merge] at h
        cases h
        rw [has_union, Bool.or_eq_true_iff]
        have tail := ih g hs
        cases a <;> cases d <;> simp_all [has, singleton]

theorem supported_read_exact (e : Expr) (f : Flags) (h : summary e = some f) (d : Demand) :
    has f d = true ↔ Event.read d ∈ events e := by
  rw [summary_correspondence] at h
  exact events_read_exact _ f h d

theorem supported_absence_no_read (e : Expr) (f : Flags) (h : summary e = some f)
    (d : Demand) (absent : has f d = false) : Event.read d ∉ events e := by
  intro present
  have := (supported_read_exact e f h d).mpr present
  simp_all

theorem supported_empty_no_reads (e : Expr) (h : summary e = some empty) (d : Demand) :
    Event.read d ∉ events e := by
  apply supported_absence_no_read e empty h d
  cases d <;> rfl

theorem inverse_preserves_summary (e : Expr) : summary (.unary .invert e) = summary e := rfl

theorem binary_retains_both (op : Binary) (a b : Expr) (x y : Flags)
    (ha : summary a = some x) (hb : summary b = some y) :
    summary (.binary op a b) = some (union x y) := by
  simp [summary, ha, hb, merge]

theorem ternary_retains_all (op : Ternary) (a b c : Expr) (x y z : Flags)
    (ha : summary a = some x) (hb : summary b = some y) (hc : summary c = some z) :
    summary (.ternary op a b c) = some (union x (union y z)) := by
  simp [summary, ha, hb, hc, merge]

theorem binary_unknown_left (op : Binary) (a b : Expr) (h : summary a = none) :
    summary (.binary op a b) = none := by simp [summary, h, merge]
theorem binary_unknown_right (op : Binary) (a b : Expr) (h : summary b = none) :
    summary (.binary op a b) = none := by
  simp [summary, h]; cases summary a <;> rfl


theorem eventsList_contains (e : Expr) (es : List Expr) (member : e ∈ es)
    (x : Event) (present : x ∈ events e) : x ∈ eventsList es := by
  induction es with
  | nil => simp at member
  | cons a rest ih =>
    simp only [List.mem_cons] at member
    rcases member with same | later
    · subst a; simp [eventsList, present]
    · have tail := ih later
      simp [eventsList, tail]

theorem variadic_unknown_member (op : Variadic) (es : List Expr) (e : Expr)
    (member : e ∈ es) (unknown : summary e = none) : summary (.variadic op es) = none := by
  apply (summary_unknown_iff _).mpr
  exact eventsList_contains e es member .unsupported ((summary_unknown_iff e).mp unknown)

theorem variadic_retains_every_read (op : Variadic) (es : List Expr) (e : Expr)
    (member : e ∈ es) (d : Demand) (read : Event.read d ∈ events e)
    (f : Flags) (supported : summary (.variadic op es) = some f) : has f d = true := by
  apply (supported_read_exact _ f supported d).mpr
  exact eventsList_contains e es member (.read d) read

theorem union_comm (a b : Flags) : union a b = union b a := by
  cases a; cases b; simp [union, Bool.or_comm]
theorem union_idempotent (a : Flags) : union a a = a := by
  cases a; simp [union]

end NumberContext
