import URLNativeLeadingBulk
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeLeading
open URLNativeState
abbrev Byte := CommentScan.Byte
inductive Result where
 | function (state : State)
 | emptyURL (state : State)
 | body (value : URLNativeBorrowed.Entry)
 deriving DecidableEq, Repr

def scan : List Byte → Nat → URLWhitespace.Stats → State → Result
 | [], index, stats, s => .emptyURL (URLNativeLeadingBulk.apply index stats s)
 | b::bs, index, stats, s =>
   if URLScan.nativeWhitespace b then
     scan bs (index+1) (if URLWhitespace.marks b bs then ⟨stats.lines+1,index⟩ else stats) s
   else if URLLeading.quote b then .function s
   else if b==41 then .emptyURL (URLNativeLeadingBulk.apply (index+1) stats s)
   else .body (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.apply index stats s))

def run (xs : List Byte) (s : State) : Result := scan xs 0 ⟨0,0⟩ s

theorem marks_append (b : Byte) (bs tail : List Byte) (safe : tail.head?≠some 10) :
 URLWhitespace.marks b (bs++tail)=URLWhitespace.marks b bs := by
 cases bs with
 | nil =>
   have he : (tail.head? != some (10:Byte))=true := by simpa only [bne_iff_ne] using safe
   have hn : ((none:Option Byte) != some 10)=true := rfl
   simp [URLWhitespace.marks,he,hn]
 | cons c cs => rfl

theorem scan_prefix (ws tail : List Byte) (index : Nat) (stats : URLWhitespace.Stats) (s : State)
 (white : ∀ b∈ws, URLScan.nativeWhitespace b=true) (safe : tail.head?≠some 10) :
 scan (ws++tail) index stats s=
 scan tail (index+ws.length) (URLWhitespace.scan ws index stats) s := by
 induction ws generalizing index stats with
 | nil => simp [URLWhitespace.scan]
 | cons b bs ih =>
   have hb := white b (by simp)
   have ht := ih (index+1) (if URLWhitespace.marks b bs then ⟨stats.lines+1,index⟩ else stats)
     (fun c hc => white c (by simp [hc]))
   simpa [scan,hb,marks_append b bs tail safe,URLWhitespace.scan,Nat.add_assoc,Nat.add_comm 1] using ht

theorem nonwhite_not_lf (tail : List Byte)
 (hn : ∀ b∈tail.head?, URLScan.nativeWhitespace b=false) : tail.head?≠some 10 := by
 intro h
 have he := hn 10 (by simp [h])
 contradiction

theorem decomposition (xs : List Byte) :
 ∃ ws tail, xs=ws++tail ∧
  (∀ b∈ws,URLScan.nativeWhitespace b=true) ∧
  (∀ b∈tail.head?,URLScan.nativeWhitespace b=false) := by
 induction xs with
 | nil => exact ⟨[],[],rfl,by simp,by simp⟩
 | cons b bs ih =>
   by_cases hw : URLScan.nativeWhitespace b=true
   · obtain ⟨ws,tail,he,hws,ht⟩ := ih
     exact ⟨b::ws,tail,by simp [he],by intro c hc; rcases List.mem_cons.mp hc with rfl|hc; exact hw; exact hws c hc,ht⟩
   · exact ⟨[],b::bs,rfl,by simp,by simpa using hw⟩

theorem source_scan (xs : List Byte) (s : State) :
 ∃ ws tail, xs=ws++tail ∧
  (∀ b∈ws,URLScan.nativeWhitespace b=true) ∧
  (∀ b∈tail.head?,URLScan.nativeWhitespace b=false) ∧
  run xs s=scan tail ws.length (URLWhitespace.scan ws 0 ⟨0,0⟩) s := by
 obtain ⟨ws,tail,he,hw,ht⟩ := decomposition xs
 refine ⟨ws,tail,he,hw,ht,?_⟩
 simp only [run,he]
 simpa using scan_prefix ws tail 0 ⟨0,0⟩ s hw (nonwhite_not_lf tail ht)

theorem quote_rollback (ws body : List Byte) (q : Byte) (s : State)
 (hw : ∀ b∈ws, URLScan.nativeWhitespace b=true) (hq : URLLeading.quote q=true) :
 run (ws++q::body) s=.function s := by
 have hn : URLScan.nativeWhitespace q=false := by
   have disjoint : ∀ b : Byte, URLLeading.quote b=true → URLScan.nativeWhitespace b=false := by decide
   exact disjoint q hq
 rw [run,scan_prefix ws (q::body) 0 ⟨0,0⟩ s hw (nonwhite_not_lf _ (by simpa using hn))]
 simp [scan,hn,hq]

