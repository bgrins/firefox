import ByteLex
import PublicCleanup
set_option autoImplicit false
namespace ByteLexProgress
open PublicCache ByteLex

def ProviderProgress (provider : Family → List Byte → Nat) : Prop :=
 ∀ family xs, xs≠[] → 0<provider family xs

def ProviderBound (provider : Family → List Byte → Nat) : Prop :=
 ∀ family xs, provider family xs≤xs.length

theorem other_positive (provider : Family → List Byte → Nat) (xs : List Byte)
 (hp : ProviderProgress provider) (hn : xs≠[]) : 0<(other provider xs).count := by
 unfold other
 split
 · dsimp only
   omega
 · decide
 · decide
 · decide
 · decide
 · decide
 · decide
 · decide
 · contradiction
 · exact hp _ _ hn

theorem other_bound (provider : Family → List Byte → Nat) (xs : List Byte)
 (hb : ProviderBound provider) : (other provider xs).count≤xs.length := by
 unfold other
 split
 · rename_i tail
   have h := CommentScan.consumed_bound tail
   simp only [List.length_cons]
   omega
 · simp
 · simp
 · simp
 · simp
 · simp
 · simp
 · simp
 · simp
 · exact hb _ _

theorem count_positive (provider : Family → List Byte → Nat) (xs : List Byte)
 (hp : ProviderProgress provider) (hn : xs≠[]) : 0<(native provider xs).count := by
 by_cases hs : selected xs=true
 · exact ident_count_positive provider xs hs
 · simpa [native,hs] using other_positive provider xs hp hn

theorem count_bound (provider : Family → List Byte → Nat) (xs : List Byte)
 (hb : ProviderBound provider) : (native provider xs).count≤xs.length := by
 unfold native
 split
 · exact URLDispatch.count_bound xs false
 · exact other_bound provider xs hb

theorem read_progress (provider : Family → List Byte → Nat) (source : List Byte)
 (hp : ProviderProgress provider) : PublicCleanup.Progress source.length (ByteLex.read provider source) := by
 intro position hpos
 have hn : source.drop position≠[] := by
   intro he
   have len := congrArg List.length he
   simp only [List.length_drop,List.length_nil] at len
   omega
 have h := count_positive provider (source.drop position) hp hn
 simp only [ByteLex.read]
 omega

theorem read_bound (provider : Family → List Byte → Nat) (source : List Byte)
 (position : Nat) (hb : ProviderBound provider) (hpos : position≤source.length) :
 (ByteLex.read provider source position).cursor.position≤source.length := by
 have h := count_bound provider (source.drop position) hb
 simp only [List.length_drop] at h
 simp only [ByteLex.read]
 omega

theorem pending_cleanup_complete (provider : Family → List Byte → Nat)
 (source : List Byte) (names : List (List Byte)) (s : State) (hp : ProviderProgress provider) :
 (PublicCleanup.pending source.length (ByteLex.read provider source) names s).complete=true :=
 PublicCleanup.pending_complete _ _ _ _ (read_progress provider source hp)

end ByteLexProgress
