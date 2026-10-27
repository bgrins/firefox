import QuoteAppend

namespace QuoteScopes
open QuoteAppend

inductive Content where
  | empty
  | quote (op : Op) (rest : Content)
  | scope (body rest : Content)
  deriving DecidableEq, Repr

inductive Render where
  | empty
  | quote (value : Cell) (rest : Render)
  | scope (body rest : Render)
  deriving DecidableEq, Repr

structure Entry where
  value : Cell
  afterDepth : Nat
  deriving DecidableEq, Repr

def parentPass (p : Provider) (start : Nat) : Content → List Entry
  | .empty => []
  | .quote op rest => ⟨cell p start op, after start op⟩ :: parentPass p (after start op) rest
  | .scope _ rest => parentPass p start rest

def reference (p : Provider) (start : Nat) : Content → Render
  | .empty => .empty
  | .quote op rest => .quote (cell p start op) (reference p (after start op) rest)
  | .scope body rest => .scope (reference p start body) (reference p start rest)

mutual
  def staged (p : Provider) (start : Nat) (tree : Content) : Render :=
    assemble p start (parentPass p start tree) tree
  termination_by (sizeOf tree, 1)

  def assemble (p : Provider) (preceding : Nat) (entries : List Entry) (tree : Content) : Render :=
    match tree with
    | .empty => .empty
    | .quote _ rest =>
      match entries with
      | [] => .empty
      | entry :: tail => .quote entry.value (assemble p entry.afterDepth tail rest)
    | .scope body rest => .scope (staged p preceding body) (assemble p preceding entries rest)
  termination_by (sizeOf tree, 0)
end

theorem staged_and_assemble (p : Provider) (tree : Content) :
    (∀ start, staged p start tree = reference p start tree) ∧
    (∀ start, assemble p start (parentPass p start tree) tree = reference p start tree) := by
  induction tree with
  | empty => exact ⟨fun _ => by rw [staged, assemble, reference], fun _ => by rw [assemble, reference]⟩
  | quote op rest ih =>
    have h : ∀ start, assemble p start (parentPass p start (.quote op rest)) (.quote op rest) =
        reference p start (.quote op rest) := by
      intro start
      simp only [parentPass, assemble, reference]
      rw [ih.2]
    exact ⟨fun start => by rw [staged]; exact h start, h⟩
  | scope body rest bodyIH restIH =>
    have h : ∀ start, assemble p start (parentPass p start (.scope body rest)) (.scope body rest) =
        reference p start (.scope body rest) := by
      intro start
      simp only [parentPass, assemble, reference]
      rw [bodyIH.1, restIH.2]
    exact ⟨fun start => by rw [staged]; exact h start, h⟩

theorem staged_eq_reference (p : Provider) (start : Nat) (tree : Content) :
    staged p start tree = reference p start tree := (staged_and_assemble p tree).1 start

def parentOps : Content → List Op
  | .empty => []
  | .quote op rest => op :: parentOps rest
  | .scope _ rest => parentOps rest

def table (p : Provider) (start : Nat) : List Op → List Entry
  | [] => []
  | op :: rest => ⟨cell p start op, after start op⟩ :: table p (after start op) rest

theorem parentPass_eq_table (p : Provider) (tree : Content) (start : Nat) :
    parentPass p start tree = table p start (parentOps tree) := by
  induction tree generalizing start with
  | empty => rfl
  | quote op rest ih => simp [parentPass, parentOps, table, ih]
  | scope body rest bodyIH restIH => exact restIH start

def precedingLookup : Nat → List Entry → Nat → Nat
  | ancestor, _, 0 => ancestor
  | ancestor, [], _ + 1 => ancestor
  | _, entry :: rest, count + 1 => precedingLookup entry.afterDepth rest count

theorem lookup_table (p : Provider) (ops : List Op) (start count : Nat) :
    precedingLookup start (table p start ops) count = finish start (ops.take count) := by
  induction ops generalizing start count with
  | nil => cases count <;> rfl
  | cons op rest ih =>
    cases count with
    | zero => rfl
    | succ n => simpa [precedingLookup, table, finish] using ih (after start op) n

theorem lookup_parent_prefix (p : Provider) (tree : Content) (start count : Nat) :
    precedingLookup start (parentPass p start tree) count =
      finish start ((parentOps tree).take count) := by
  rw [parentPass_eq_table, lookup_table]

def scopePositions : Content → List Nat
  | .empty => []
  | .quote _ rest => (scopePositions rest).map Nat.succ
  | .scope _ rest => 0 :: scopePositions rest

def scanChildStarts (start : Nat) : Content → List Nat
  | .empty => []
  | .quote op rest => scanChildStarts (after start op) rest
  | .scope _ rest => start :: scanChildStarts start rest

theorem positions_bounded (tree : Content) :
    ∀ k ∈ scopePositions tree, k ≤ (parentOps tree).length := by
  induction tree with
  | empty => simp [scopePositions]
  | quote op rest ih =>
    intro k hk
    obtain ⟨n, hn, rfl⟩ := List.mem_map.mp hk
    exact Nat.succ_le_succ (ih n hn)
  | scope body rest bodyIH restIH =>
    intro k hk
    rcases List.mem_cons.mp hk with rfl | h
    · exact Nat.zero_le _
    · exact restIH k h

theorem lookup_child_starts (p : Provider) (tree : Content) (start : Nat) :
    (scopePositions tree).map (precedingLookup start (parentPass p start tree)) =
      scanChildStarts start tree := by
  induction tree generalizing start with
  | empty => rfl
  | quote op rest ih =>
    simpa [scopePositions, parentPass, scanChildStarts, List.map_map, Function.comp_def, precedingLookup] using ih (after start op)
  | scope body rest bodyIH restIH =>
    simp [scopePositions, parentPass, scanChildStarts, precedingLookup, restIH]

def embed : List Op → Content
  | [] => .empty
  | op :: rest => .quote op (embed rest)

def renderCells : List Cell → Render
  | [] => .empty
  | value :: rest => .quote value (renderCells rest)

theorem childless_fastpath (p : Provider) (ops : List Op) (start : Nat) :
    staged p start (embed ops) = renderCells (scan p start ops) := by
  rw [staged_eq_reference]
  induction ops generalizing start with
  | nil => rfl
  | cons op rest ih => simp [embed, reference, scan, renderCells, ih]

end QuoteScopes
