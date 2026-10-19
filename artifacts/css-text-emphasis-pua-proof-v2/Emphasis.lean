import Std

namespace Emphasis

inductive Category where
  | Cn | Lu | Ll | Lt | Lm | Lo | Mn | Me | Mc | Nd | Nl | No
  | Zs | Zl | Zp | Cc | Cf | Co | Cs | Pd | Ps | Pe | Pc | Po
  | Sm | Sc | Sk | So | Pi | Pf
  deriving DecidableEq, Repr

inductive Coarse where
  | other | letter | mark | number | separator | punctuation | symbol
  deriving DecidableEq, Repr

def coarse : Category → Coarse
  | .Cn | .Cc | .Cf | .Co | .Cs => .other
  | .Lu | .Ll | .Lt | .Lm | .Lo => .letter
  | .Mn | .Me | .Mc => .mark
  | .Nd | .Nl | .No => .number
  | .Zs | .Zl | .Zp => .separator
  | .Pd | .Ps | .Pe | .Pc | .Po | .Pi | .Pf => .punctuation
  | .Sm | .Sc | .Sk | .So => .symbol

def specified (c : Category) (exception : Bool) : Bool :=
  match c with
  | .Zs | .Zl | .Zp | .Cc | .Cf | .Cn | .Cs => false
  | .Pd | .Ps | .Pe | .Pc | .Po | .Pi | .Pf => exception
  | _ => true

def candidate (c : Category) (exception : Bool) : Bool :=
  match coarse c with
  | .separator => false
  | .other => c == .Co
  | .punctuation => exception
  | _ => true

def original (c : Category) (exception : Bool) : Bool :=
  match coarse c with
  | .separator | .other => false
  | .punctuation => exception
  | _ => true

theorem classifier_refinement (c : Category) (e : Bool) :
    candidate c e = specified c e := by cases c <;> rfl

theorem private_use_accepted (e : Bool) : candidate .Co e = true := rfl

theorem other_categories_unchanged (c : Category) (e : Bool) (h : c ≠ .Co) :
    candidate c e = original c e := by cases c <;> simp_all [candidate, original, coarse]

def privateUseRange (cp : Nat) : Bool :=
  (0xE000 ≤ cp && cp ≤ 0xF8FF) ||
  (0xF0000 ≤ cp && cp ≤ 0xFFFFD) ||
  (0x100000 ≤ cp && cp ≤ 0x10FFFD)

theorem private_use_is_scalar (cp : Nat) (h : privateUseRange cp = true) :
    cp < 0x110000 ∧ ¬ (0xD800 ≤ cp ∧ cp ≤ 0xDFFF) := by
  simp [privateUseRange] at h
  omega

abbrev Unit := Fin 65536

def pair (a b : Unit) : Bool :=
  (0xD800 ≤ a.val && a.val ≤ 0xDBFF) && (0xDC00 ≤ b.val && b.val ≤ 0xDFFF)

def nativePairValue (a b : Unit) : Nat :=
  (a.val % 1024) * 1024 + b.val % 1024 + 65536

def specPairValue (a b : Unit) : Nat :=
  65536 + (a.val - 0xD800) * 1024 + (b.val - 0xDC00)

theorem pair_value_refinement (a b : Unit) (h : pair a b = true) :
    nativePairValue a b = specPairValue a b := by
  simp [pair] at h
  unfold nativePairValue specPairValue
  omega

theorem pair_value_scalar (a b : Unit) (_h : pair a b = true) :
    65536 ≤ nativePairValue a b ∧ nativePairValue a b < 0x110000 := by
  unfold nativePairValue
  omega

structure Token where
  units : List Unit
  cp : Nat
  deriving DecidableEq, Repr

def decode : List Unit → List Token
  | [] => []
  | [a] => [⟨[a], a.val⟩]
  | a :: b :: rest =>
    if pair a b then ⟨[a,b], nativePairValue a b⟩ :: decode rest
    else ⟨[a],a.val⟩ :: decode (b::rest)
termination_by xs => xs.length

inductive Decodes : List Unit → List Token → Prop where
  | nil : Decodes [] []
  | last (a : Unit) : Decodes [a] [⟨[a],a.val⟩]
  | single (a b : Unit) (rest : List Unit) (ts : List Token)
      (h : pair a b = false) (tail : Decodes (b::rest) ts) :
      Decodes (a::b::rest) (⟨[a],a.val⟩::ts)
  | double (a b : Unit) (rest : List Unit) (ts : List Token)
      (h : pair a b = true) (tail : Decodes rest ts) :
      Decodes (a::b::rest) (⟨[a,b],specPairValue a b⟩::ts)

theorem decode_refines (xs : List Unit) : Decodes xs (decode xs) := by
  match xs with
  | [] => simpa [decode] using Decodes.nil
  | [a] => simpa [decode] using Decodes.last a
  | a::b::rest =>
    simp only [decode]
    split
    next h =>
      rw [pair_value_refinement a b h]
      exact .double a b rest (decode rest) h (decode_refines rest)
    next h =>
      exact .single a b rest (decode (b::rest)) (Bool.eq_false_iff.mpr h) (decode_refines (b::rest))
