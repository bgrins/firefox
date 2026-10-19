import Tab
import Lean
namespace Tab
structure Input where
  id : Nat
  mode : Nat
  tokens : List Token
  begin : Nat
  ending : Nat
  width : Int
  minimum : Int
  initial : Int
  split : Int
  deriving Repr

def slice (tokens : List Token) (a b : Nat) := (tokens.drop a).take (b-a)
def boolInt (b : Bool) : Int := if b then 1 else 0

def flowInvocation (mode : Mode) (policy : Policy) (c : Input) (a b : Nat) (s : NativeState) :=
  let fresh := { s with pending := 0, pendingCount := 0, cursor := a, metricKnown := false, provider := s.provider ++ [(1,a,(b : Int)),(5,0,0),(6,a,(b : Int))] }
  nativeRun mode policy (slice c.tokens a b) fresh

def flowBridge (fixed : Bool) (c : Input) :=
  let mode := if c.mode == 1 then Mode.minimum else Mode.preferred
  let policy := if fixed then candidate c.width c.minimum else legacy c.width c.minimum
  let start : NativeState := {current := c.initial}
  if c.split < 0 then flowInvocation mode policy c c.begin c.ending start
  else
    let first := flowInvocation mode policy c c.begin c.split.toNat start
    flowInvocation mode policy c c.split.toNat c.ending first

def normalCalculate (policy : Policy) (c : Input) (ending : Nat) (s : NormalState) :=
  let next := normalLoop true policy (slice c.tokens s.cursor ending) s
  if next.cache then next else { next with provider := next.provider ++ [(7,0,0)], analyzed := max next.analyzed (ending-next.origin) }

def normalBridge (fixed : Bool) (c : Input) :=
  let policy := if fixed then candidate c.width c.minimum else legacy c.width c.minimum
  let initial : NormalState := { measured := c.initial, offset := c.initial, origin := c.begin, cursor := c.begin }
  let enabled := c.width > 0 && c.tokens.contains .tab
  let s := if c.mode == 6 then initial
    else if c.mode == 7 || c.mode == 8 then normalCalculate policy c c.ending initial
    else if enabled then
      let first := if c.mode == 4 then normalCalculate policy c (c.begin + (c.ending-c.begin)/2) initial else initial
      let full := normalCalculate policy c c.ending first
      if c.mode == 4 then normalCalculate policy c c.ending full else full
    else initial
  if c.mode == 5 then
    { s with provider := s.provider ++ [(5,0,0)] ++ (if enabled then [(3,0,0)] else []) }
  else s

def eventsJSON (events : List Event) : String :=
  "[" ++ String.intercalate "," (events.map fun (c,a,b) => s!"[{c},{a},{b}]") ++ "]"
def intsJSON (xs : List Int) : String :=
  "[" ++ String.intercalate "," (xs.map toString) ++ "]"
def glyphSum : List Token → Int
  | [] => 0
  | .glyph n :: ts => n + glyphSum ts
  | .tab :: ts => glyphSum ts

theorem glyphSum_cons (t : Token) (ts : List Token) :
    glyphSum (t :: ts) = (match t with | .glyph n => (n : Int) | .tab => 0) + glyphSum ts := by
  cases t <;> simp [glyphSum]

theorem identity_sum (ts : List Token) (x : Int) : scalar id ts x = x + glyphSum ts := by
  induction ts generalizing x with
  | nil => simp [scalar,glyphSum]
  | cons t ts ih => cases t <;> simp [scalar,ih,glyphSum_cons,Int.add_assoc]

theorem normal_consumer_zero (c : Input) :
    c.initial + glyphSum (slice c.tokens c.begin c.ending) =
      (specRun id (slice c.tokens c.begin c.ending) ⟨c.initial,c.begin,[]⟩).advance := by
  rw [spec_scalar,identity_sum]

