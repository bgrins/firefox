import Std
namespace Boundary
inductive Class where
  | whitespace | atKeywordOrHash | number | dimension | percentage | urlOrBadUrl
  | function | ident | cdc | dashMatch | substringMatch | openParen | delimHash
  | delimAt | delimDotOrPlus | delimMinus | delimQuestion | delimAssorted
  | delimEquals | delimBar | delimSlash | delimAsterisk | delimPercent | other
  deriving DecidableEq, Repr
inductive Block where
  | function | paren | square | curly
  deriving DecidableEq, Repr
def Block.openClass : Block → Class
  | .function => .function
  | .paren => .openParen
  | .square | .curly => .other
inductive Event where
  | token (cls : Class)
  | comment
  | block (kind : Block) (body : List Class)
  deriving DecidableEq, Repr
structure Summary where
  first : Option Class := none
  last : Option Class := none
  deriving DecidableEq, Repr

def flattenOne : Event → List Class
  | .token c => [c]
  | .comment => []
  | .block k body => k.openClass :: (body ++ [.other])
def flatten (es : List Event) : List Class := es.flatMap flattenOne

def reference (xs : List Class) : Summary := ⟨xs.head?, xs.getLast?⟩
def join (a b : Summary) : Summary := ⟨a.first.or b.first, b.last.or a.last⟩
def step (s : Summary) : Event → Summary
  | .comment => s
  | .token c => ⟨s.first.or (some c), some c⟩
  | .block k _ => ⟨s.first.or (some k.openClass), some .other⟩
def loop (s : Summary) : List Event → Summary
  | [] => s
  | e :: es => loop (step s e) es

theorem join_assoc (a b c : Summary) : join (join a b) c = join a (join b c) := by
  cases a with | mk af al =>
    cases b with | mk bf bl =>
      cases c with | mk cf cl =>
        cases af <;> cases bf <;> cases cf <;> cases al <;> cases bl <;> cases cl <;> rfl

theorem reference_append (xs ys : List Class) :
    reference (xs ++ ys) = join (reference xs) (reference ys) := by
  simp [reference, join, List.head?_append, List.getLast?_append]

theorem step_reference (s : Summary) (e : Event) :
    step s e = join s (reference (flattenOne e)) := by
  cases e with
  | token c => rfl
  | comment => simp [step, join, reference, flattenOne, Option.or_none]
  | block k body => simp [step, join, reference, flattenOne, List.getLast?_cons, List.getLast?_append]

theorem loop_reference (s : Summary) (es : List Event) :
    loop s es = join s (reference (flatten es)) := by
  induction es generalizing s with
  | nil => simp [loop, flatten, reference, join, Option.or_none]
  | cons e es ih =>
    rw [loop, ih, step_reference, join_assoc]
    simp [flatten, List.flatMap_cons, reference_append]

theorem complete_summary (es : List Event) :
    loop {} es = reference (flatten es) := by
  rw [loop_reference]
  simp [join]

theorem first_token (es : List Event) :
    (loop {} es).first = (flatten es).head? := by rw [complete_summary]; rfl

theorem last_token (es : List Event) :
    (loop {} es).last = (flatten es).getLast? := by rw [complete_summary]; rfl

theorem composition (xs ys : List Event) :
    loop {} (xs ++ ys) = join (loop {} xs) (loop {} ys) := by
  simp only [complete_summary, flatten, List.flatMap_append, reference_append]

theorem arbitrary_list_composition (parts : List (List Event)) :
    loop {} parts.flatten = parts.foldl (fun s es => join s (loop {} es)) {} := by
  have aux (s : Summary) (ps : List (List Event)) :
      join s (reference (flatten ps.flatten)) =
      ps.foldl (fun a es => join a (loop {} es)) s := by
    induction ps generalizing s with
    | nil => simp [flatten, reference, join, Option.or_none]
    | cons p ps ih =>
      simp only [List.flatten_cons, flatten, List.flatMap_append, reference_append,
        List.foldl_cons, complete_summary]
      rw [← join_assoc]
      simpa only [complete_summary, flatten] using ih (join s (reference (flatten p)))
  rw [loop_reference]
  exact aux {} parts

theorem serialized_pair (left separator right : List Event) :
    loop {} (left ++ separator ++ right) =
    join (join (loop {} left) (loop {} separator)) (loop {} right) := by
  rw [composition, composition]


theorem comments_omitted (s : Summary) (es : List Event) :
    loop s (.comment :: es) = loop s es := rfl

theorem comment_only (n : Nat) : loop {} (List.replicate n .comment) = {} := by
  induction n with
  | zero => rfl
  | succ n ih => simpa [List.replicate_succ, loop, step] using ih

theorem block_boundary (k : Block) (body : List Class) :
    loop {} [.block k body] = ⟨some k.openClass, some .other⟩ := rfl

theorem block_body_independent (k : Block) (a b : List Class) :
    loop {} [.block k a] = loop {} [.block k b] := rfl

theorem surrounding_whitespace (es : List Event) :
    loop {} (.token .whitespace :: es ++ [.token .whitespace]) =
    ⟨some .whitespace, some .whitespace⟩ := by
  rw [complete_summary]
  simp [flatten, flattenOne, reference, List.getLast?_cons, List.getLast?_append]

theorem later_sibling_wins (k : Block) (body : List Class) (c : Class) :
    (loop {} [.block k body, .token c]).last = some c := rfl

def oldLP : Summary := ⟨some .percentage, some .percentage⟩
theorem old_lp_dimension_wrong : oldLP ≠ loop {} [.token .dimension] := by decide

theorem old_lp_function_wrong : oldLP ≠ loop {} [.block .function [.dimension]] := by decide

theorem first_component_last_wrong :
    loop {} [.token .percentage] ≠
    loop {} [.token .percentage, .token .whitespace, .token .dimension] := by decide

theorem opener_as_last_wrong :
    (⟨some .function, some .function⟩ : Summary) ≠
    loop {} [.block .function [.dimension]] := by decide

theorem comment_as_slash_wrong :
    loop {} [.token .delimSlash, .token .dimension] ≠
    loop {} [.comment, .token .dimension] := by decide

theorem whitespace_dropping_wrong :
    loop {} [.token .whitespace, .token .dimension] ≠
    loop {} [.token .dimension] := by decide
end Boundary
