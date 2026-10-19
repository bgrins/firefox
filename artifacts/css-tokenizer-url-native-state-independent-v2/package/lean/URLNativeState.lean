import CommentObservers
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace URLNativeState
abbrev Byte := CommentScan.Byte
abbrev modulus : Nat := 4294967296
def wrap (n : Int) : Int := n % (modulus:Int)
structure State where
 position : Nat
 currentLineStart : Int
 packedLine : Nat
 deriving DecidableEq, Repr

def advance (s : State) (n : Nat) : State := {s with position:=s.position+n}
def intro (s : State) : State :=
 {s with position:=s.position+1,currentLineStart:=wrap (s.currentLineStart-1)}
def continuation (s : State) : State :=
 {s with position:=s.position+1,currentLineStart:=wrap (s.currentLineStart+1)}
def known (s : State) (b : Byte) : State :=
 if 240≤b.val then intro s
 else if 128≤b.val ∧ b.val≤191 then continuation s else advance s 1

def advanceLine (s : State) (count : Nat) : State :=
 {s with packedLine := (s.packedLine+(count*4)%modulus)%modulus}
def newline (s : State) (length : Nat) : State :=
 advanceLine {s with position:=s.position+length, currentLineStart:=wrap (s.position+length)} 1

def character (s : State) (bytes units : Nat) : State :=
 {s with position:=s.position+bytes, currentLineStart:=wrap (s.currentLineStart+(bytes-units:Nat))}

def Related (s : State) (r : CommentObservers.State) (block : Nat) : Prop :=
 s.position=r.offset ∧
 s.currentLineStart=wrap ((r.offset:Int)+1-r.column) ∧
 s.packedLine=4*r.line+block ∧ block<4

def location (s : State) : Nat × Int :=
 (s.packedLine/4,wrap ((s.position:Int)-s.currentLineStart+1))

theorem wrap_add_left (a b : Int) : wrap (wrap a+b)=wrap (a+b) := by
 simp only [wrap,Int.add_emod,Int.emod_emod]
theorem wrap_sub_left (a b : Int) : wrap (wrap a-b)=wrap (a-b) := by
 simp only [wrap,Int.sub_emod,Int.emod_emod]
theorem wrap_sub_right (a b : Int) : wrap (a-wrap b)=wrap (a-b) := by
 simp only [wrap,Int.sub_emod,Int.emod_emod]

theorem source_location (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) : location s=(r.line,wrap r.column) := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 unfold location
 rw [hp,hs,hl]
 have line : (4*r.line+block)/4=r.line := by omega
 rw [line]
 congr 1
 rw [← wrap_add_left,wrap_sub_right,wrap_add_left]
 congr 1
 omega

theorem source_location_headroom (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (hc : r.column<modulus) :
 location s=(r.line,(r.column:Int)) := by
 rw [source_location s r block h]
 congr 1
 exact Int.emod_eq_of_lt (by omega) (by exact_mod_cast hc)

theorem advance_related (s : State) (r : CommentObservers.State) (block n : Nat)
 (h : Related s r block) : Related (advance s n) (CommentObservers.advance n r) block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 refine ⟨by simp [advance,CommentObservers.advance,hp],?_,hl,hb⟩
 dsimp [advance,CommentObservers.advance]
 rw [hs]
 congr 1
 try simp only [Int.natCast_add]
 omega

theorem intro_related (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) :
 Related (intro s) ⟨r.offset+1,r.line,r.column+2⟩ block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 refine ⟨by simp [intro,hp],?_,hl,hb⟩
 dsimp [intro]
 rw [hs,wrap_sub_left]
 congr 1
 try simp only [Int.natCast_add]
 omega

theorem continuation_related (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) :
 Related (continuation s) ⟨r.offset+1,r.line,r.column⟩ block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 refine ⟨by simp [continuation,hp],?_,hl,hb⟩
 dsimp [continuation]
 rw [hs,wrap_add_left]
 congr 1
 try simp only [Int.natCast_add]
 omega

theorem known_related (s : State) (r : CommentObservers.State) (block : Nat) (b : Byte)
 (h : Related s r block) :
 Related (known s b) (CommentObservers.ordinary b r) block := by
 unfold known
 split
 · rename_i hb
   have noCont : ¬(128≤b.val ∧ b.val≤191) := by omega
   simpa [CommentObservers.ordinary,CommentObservers.nativeWidth,hb,noCont] using intro_related s r block h
 · rename_i hi
   split
   · rename_i hc
     simpa [CommentObservers.ordinary,CommentObservers.nativeWidth,hc] using continuation_related s r block h
   · rename_i hc
     simpa [CommentObservers.ordinary,CommentObservers.nativeWidth,hc,hi,CommentObservers.advance] using advance_related s r block 1 h

theorem packed_add_exact (s : State) (count : Nat)
 (shift : count<1073741824) (add : s.packedLine+count*4<modulus) :
 (advanceLine s count).packedLine=s.packedLine+count*4 := by
 have hs : count*4<modulus := by
  exact Nat.mul_lt_mul_of_pos_right shift (by decide)
 simp [advanceLine,Nat.mod_eq_of_lt hs,Nat.mod_eq_of_lt add]

theorem advance_line_related (s : State) (r : CommentObservers.State) (block count : Nat)
 (h : Related s r block) (shift : count<1073741824)
 (add : s.packedLine+count*4<modulus) :
 Related (advanceLine s count) ⟨r.offset,r.line+count,r.column⟩ block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 refine ⟨hp,hs,?_,hb⟩
 change (advanceLine s count).packedLine=4*(r.line+count)+block
 rw [packed_add_exact s count shift add,hl]
 omega

theorem newline_related (s : State) (r : CommentObservers.State) (block length : Nat)
 (h : Related s r block) (add : s.packedLine+4<modulus) :
 Related (newline s length) (CommentObservers.newline length r) block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 unfold newline
 apply advance_line_related _ ⟨r.offset+length,r.line,1⟩ block 1
 · refine ⟨by simp [hp],?_,hl,hb⟩
   dsimp
   rw [hp]
   congr 1
   try simp only [Int.natCast_add]
   omega
 · decide
 · exact add

theorem character_related (s : State) (r : CommentObservers.State) (block bytes units : Nat)
 (h : Related s r block) (width : units≤bytes) :
 Related (character s bytes units) ⟨r.offset+bytes,r.line,r.column+units⟩ block := by
 obtain ⟨hp,hs,hl,hb⟩ := h
 refine ⟨by simp [character,hp],?_,hl,hb⟩
 dsimp [character]
 rw [hs,wrap_add_left]
 congr 1
 try simp only [Int.natCast_add]
 omega

theorem native_byte_masks : ∀ b : Byte,
 (Nat.land b.val 240=240 ↔ 240≤b.val) ∧
 (Nat.land b.val 192=128 ↔ 128≤b.val ∧ b.val≤191) := by decide

theorem initial_astral_wrap :
 intro ⟨0,0,0⟩ = ⟨1,4294967295,0⟩ := by decide

theorem initial_astral_location :
 location (continuation (continuation (continuation (intro ⟨0,0,0⟩)))) = (0,3) := by decide
end URLNativeState
