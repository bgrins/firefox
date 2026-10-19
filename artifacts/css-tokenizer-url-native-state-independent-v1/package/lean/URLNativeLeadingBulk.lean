import URLNativeBorrowed
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeLeadingBulk
open URLNativeState
abbrev Byte := CommentScan.Byte

def apply (consumed : Nat) (stats : URLWhitespace.Stats) (s : State) : State :=
 let moved := {s with position:=s.position+consumed}
 if stats.lines>0 then
   advanceLine {moved with currentLineStart:=wrap (s.position+stats.last+1)} stats.lines
 else moved

def bulk (ws : List Byte) (s : State) : State :=
 apply ws.length (URLWhitespace.scan ws 0 ⟨0,0⟩) s

theorem stats_summary (ws : List Byte) :
 URLWhitespace.scan ws 0 ⟨0,0⟩=URLWhitespace.summary ws := by
 rw [URLWhitespace.scan_summary]
 cases hs : URLWhitespace.summary ws with
 | mk lines last =>
   simp only [Nat.zero_add]
   by_cases hl : lines>0
   · simp [hl]
   · have hz : lines=0 := by omega
     have lastzero : (URLWhitespace.summary ws).lines=0 → (URLWhitespace.summary ws).last=0 := by
       cases ws with
       | nil => simp [URLWhitespace.summary]
       | cons b bs =>
         simp only [URLWhitespace.summary]
         intro h
         have zero : (URLWhitespace.summary bs).lines=0 := by omega
         simp [zero]
     have he := lastzero (by simp [hs,hz])
     simp only [hs] at he
     simp [hz,he]

def Admitted (ws : List Byte) (s : State) : Prop :=
 (URLWhitespace.summary ws).lines<1073741824 ∧
 s.packedLine+(URLWhitespace.summary ws).lines*4<modulus

theorem stored_metadata (ws : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : Admitted ws s) :
 Related (bulk ws s) (URLWhitespace.nativeBulk ws r) block := by
 rw [URLWhitespace.bulk_summary]
 simp only [bulk,stats_summary,apply,URLWhitespace.applySummary]
 by_cases hl : (URLWhitespace.summary ws).lines>0
 · simp only [hl,↓reduceIte]
   have lastbound := URLWhitespace.last_bound ws hl
   obtain ⟨hp,hs,hline,hblock⟩ := h
   refine ⟨by simp [advanceLine,hp],?_,?_,hblock⟩
   · dsimp only [advanceLine]
     rw [hp]
     congr 1
     simp only [Int.natCast_add,Int.natCast_sub (Nat.le_of_lt lastbound)]
     omega
   · change (advanceLine s (URLWhitespace.summary ws).lines).packedLine=4*(r.line+(URLWhitespace.summary ws).lines)+block
     rw [packed_add_exact s _ ha.1 ha.2]
     rw [hline]
     omega
 · have hz : (URLWhitespace.summary ws).lines=0 := by omega
   simpa [hl,hz,advance,CommentObservers.advance] using advance_related s r block ws.length h

theorem metadata (ws : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : Admitted ws s)
 (white : ∀ b∈ws, URLScan.nativeWhitespace b=true) :
 Related (bulk ws s) (CommentObservers.nativeObserve ws r) block := by
 rw [← URLWhitespace.native_metadata ws r white]
 exact stored_metadata ws s r block h ha

theorem position (ws : List Byte) (s : State) : (bulk ws s).position=s.position+ws.length := by
 simp only [bulk,apply]
 split <;> rfl

theorem close_after (ws : List Byte) (s : State) :
 apply (ws.length+1) (URLWhitespace.scan ws 0 ⟨0,0⟩) s=advance (bulk ws s) 1 := by
 unfold bulk
 by_cases hl : (URLWhitespace.scan ws 0 ⟨0,0⟩).lines>0
 all_goals simp [apply,hl,advance,advanceLine,Nat.add_assoc]
end URLNativeLeadingBulk
