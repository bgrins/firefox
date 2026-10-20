import CommentExecution
import Boundary
set_option maxRecDepth 4096
set_option maxHeartbeats 3000000
namespace CommentUTF8
open CommentScan
abbrev Unit := Boundary.Unit
abbrev bytes := Boundary.bytes

theorem stop_false (b : Byte) (tail : List Byte) (h : b ≠ 42) : stop b tail = false := by
  simp [stop,h]

theorem prefix_scan (pre tail : List Byte) (h : ∀ b ∈ pre, b ≠ 42) :
    scan (pre++tail) = ⟨pre++(scan tail).body,(scan tail).count+pre.length,(scan tail).closed⟩ := by
  induction pre with
  | nil => simp [scan]
  | cons b bs ih =>
    have hb := stop_false b (bs++tail) (h b (by simp))
    have ht := ih (fun c hc => h c (by simp [hc]))
    simp [scan,hb,ht,Nat.add_assoc]

theorem drop_prefix (pre tail : List Byte) (n : Nat) :
    (pre++tail).drop (n+pre.length) = tail.drop n := by
  rw [Nat.add_comm n,← List.drop_drop]
  simp

theorem unit_nonstar (u : Unit) (h : u.first ≠ 42) : ∀ b ∈ u.bytes, b ≠ 42 := by
  intro b hb
  simp only [Boundary.Unit.bytes,List.mem_cons] at hb
  rcases hb with rfl | hb
  · exact h
  · have hc := u.continuation b hb
    intro he
    subst b
    have hh : (42 : Byte).val = 42 := rfl
    omega

theorem valid_body_and_suffix (units : List Unit) :
    ∃ body rest : List Unit, (scan (bytes units)).body = bytes body ∧
      (bytes units).drop (scan (bytes units)).count = bytes rest := by
  induction units with
  | nil => exact ⟨[],[],rfl,rfl⟩
  | cons u us ih =>
    obtain ⟨body,rest,hbody,hrest⟩ := ih
    by_cases hs : u.first = 42
    · have hr : u.rest = [] := Boundary.unit_ascii_singleton u (by simpa [hs] using (show (42 : Byte).val < 128 by decide))
      have hb : bytes (u::us) = 42 :: bytes us := by simp [bytes,Boundary.bytes,Boundary.Unit.bytes,hs,hr]
      by_cases hstop : stop 42 (bytes us) = true
      · obtain ⟨tail,_,htail⟩ := stop_tail 42 (bytes us) hstop
        obtain ⟨after,ha⟩ := Boundary.ascii_step us 47 tail htail (by decide)
        refine ⟨[],after,?_,?_⟩
        · rw [hb]
          simp [scan,hstop]
          rfl
        · rw [hb]
          simp [scan,htail,stop,ha]
      · refine ⟨u::body,rest,?_,?_⟩
        · have hbodybytes : bytes (u::body) = 42::bytes body := by simp [bytes,Boundary.bytes,Boundary.Unit.bytes,hs,hr]
          rw [hb,hbodybytes]
          simp [scan,hstop,hbody]
        · simpa [hb,scan,hstop] using hrest
    · have hpre := prefix_scan u.bytes (bytes us) (unit_nonstar u hs)
      have hb : bytes (u::us) = u.bytes ++ bytes us := rfl
      refine ⟨u::body,rest,?_,?_⟩
      · change (scan (u.bytes ++ bytes us)).body = u.bytes ++ bytes body
        rw [hpre]
        simp [hbody]
      · rw [hb,hpre]
        exact (drop_prefix u.bytes (bytes us) _).trans hrest

theorem raw_opening_suffix (units : List Unit) (tail : List Byte)
    (h : bytes units = 47::42::tail) : ∃ rest : List Unit, tail = bytes rest := by
  obtain ⟨middle,hm⟩ := Boundary.ascii_step units 47 (42::tail) h (by decide)
  exact Boundary.ascii_step middle 42 tail hm.symm (by decide)

theorem raw_body_and_suffix (units : List Unit) (tail : List Byte)
    (h : bytes units = 47::42::tail) :
    ∃ body rest : List Unit, (scan tail).body = bytes body ∧ tail.drop (scan tail).count = bytes rest := by
  obtain ⟨inside,hi⟩ := raw_opening_suffix units tail h
  simpa [hi] using valid_body_and_suffix inside

theorem takeWhile_prefix (p : Byte → Bool) (pre tail : List Byte)
    (h : ∀ b ∈ pre, p b = true) :
    (pre++tail).takeWhile p = pre ++ tail.takeWhile p := by
  induction pre with
  | nil => simp
  | cons b bs ih =>
    simp [h b (by simp),ih (fun c hc => h c (by simp [hc]))]

