import DeclarationSelection
import ColorSelection

namespace SelectionInteraction

open SelectedDeclaration SelectedColor

def lookup (name : String) : Option DemandFallback.Expr :=
  if name = "--v" then some (.literal ["light"]) else none

def winnerReads : List String :=
  ((DemandFallback.eval lookup 5 [] [] (.expression (.reference "--v"))).getD
    ⟨none, [], []⟩).reads

def evaluate (_ : Unit) (_ : Nat) : Evaluation Unit Token String :=
  ⟨.terminal (some .light), winnerReads⟩

def selectedReads (decls : List Nat) : List String :=
  (scan (fun _ _ => true) evaluate () decls).reads

def cycleFor (reads : List String) (reverse : Bool) : Bool :=
  cycleOracle (SelectedColor.edge (reads.contains "--v") reverse)

theorem winning_reference_is_retained (tail : List Nat) :
    selectedReads (0 :: tail) = ["--v"] := by
  unfold selectedReads
  rw [terminal_ignores_tail (fun _ _ => true) evaluate () 0 tail rfl
    (some Token.light) rfl]
  decide

theorem read_graph_requires_selected_reverse (reads : List String)
    (reached : reads.contains "--v" = true) (reverse : Bool)
    (clauses : List Clause) (token : Token) :
    cycleFor reads reverse = cycleFor reads (depends (select clauses token)) ↔
      reverse = depends (select clauses token) := by
  simp only [cycleFor, independent_cycle_oracle, reached, Bool.true_and]

theorem adding_genuine_read_exposes_broad_edge (tail : List Nat) :
    broadCycle [.ident, .color] false = false ∧
    cycleFor (selectedReads (0 :: tail)) (possibleColor [.ident, .color]) = true ∧
    cycleFor (selectedReads (0 :: tail)) (depends (select [.ident, .color] .light)) = false ∧
    cycleFor (selectedReads (0 :: tail)) (depends (select [.ident, .color] .dark)) = false := by
  rw [winning_reference_is_retained]
  decide

theorem refinement_preserves_forward_read (tail : List Nat) :
    selectedReads (0 :: tail) = ["--v"] ∧
    SelectedColor.edge ((selectedReads (0 :: tail)).contains "--v")
      (depends (select [.ident, .color] .light)) .scheme .custom = true := by
  rw [winning_reference_is_retained]
  decide

theorem dropping_winning_edge_loses_genuine_cycle :
    cycleFor winnerReads (depends (select [.color, .ident] .canvas)) = true ∧
    cycleFor [] (depends (select [.color, .ident] .canvas)) = false := by decide

end SelectionInteraction