termination_by xs.length

theorem decode_covers (xs : List Unit) : (decode xs).flatMap Token.units = xs := by
  match xs with
  | [] => simp [decode]
  | [a] => simp [decode]
  | a::b::rest =>
    have h1 := decode_covers rest
    have h2 := decode_covers (b::rest)
    simp only [decode]
    split <;> simp [h1, h2]
termination_by xs.length

theorem token_progress (xs : List Unit) (t : Token) (h : t ∈ decode xs) :
    t.units.length = 1 ∨ t.units.length = 2 := by
  match xs with
  | [] => simp [decode] at h
  | [a] => simp [decode] at h; subst t; exact Or.inl rfl
  | a::b::rest =>
    simp only [decode] at h
    split at h
    next hp =>
      rcases List.mem_cons.mp h with h | h
      · subst t; exact Or.inr rfl
      · exact token_progress rest t h
    next hp =>
      rcases List.mem_cons.mp h with h | h
      · subst t; exact Or.inl rfl
      · exact token_progress (b::rest) t h
termination_by xs.length

def loopFlags (eligible : Nat → Bool) : List Unit → List Bool
  | [] => []
  | [a] => [eligible a.val]
  | a::b::rest =>
    if pair a b then eligible (nativePairValue a b) :: eligible (nativePairValue a b) :: loopFlags eligible rest
    else eligible a.val :: loopFlags eligible (b::rest)
termination_by xs => xs.length

def directFlags (eligible : Nat → Bool) (xs : List Unit) : List Bool :=
  (decode xs).flatMap fun t => t.units.map fun _ => eligible t.cp

theorem flags_refinement (eligible : Nat → Bool) (xs : List Unit) :
    loopFlags eligible xs = directFlags eligible xs := by
  match xs with
  | [] => simp [loopFlags, directFlags, decode]
  | [a] => simp [loopFlags, directFlags, decode]
  | a::b::rest =>
    have h1 := flags_refinement eligible rest
    have h2 := flags_refinement eligible (b::rest)
    unfold directFlags at h1 h2 ⊢
    simp only [loopFlags, decode]
    split <;> simp [h1, h2]
termination_by xs.length

theorem flags_length (eligible : Nat → Bool) (xs : List Unit) :
    (loopFlags eligible xs).length = xs.length := by
  match xs with
  | [] => simp [loopFlags]
  | [a] => simp [loopFlags]
  | a::b::rest =>
    have h1 := flags_length eligible rest
    have h2 := flags_length eligible (b::rest)
    simp only [loopFlags]
    split <;> simp [h1, h2]
termination_by xs.length

theorem decoded_prefix_bounds (xs : List Unit) (before after : List Token)
    (t : Token) (h : decode xs = before ++ t :: after) :
    (before.flatMap Token.units).length + t.units.length ≤ xs.length := by
  have hc := decode_covers xs
  rw [h] at hc
  have hl := congrArg List.length hc
  simp only [List.flatMap_append, List.flatMap_cons, List.length_append] at hl
  omega

theorem latin1_flags (eligible : Nat → Bool) (xs : List (Fin 256)) :
    (xs.map fun x => eligible x.val).length = xs.length := by simp

structure Detail where
  id : Nat
  advance : Int
  x : Rat
  y : Rat
  deriving DecidableEq, Repr

structure Common where
  breakBefore : Fin 4
  space : Bool
  deriving DecidableEq, Repr

structure ComplexFlags where
  clusterStart : Bool
  ligatureStart : Bool
  missing : Bool
  tab : Bool
  newline : Bool
  formatting : Bool
  letterSpacing : Bool
  noEmphasis : Bool
  deriving DecidableEq, Repr

inductive Glyph where
  | simple (common : Common) (id : Fin 65536) (advance : Fin 4096)
  | complex (common : Common) (flags : ComplexFlags) (details : List Detail)
  deriving DecidableEq, Repr

def simpleFlags : ComplexFlags := ⟨true,true,false,false,false,false,false,false⟩

def suppress : Glyph → Glyph
  | .simple c id advance => .complex c { simpleFlags with noEmphasis := true }
      [⟨id.val,advance.val,0,0⟩]
  | .complex c flags ds => .complex c { flags with noEmphasis := true } ds

def contents : Glyph → Common × ComplexFlags × List Detail
  | .simple c id advance => (c,simpleFlags,[⟨id.val,advance.val,0,0⟩])
  | .complex c flags ds => (c,flags,ds)

def unaffected (g : Glyph) : Common × ComplexFlags × List Detail :=
  let (c,f,ds) := contents g
  (c,{ f with noEmphasis := false },ds)

def charMay (g : Glyph) : Bool :=
  let (c,f,_) := contents g
  !c.space && !f.noEmphasis

theorem suppression_preserves_contents (g : Glyph) :
    unaffected (suppress g) = unaffected g := by cases g <;> rfl

theorem suppression_excludes (g : Glyph) : charMay (suppress g) = false := by
  cases g <;> simp [charMay, contents, suppress]

theorem suppression_idempotent (g : Glyph) : suppress (suppress g) = suppress g := by
  cases g <;> rfl

