import CommentScan
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace CommentDirectives
open CommentScan

def nativeSpace (b : Byte) : Bool := b == 32 || b == 9 || b == 13 || b == 10
def referenceSpace (b : Byte) : Bool := ([9,10,12,13,32] : List Byte).contains b

theorem whitespace_classification : ∀ b : Byte, nativeSpace b = referenceSpace b := by decide

def consumeLiteral : List Byte → List Byte → Option (List Byte)
  | [], xs => some xs
  | _::_, [] => none
  | p::ps, b::bs => if p == b then consumeLiteral ps bs else none

theorem literal_prefix (key xs : List Byte) :
    consumeLiteral key xs = if key.isPrefixOf xs then some (xs.drop key.length) else none := by
  induction key generalizing xs with
  | nil => simp [consumeLiteral]
  | cons p ps ih =>
    cases xs with
    | nil => simp [consumeLiteral]
    | cons b bs =>
      by_cases h : p = b
      · subst b; simp [consumeLiteral,ih]
      · simp [consumeLiteral,h]

def nativeDirective (key body : List Byte) : Option (List Byte) :=
  if ([35,32] ++ key).isPrefixOf body || ([64,32] ++ key).isPrefixOf body then
    some ((body.drop (key.length+2)).takeWhile (fun b => !nativeSpace b))
  else none

def referenceDirective (key body : List Byte) : Option (List Byte) :=
  match body with
  | flag::space::tail =>
    if (flag == 35 || flag == 64) && space == 32 then
      (consumeLiteral key tail).map (fun rest => rest.takeWhile (fun b => !referenceSpace b))
    else none
  | _ => none

theorem directive_reference (key body : List Byte) :
    nativeDirective key body = referenceDirective key body := by
  cases body with
  | nil => simp [nativeDirective,referenceDirective]
  | cons flag rest =>
    cases rest with
    | nil => simp [nativeDirective,referenceDirective]
    | cons space tail =>
      simp only [nativeDirective,referenceDirective,literal_prefix]
      have e35 : ((35 : Byte) = flag) ↔ flag = 35 := eq_comm
      have e64 : ((64 : Byte) = flag) ↔ flag = 64 := eq_comm
      have e32 : ((32 : Byte) = space) ↔ space = 32 := eq_comm
      by_cases h35 : flag = 35 <;> by_cases h64 : flag = 64 <;> by_cases hs : space = 32 <;>
        simp_all [List.isPrefixOf,whitespace_classification,e35,e64,e32]

def ascii (s : String) : List Byte := s.toList.map (fun c => ⟨c.toNat % 256, Nat.mod_lt _ (by decide)⟩)
def nativeMapKey : List Byte := ascii "sourceMappingURL="
def nativeSourceKey : List Byte := ascii "sourceURL="
def referenceMapKey : List Byte := [115,111,117,114,99,101,77,97,112,112,105,110,103,85,82,76,61]
def referenceSourceKey : List Byte := [115,111,117,114,99,101,85,82,76,61]

theorem map_key : nativeMapKey = referenceMapKey := by decide
theorem source_key : nativeSourceKey = referenceSourceKey := by decide

structure URLs where
  sourceMap : Option (List Byte)
  source : Option (List Byte)
  deriving DecidableEq, Repr

def nativeUpdate (body : List Byte) (old : URLs) : URLs :=
  let m := nativeDirective nativeMapKey body
  let u := nativeDirective nativeSourceKey body
  ⟨m.or old.sourceMap,u.or old.source⟩

def referenceUpdate (body : List Byte) (old : URLs) : URLs :=
  ⟨(referenceDirective referenceMapKey body).or old.sourceMap,
   (referenceDirective referenceSourceKey body).or old.source⟩

theorem update_reference (body : List Byte) (old : URLs) :
    nativeUpdate body old = referenceUpdate body old := by
  simp [nativeUpdate,referenceUpdate,directive_reference,map_key,source_key]

theorem preserves_map (body : List Byte) (old : URLs)
    (h : referenceDirective referenceMapKey body = none) :
    (nativeUpdate body old).sourceMap = old.sourceMap := by
  simp [update_reference,referenceUpdate,h]

theorem preserves_source (body : List Byte) (old : URLs)
    (h : referenceDirective referenceSourceKey body = none) :
    (nativeUpdate body old).source = old.source := by
  simp [update_reference,referenceUpdate,h]

theorem history_reference (bodies : List (List Byte)) (old : URLs) :
    bodies.foldl (fun state body => nativeUpdate body state) old =
      bodies.foldl (fun state body => referenceUpdate body state) old := by
  simp [update_reference]

theorem empty_url_overwrites (old : URLs) :
    (nativeUpdate (ascii "# sourceURL=") old).source = some [] := by
  simp [nativeUpdate,nativeDirective,nativeSourceKey,ascii]
end CommentDirectives
