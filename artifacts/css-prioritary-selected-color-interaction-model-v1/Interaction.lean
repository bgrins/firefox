import DeclarationSelection
import ColorSelection

namespace SelectionInteraction

open SelectedDeclaration SelectedColor

def lookup (token : Token) (name : String) : Option DemandFallback.Expr :=
  if name = "--v" then some (.literal [reprStr token]) else none

def winnerReads (token : Token) : List String :=
  ((DemandFallback.eval (lookup token) 5 [] [] (.expression (.reference "--v"))).getD
    ⟨none, [], []⟩).reads

def evaluate (token : Token) (_ : Unit) (_ : Nat) : Evaluation Unit Token String :=
  ⟨.terminal (some token), winnerReads token⟩

def selectedReads (token : Token) (decls : List Nat) : List String :=
  (scan (fun _ _ => true) (evaluate token) () decls).reads

def cycleFor (reads : List String) (reverse : Bool) : Bool :=
  cycleOracle (SelectedColor.edge (reads.contains "--v") reverse)

theorem winning_reference_is_retained (token : Token) (tail : List Nat) :
    selectedReads token (0 :: tail) = ["--v"] := by
  unfold selectedReads
  rw [terminal_ignores_tail (fun _ _ => true) (evaluate token) () 0 tail rfl
    (some token) rfl]
  cases token <;> decide

theorem read_graph_requires_selected_reverse (reads : List String)
    (reached : reads.contains "--v" = true) (reverse : Bool)
    (clauses : List Clause) (token : Token) :
    cycleFor reads reverse = cycleFor reads (depends (select clauses token)) ↔
      reverse = depends (select clauses token) := by
  simp only [cycleFor, independent_cycle_oracle, reached, Bool.true_and]

theorem adding_genuine_read_exposes_broad_edge (tail : List Nat) :
    broadCycle [.ident, .color] false = false ∧
    cycleFor (selectedReads .light (0 :: tail)) (possibleColor [.ident, .color]) = true ∧
    cycleFor (selectedReads .light (0 :: tail)) (depends (select [.ident, .color] .light)) = false ∧
    cycleFor (selectedReads .dark (0 :: tail)) (depends (select [.ident, .color] .dark)) = false := by
  simp only [winning_reference_is_retained]
  decide

theorem refinement_preserves_forward_read (tail : List Nat) :
    selectedReads .light (0 :: tail) = ["--v"] ∧
    SelectedColor.edge ((selectedReads .light (0 :: tail)).contains "--v")
      (depends (select [.ident, .color] .light)) .scheme .custom = true := by
  simp only [winning_reference_is_retained]
  decide

theorem dropping_winning_edge_loses_genuine_cycle :
    cycleFor (winnerReads .canvas) (depends (select [.color, .ident] .canvas)) = true ∧
    cycleFor [] (depends (select [.color, .ident] .canvas)) = false := by decide

end SelectionInteraction
