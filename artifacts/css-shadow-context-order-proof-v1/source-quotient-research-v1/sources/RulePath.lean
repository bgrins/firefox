import Base
import Priority
namespace ShadowOrder
set_option maxHeartbeats 800000

def dedupAdjacent [DecidableEq α] : List α → List α
 | [] => []
 | [a] => [a]
 | a::b::rest => if a = b then dedupAdjacent (b::rest)
   else a::dedupAdjacent (b::rest)

def runActions (step : σ → α → σ) : List α → σ → σ
 | [], state => state
 | a::rest, state => runActions step rest (step state a)

theorem duplicate_elision [DecidableEq α] (step : σ → α → σ)
 (idempotent : ∀ state a, step (step state a) a = step state a)
 (xs : List α) (state : σ) :
 runActions step (dedupAdjacent xs) state = runActions step xs state := by
 induction xs using dedupAdjacent.induct generalizing state with
 | case1 => rfl
 | case2 a => rfl
 | case3 a rest ih =>
   simp only [dedupAdjacent, ↓reduceIte]
   rw [ih]
   simp [runActions,idempotent]
 | case4 a b rest different ih =>
   simp only [dedupAdjacent,different,↓reduceIte,runActions]
   exact ih (step state a)

structure PathItem where
 source : Nat
 priority : Priority
 deriving DecidableEq, Repr

inductive RulePath where
 | root
 | child (item : PathItem) (parent : RulePath)
 deriving DecidableEq, Repr

def ancestors : RulePath → List PathItem
 | .root => []
 | .child item parent => item::ancestors parent

def insertPath : RulePath → List PathItem → RulePath
 | path, [] => path
 | path, item::rest => insertPath (.child item path) rest

theorem ancestor_insertion (items : List PathItem) (path : RulePath) :
 ancestors (insertPath path items) = items.reverse ++ ancestors path := by
 induction items generalizing path with
 | nil => simp [insertPath]
 | cons item rest ih =>
   simp [insertPath,ih,ancestors,List.reverse_cons,List.append_assoc]

structure NodeObservation where
 priority : Priority
 declarations : List Declaration
 deriving DecidableEq, Repr

def filteredDeclarations (keep : Priority → Declaration → Bool) (node : NodeObservation) :
 List (Declaration × Priority) :=
 (node.declarations.reverse.filter (keep node.priority)).map fun d => (d,node.priority)

def iteratorLoop (keep : Priority → Declaration → Bool) :
 List NodeObservation → List (Declaration × Priority)
 | [] => []
 | node::rest => scan node.priority node.declarations.reverse ++ iteratorLoop keep rest
where
 scan (priority : Priority) : List Declaration → List (Declaration × Priority)
 | [] => []
 | d::rest => if keep priority d then (d,priority)::scan priority rest else scan priority rest

theorem declaration_scan (keep : Priority → Declaration → Bool) (priority : Priority)
 (decls : List Declaration) :
 iteratorLoop.scan keep priority decls =
   (decls.filter (keep priority)).map (fun d => (d,priority)) := by
 induction decls with
 | nil => rfl
 | cons d rest ih =>
   simp only [iteratorLoop.scan,List.filter_cons]
   split <;> simp_all

theorem declaration_iterator (keep : Priority → Declaration → Bool) (nodes : List NodeObservation) :
 iteratorLoop keep nodes = nodes.flatMap (filteredDeclarations keep) := by
 induction nodes with
 | nil => rfl
 | cons node rest ih =>
   simp [iteratorLoop,filteredDeclarations,declaration_scan,ih]

#print axioms duplicate_elision
#print axioms ancestor_insertion
#print axioms declaration_iterator
end ShadowOrder