def applyFlag (g : Glyph) (eligible : Bool) : Glyph :=
  if eligible then g else suppress g

theorem apply_preserves_contents (g : Glyph) (eligible : Bool) :
    unaffected (applyFlag g eligible) = unaffected g := by
  cases eligible <;> simp [applyFlag, suppression_preserves_contents]

theorem effective_eligibility (g : Glyph) (eligible : Bool) :
    charMay (applyFlag g eligible) = (charMay g && eligible) := by
  cases eligible <;> simp [applyFlag, suppression_excludes]

def applyFlags (gs : List Glyph) (flags : List Bool) : List Glyph :=
  List.zipWith applyFlag gs flags

theorem apply_buffer_preserves (gs : List Glyph) (flags : List Bool)
    (h : gs.length = flags.length) :
    (applyFlags gs flags).map unaffected = gs.map unaffected := by
  induction gs generalizing flags with
  | nil => simp [applyFlags]
  | cons g gs ih =>
    cases flags with
    | nil => simp at h
    | cons f fs =>
      simp only [List.length_cons, Nat.add_right_cancel_iff] at h
      change unaffected (applyFlag g f) :: (applyFlags gs fs).map unaffected = unaffected g :: gs.map unaffected
      rw [apply_preserves_contents, ih fs h]

theorem apply_buffer_eligibility (gs : List Glyph) (flags : List Bool) :
    (applyFlags gs flags).map charMay = List.zipWith (fun g f => charMay g && f) gs flags := by
  induction gs generalizing flags with
  | nil => simp [applyFlags]
  | cons g gs ih =>
    cases flags <;> simp [applyFlags, effective_eligibility]

theorem complete_utf16_storage (eligible : Nat → Bool) (xs : List Unit)
    (gs : List Glyph) (h : gs.length = xs.length) :
    (applyFlags gs (loopFlags eligible xs)).map unaffected = gs.map unaffected ∧
    (applyFlags gs (loopFlags eligible xs)).map charMay =
      List.zipWith (fun g f => charMay g && f) gs (directFlags eligible xs) := by
  constructor
  · exact apply_buffer_preserves gs _ (by rw [flags_length]; exact h)
  · rw [apply_buffer_eligibility, flags_refinement]

def nativeAny : List Bool → Bool → Bool
  | [], state => state
  | b::rest, state => nativeAny rest (state || b)

theorem native_any_refinement (xs : List Bool) (state : Bool) :
    nativeAny xs state = (state || xs.any id) := by
  induction xs generalizing state with
  | nil => simp [nativeAny]
  | cons a xs ih =>
    rw [nativeAny, ih]
    cases state <;> cases a <;> simp

structure Cell where
  eligible : Bool
  boundary : Bool
  deriving DecidableEq, Repr

def encodedCluster : List Bool → List Cell
  | [] => []
  | [b] => [⟨b,true⟩]
  | b::c::rest => ⟨b,false⟩ :: encodedCluster (c::rest)

def streamDraw : List Cell → Bool → Nat → List Nat
  | [], _, _ => []
  | c::rest, pending, index =>
    let next := pending || c.eligible
    if c.boundary then
      (if next then [index] else []) ++ streamDraw rest false (index+1)
    else streamDraw rest next (index+1)

theorem stream_cluster (xs : List Bool) (tail : List Cell) (pending : Bool) (index : Nat)
    (hne : xs ≠ []) :
    streamDraw (encodedCluster xs ++ tail) pending index =
      (if pending || xs.any id then [index + xs.length - 1] else []) ++
      streamDraw tail false (index + xs.length) := by
  match xs with
  | [] => contradiction
  | [a] => simp [encodedCluster, streamDraw]
  | a::b::rest =>
    have ih := stream_cluster (b::rest) tail (pending || a) (index+1) (by simp)
    simp only [encodedCluster, List.cons_append, streamDraw, Bool.false_eq_true, ↓reduceIte]
    rw [ih]
    have ha : index + 1 + (b::rest).length - 1 = index + (a::b::rest).length - 1 := by simp; omega
    have hb : index + 1 + (b::rest).length = index + (a::b::rest).length := by simp; omega
    rw [ha,hb]
    congr 2
    simp only [List.any_cons, id_eq]
    cases pending <;> cases a <;> simp
termination_by xs.length

def directDraw (clusters : List (List Bool)) (index : Nat) : List Nat :=
  match clusters with
  | [] => []
  | c::rest => (if c.any id then [index+c.length-1] else []) ++ directDraw rest (index+c.length)

theorem arbitrary_cluster_draws (clusters : List (List Bool)) (index : Nat)
    (valid : ∀ c ∈ clusters, c ≠ []) :
    streamDraw (clusters.flatMap encodedCluster) false index = directDraw clusters index := by
  induction clusters generalizing index with
  | nil => simp [streamDraw, directDraw]
  | cons c rest ih =>
    simp only [List.flatMap_cons, directDraw]
    rw [stream_cluster c _ false index (valid c (by simp))]
    simp only [Bool.false_or]
    rw [ih _ (by intro x hx; exact valid x (by simp [hx]))]

end Emphasis