theorem empty_end (ws : List Byte) (s : State)
 (hw : ∀ b∈ws, URLScan.nativeWhitespace b=true) :
 run ws s=.emptyURL (URLNativeLeadingBulk.bulk ws s) := by
 have he := scan_prefix ws [] 0 ⟨0,0⟩ s hw (by simp)
 simpa [run,scan,URLNativeLeadingBulk.bulk] using he

theorem close_end (ws tail : List Byte) (s : State)
 (hw : ∀ b∈ws, URLScan.nativeWhitespace b=true) :
 run (ws++41::tail) s=.emptyURL (advance (URLNativeLeadingBulk.bulk ws s) 1) := by
 rw [run,scan_prefix ws (41::tail) 0 ⟨0,0⟩ s hw (by simp)]
 simp only [scan,show URLScan.nativeWhitespace (41:Byte)=false by decide,
   show URLLeading.quote (41:Byte)=false by decide,beq_self_eq_true,↓reduceIte,Nat.zero_add]
 rw [URLNativeLeadingBulk.close_after]
 simp

theorem body_entry (ws : List Byte) (b : Byte) (bs : List Byte) (s : State)
 (hw : ∀ c∈ws,URLScan.nativeWhitespace c=true)
 (hn : URLScan.nativeWhitespace b=false) (hq : URLLeading.quote b=false) (hc : b≠41) :
 run (ws++b::bs) s=.body (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.bulk ws s)) := by
 rw [run,scan_prefix ws (b::bs) 0 ⟨0,0⟩ s hw (nonwhite_not_lf _ (by simpa using hn))]
 simp [scan,hn,hq,hc,URLNativeLeadingBulk.bulk]

theorem body_metadata (ws : List Byte) (b : Byte) (bs : List Byte)
 (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (hw : ∀ c∈ws,URLScan.nativeWhitespace c=true)
 (hn : URLScan.nativeWhitespace b=false)
 (ha : URLNativeLeadingBulk.Admitted ws s)
 (bodyAdmission : URLNativeBody.Admitted (b::bs) (URLNativeLeadingBulk.bulk ws s))
 (valid : URLNativeAlignment.TailValid (b::bs)) :
 Related (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.bulk ws s)).result.state
 (CommentObservers.nativeObserve (ws++(b::bs).take (URLScan.reference (b::bs)).count) r) block := by
 have hb := URLNativeLeadingBulk.metadata ws s r block h ha hw
 have he := URLNativeBorrowed.metadata (b::bs) _ _ block hb bodyAdmission valid
 have safe : URLDelegation.NoSplit ws ((b::bs).take (URLScan.reference (b::bs)).count) :=
   Or.inr (CommentExecution.head_take_not _ _ 10 (nonwhite_not_lf _ (by simpa using hn)))
 rw [URLDelegation.observe_append _ _ r safe]
 exact he

theorem body_raw_source (before ws : List Byte) (b : Byte) (bs : List Byte) (s : State)
 (hp : s.position=before.length) (valid : URLNativeAlignment.TailValid (b::bs)) :
 URLNativeBorrowed.captured (before++ws++b::bs)
   (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.bulk ws s)) =
 if (URLScan.reference (b::bs)).kind=.bad then some (URLTrace.rawPayload (URLTrace.run (b::bs))) else none := by
 apply URLNativeBorrowed.captured_source (before++ws) (b::bs) _ _ valid
 simp [URLNativeLeadingBulk.position,hp]
theorem body_valid (ws tail : List Byte) (valid : StringUTF8.Valid (ws++tail))
 (white : ∀ b∈ws,URLScan.nativeWhitespace b=true) : StringUTF8.Valid tail := by
 obtain ⟨units,hu⟩ := valid
 obtain ⟨rest,hr⟩ := Boundary.ascii_prefix units ws tail hu.symm
   (fun b hb => URLUTF8.whitespace_ascii b (white b hb))
 exact ⟨rest,hr⟩

theorem admitted_body_metadata (ws : List Byte) (b : Byte) (bs : List Byte)
 (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (hw : ∀ c∈ws,URLScan.nativeWhitespace c=true)
 (hn : URLScan.nativeWhitespace b=false)
 (ha : URLNativeLeadingBulk.Admitted ws s)
 (bodyAdmission : URLNativeBody.Admitted (b::bs) (URLNativeLeadingBulk.bulk ws s))
 (valid : StringUTF8.Valid (ws++b::bs)) :
 Related (URLNativeBorrowed.entry (b::bs) (URLNativeLeadingBulk.bulk ws s)).result.state
 (CommentObservers.nativeObserve (ws++(b::bs).take (URLScan.reference (b::bs)).count) r) block :=
 body_metadata ws b bs s r block h hw hn ha bodyAdmission
   (URLNativeAlignment.from_valid _ (body_valid ws (b::bs) valid hw))
end URLNativeLeading
