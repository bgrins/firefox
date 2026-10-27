import Std

namespace KeyframeAttributePreparation

structure Key where
  namespaceURI : Option String
  localName : String
  deriving DecidableEq, Repr

structure Value (α : Type) where
  payload : α
  tainted : Bool
  deriving DecidableEq, Repr

variable {Context Raw Prepared Output : Type}
abbrev Provider (Raw : Type) := Key → Option Raw
abbrev Cache (Prepared : Type) := Key → Option Prepared

def prepare (provider : Provider Raw) (resolve : Context → Key → Raw → Option Prepared)
    (context : Context) : List Key → Cache Prepared
  | [] => fun _ => none
  | key :: rest => fun query =>
      if query = key then (provider key).bind (resolve context key)
      else prepare provider resolve context rest query

theorem prepare_lookup (provider : Provider Raw)
    (resolve : Context → Key → Raw → Option Prepared) (context : Context)
    (keys : List Key) (key : Key) :
    prepare provider resolve context keys key =
      if key ∈ keys then (provider key).bind (resolve context key) else none := by
  induction keys with
  | nil => simp [prepare]
  | cons first rest ih =>
      by_cases h : key = first
      · subst first; simp [prepare]
      · simp [prepare, h, ih]

def evaluate (provider : Provider Raw) (cache : Cache Prepared)
    (parse : Prepared → Option Output) (key : Key) (fallback : Value Output) : Value Output :=
  match provider key with
  | none => fallback
  | some _ => match (cache key).bind parse with
      | none => fallback
      | some value => ⟨value, true⟩

def direct (provider : Provider Raw) (resolve : Context → Key → Raw → Option Prepared)
    (parse : Prepared → Option Output) (context : Context) (key : Key)
    (fallback : Value Output) : Value Output :=
  match provider key with
  | none => fallback
  | some raw => match (resolve context key raw).bind parse with
      | none => fallback
      | some value => ⟨value, true⟩

theorem prepared_evaluation (provider : Provider Raw)
    (resolve : Context → Key → Raw → Option Prepared) (parse : Prepared → Option Output)
    (context : Context) (keys : List Key) (key : Key) (fallback : Value Output)
    (prepared : key ∈ keys) :
    evaluate provider (prepare provider resolve context keys) parse key fallback =
      direct provider resolve parse context key fallback := by
  unfold evaluate direct
  rw [prepare_lookup, ite_eq_left prepared]
  cases provider key <;> rfl

structure Request (Prepared Output : Type) where
  key : Key
  parse : Prepared → Option Output
  fallback : Value Output

structure Frame (Context Raw Prepared Output : Type) where
  provider : Provider Raw
  context : Context
  preparation : List Key
  requests : List (Request Prepared Output)

def Frame.covered (frame : Frame Context Raw Prepared Output) : Prop :=
  ∀ request ∈ frame.requests, request.key ∈ frame.preparation

def runFrame (resolve : Context → Key → Raw → Option Prepared)
    (frame : Frame Context Raw Prepared Output) : List (Value Output) :=
  let cache := prepare frame.provider resolve frame.context frame.preparation
  frame.requests.map fun request =>
    evaluate frame.provider cache request.parse request.key request.fallback

def directFrame (resolve : Context → Key → Raw → Option Prepared)
    (frame : Frame Context Raw Prepared Output) : List (Value Output) :=
  frame.requests.map fun request =>
    direct frame.provider resolve request.parse frame.context request.key request.fallback

theorem frame_correspondence (resolve : Context → Key → Raw → Option Prepared)
    (frame : Frame Context Raw Prepared Output) (coverage : frame.covered) :
    runFrame resolve frame = directFrame resolve frame := by
  apply List.map_congr_left
  intro request member
  exact prepared_evaluation _ _ _ _ _ _ _ (coverage request member)

def runHistory (resolve : Context → Key → Raw → Option Prepared)
    (frames : List (Frame Context Raw Prepared Output)) : List (List (Value Output)) :=
  frames.map (runFrame resolve)

theorem history_correspondence (resolve : Context → Key → Raw → Option Prepared)
    (frames : List (Frame Context Raw Prepared Output))
    (coverage : ∀ frame ∈ frames, frame.covered) :
    runHistory resolve frames = frames.map (directFrame resolve) := by
  apply List.map_congr_left
  intro frame member
  exact frame_correspondence _ _ (coverage frame member)

theorem successful_attribute_tainted (provider : Provider Raw) (cache : Cache Prepared)
    (parse : Prepared → Option Output) (key : Key) (fallback : Value Output)
    (raw : Raw) (value : Output) (present : provider key = some raw)
    (success : (cache key).bind parse = some value) :
    evaluate provider cache parse key fallback = ⟨value, true⟩ := by
  simp [evaluate, present, success]

end KeyframeAttributePreparation