theorem valid_takeWhile (p : Byte → Bool) (nonAscii : ∀ b : Byte, 128 ≤ b.val → p b = true)
    (units : List Unit) : ∃ picked : List Unit, (bytes units).takeWhile p = bytes picked := by
  induction units with
  | nil => exact ⟨[],rfl⟩
  | cons u us ih =>
    by_cases hh : p u.first = true
    · have hall : ∀ b ∈ u.bytes, p b = true := by
        intro b hb
        simp only [Boundary.Unit.bytes,List.mem_cons] at hb
        rcases hb with rfl | hb
        · exact hh
        · exact nonAscii b (u.continuation b hb).1
      obtain ⟨picked,hp⟩ := ih
      refine ⟨u::picked,?_⟩
      change (u.bytes ++ bytes us).takeWhile p = u.bytes ++ bytes picked
      rw [takeWhile_prefix p u.bytes (bytes us) hall,hp]
    · refine ⟨[],?_⟩
      simp [bytes,Boundary.bytes,Boundary.Unit.bytes,hh]

theorem url_prefix_utf8 (units : List Unit) :
    ∃ picked : List Unit,
      (bytes units).takeWhile (fun b => !CommentDirectives.referenceSpace b) = bytes picked := by
  apply valid_takeWhile
  intro b hb
  have hall : ∀ c : Byte, 128 ≤ c.val → CommentDirectives.referenceSpace c = false := by decide
  have hc := hall b hb
  simp [hc]
theorem literal_suffix_utf8 (key : List Byte) (units : List Unit) (rest : List Byte)
    (asciiKey : ∀ b ∈ key, b.val < 128)
    (matched : CommentDirectives.consumeLiteral key (bytes units) = some rest) :
    ∃ suffix : List Unit, rest = bytes suffix := by
  induction key generalizing units with
  | nil => exact ⟨units, by simpa [CommentDirectives.consumeLiteral] using matched.symm⟩
  | cons b bs ih =>
    cases hu : bytes units with
    | nil => simp [hu,CommentDirectives.consumeLiteral] at matched
    | cons c cs =>
      by_cases he : b = c
      · subst c
        obtain ⟨tail,ht⟩ := Boundary.ascii_step units b cs hu (asciiKey b (by simp))
        apply ih tail (fun x hx => asciiKey x (by simp [hx]))
        simpa [hu,CommentDirectives.consumeLiteral,ht] using matched
      · simp [hu,CommentDirectives.consumeLiteral,he] at matched

theorem directive_value_utf8 (key : List Byte) (units : List Unit) (value : List Byte)
    (asciiKey : ∀ b ∈ key, b.val < 128)
    (matched : CommentDirectives.referenceDirective key (bytes units) = some value) :
    ∃ result : List Unit, value = bytes result := by
  cases hu : bytes units with
  | nil => simp [hu,CommentDirectives.referenceDirective] at matched
  | cons flag rest =>
    cases hr : rest with
    | nil => simp [hu,hr,CommentDirectives.referenceDirective] at matched
    | cons space tail =>
      by_cases guard : ((flag == 35 || flag == 64) && space == 32) = true
      · have g := guard
        simp only [Bool.and_eq_true,Bool.or_eq_true,beq_iff_eq] at g
        obtain ⟨hf,hs⟩ := g
        have flagAscii : flag.val < 128 := by rcases hf with rfl | rfl <;> decide
        obtain ⟨u1,h1⟩ := Boundary.ascii_step units flag (space::tail) (by simpa [hr] using hu) flagAscii
        obtain ⟨u2,h2⟩ := Boundary.ascii_step u1 space tail h1.symm (by subst space; decide)
        cases hm : CommentDirectives.consumeLiteral key tail with
        | none => simp [hu,hr,CommentDirectives.referenceDirective,guard,hm] at matched
        | some remaining =>
          obtain ⟨u3,h3⟩ := literal_suffix_utf8 key u2 remaining asciiKey (by simpa [h2] using hm)
          obtain ⟨picked,hp⟩ := url_prefix_utf8 u3
          refine ⟨picked,?_⟩
          have hv : remaining.takeWhile (fun b => !CommentDirectives.referenceSpace b) = value := by
            simpa [hu,hr,CommentDirectives.referenceDirective,guard,hm] using matched
          exact hv.symm.trans (by simpa [h3] using hp)
      · simp [hu,hr,CommentDirectives.referenceDirective,guard] at matched
end CommentUTF8