def encode (fixed : Bool) (c : Input) : String :=
  let jsonEvents := fun events => Lean.toJson (events.map fun (c,a,b) => [(c : Int),(a : Int),b])
  if c.mode == 1 || c.mode == 2 then
    let s := flowBridge fixed c
    let state := [s.current,0,boolInt s.atStart,boolInt s.empty,0]
    (Lean.Json.mkObj [("id",Lean.toJson c.id),("mode",Lean.toJson c.mode),
      ("state",Lean.toJson state),("events",jsonEvents s.provider)]).compress
  else
    let s := normalBridge fixed c
    let value := c.initial + glyphSum (slice c.tokens c.begin c.ending) + (s.records.map Prod.snd).sum
    let analyzed := s.analyzed
    let present := c.mode != 6 && c.mode != 7 && c.mode != 8 && s.cache
    let state := [s.offset,analyzed,if s.metricKnown then c.minimum else -1,boolInt present]
    let cache := if s.cache then
      [Lean.toJson (s.cursor-c.begin),Lean.toJson (0 : Int)] ++
        s.records.map (fun (i,w) => Lean.toJson [(i : Int),w]) else []
    let spacing := (List.range (c.ending-c.begin)).map fun i =>
      let width := ((s.records.filter fun r => r.1 == i).map Prod.snd).sum
      [0,width]
    (Lean.Json.mkObj [("id",Lean.toJson c.id),("mode",Lean.toJson c.mode),
      ("value",Lean.toJson value),("state",Lean.toJson state),("spacing",Lean.toJson spacing),
      ("cache",Lean.Json.arr cache.toArray),("events",jsonEvents s.provider)]).compress
def coordFits (x : Int) : Prop := -1073741823 ≤ x ∧ x ≤ 1073741823

def windowValid (c : Input) : Prop :=
  c.begin ≤ c.ending ∧ c.ending ≤ c.tokens.length ∧
  c.tokens.length < 2147483647 ∧
  (c.split < 0 ∨ (c.begin : Int) ≤ c.split ∧ c.split ≤ c.ending)

structure ProviderWindow where
  sourceLength : Nat
  glyphLength : Nat
  tabAt : Nat → Bool
  glyphAt : Nat → Nat
  originalToSkipped : Nat → Nat
  before : Nat → Int
  after : Nat → Int
  measure : Nat → Nat → Int
  width : Int
  minimum : Int

def providerAgrees (c : Input) (p : ProviderWindow) : Prop :=
  p.sourceLength = c.tokens.length ∧
  p.sourceLength < p.glyphLength ∧
  p.width = c.width ∧ p.minimum = c.minimum ∧
  (∀ i, i < c.tokens.length →
    p.originalToSkipped i = i ∧ p.before i = 0 ∧ p.after i = 0 ∧
    match c.tokens[i]? with
    | some (.glyph n) => p.tabAt i = false ∧ p.glyphAt i = n
    | some .tab => p.tabAt i = true ∧ p.glyphAt i = 0
    | none => False) ∧
  (∀ a b, c.begin ≤ a → a ≤ b → b ≤ c.ending →
    p.measure a b = glyphSum (slice c.tokens a b))

def admissiblePrefixes (mode : Mode) (policy : Policy)
    (ts : List Token) (s : NativeState) : Prop :=
  ∀ front rest, ts = front ++ rest →
    let state := nativeLoop mode policy front s
    coordFits state.current ∧ coordFits state.pending ∧
    coordFits (state.current + state.pending) ∧
    state.cursor < 2147483647 ∧ state.pendingCount < 2147483647

theorem admissible_final (mode : Mode) (policy : Policy)
    (ts : List Token) (s : NativeState)
    (h : admissiblePrefixes mode policy ts s) :
    coordFits (nativeRun mode policy ts s).current := by
  have last := h ts [] (by simp)
  exact last.2.2.1

theorem zero_window_applicability (mode : Mode) (c : Input) (p : ProviderWindow)
    (s : NativeState) (n : NormalState)
    (window : windowValid c) (providers : providerAgrees c p)
    (width : c.width = 0) (start : view s = ⟨c.initial,c.begin,[]⟩)
    (normal : normalView n = view s)
    (numeric : admissiblePrefixes mode (candidate c.width c.minimum)
      (slice c.tokens c.begin c.ending) s) :
    coordFits (nativeRun mode (candidate c.width c.minimum)
      (slice c.tokens c.begin c.ending) s).current ∧
    (view (nativeRun mode (candidate c.width c.minimum)
      (slice c.tokens c.begin c.ending) s)).advance =
      c.initial + p.measure c.begin c.ending ∧
    view (nativeRun mode (candidate c.width c.minimum)
      (slice c.tokens c.begin c.ending) s) =
      normalView (normalLoop false (candidate c.width c.minimum)
        (slice c.tokens c.begin c.ending) n) := by
  refine ⟨admissible_final mode _ _ s numeric, ?_, ?_⟩
  · have measured := providers.2.2.2.2.2 c.begin c.ending
      (Nat.le_refl _) window.1 (Nat.le_refl _)
    have policy : candidate c.width c.minimum = id := by
      rw [width]
      exact funext (zero_identity c.minimum)
    rw [run_agreement,policy,spec_scalar,identity_sum,start,measured]
  · rw [width]
    exact zero_caller_agreement mode c.minimum _ s n normal.symm

end Tab
