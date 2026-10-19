import URLNativeBodyState
import URLNativeSlice
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeBorrowed
open URLNativeState URLNativeEnd URLNativeAlignment
abbrev Byte := CommentScan.Byte

def run : List Byte → State → Result
 | [], s => ⟨s,none⟩
 | b::bs, s => match URLScan.nativeClass b with
   | .close => ⟨advance s 1,none⟩
   | .invalid => bad bs (advance s 1)
   | .space => URLNativeEnd.run (b::bs) s
   | .copy => run bs (known s b)
   | _ => URLNativeBody.run (b::bs) s

theorem state_handoff (xs : List Byte) (s : State) : run xs s=URLNativeBody.run xs s := by
 induction xs generalizing s with
 | nil => simp [run,URLNativeBody.run]
 | cons b bs ih =>
   cases hc : URLScan.nativeClass b <;> simp [run,URLNativeBody.run,hc,ih]

structure Entry where
 startPosition : Nat
 result : Result
 deriving DecidableEq, Repr

def entry (xs : List Byte) (s : State) : Entry := ⟨s.position,run xs s⟩

def captured (source : List Byte) (e : Entry) : Option (List Byte) :=
 e.result.rawEnd.map (fun finish => URLNativeSlice.slice source e.startPosition finish)

theorem metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : URLNativeBody.Admitted xs s) (hv : TailValid xs) :
 Related (entry xs s).result.state
 (CommentObservers.nativeObserve (xs.take (URLScan.reference xs).count) r) block := by
 simp only [entry,state_handoff]
 have he := URLNativeBodyState.metadata xs s r block h ha hv
 simpa only [URLNativeBodyState.observed,URLTrace.trace_exact,URLTrace.value_reference] using he

theorem bad_closed_count (xs : List Byte) :
 (if (BadURL.native xs).closed then 1 else 0)≤(BadURL.native xs).count := by
 have he := URLNativeSlice.close_le_count xs ⟨0,0,0⟩
 rw [(URLNativeBad.boundary xs ⟨0,0,0⟩).1,(URLNativeBad.boundary xs ⟨0,0,0⟩).2] at he
 exact he

theorem closed_count_ending (xs : List Byte) :
 (if (URLTrace.ending xs).closed then 1 else 0)≤(URLTrace.ending xs).value.count := by
 induction xs with
 | nil => simp [URLTrace.ending]
 | cons b bs ih =>
   simp only [URLTrace.ending]
   split
   · simp
   · split
     · change (if (URLTrace.ending bs).closed then 1 else 0) ≤ 1+(URLTrace.ending bs).value.count
       exact Nat.le_trans ih (Nat.le_add_left _ 1)
     · exact bad_closed_count (b::bs)

theorem closed_count (xs : List Byte) :
 (if (URLTrace.run xs).closed then 1 else 0)≤(URLTrace.run xs).value.count := by
 induction xs using URLTrace.run.induct with
 | case1 => simp [URLTrace.run]
 | case2 b bs hc => simp [URLTrace.run,hc]
 | case3 b bs hc =>
   have he := bad_closed_count bs
   simp [URLTrace.run,hc,URLTrace.add,URLScan.extend,URLTrace.bad]
   omega
 | case4 b bs hc => simpa [URLTrace.run,hc] using closed_count_ending (b::bs)
 | case5 b bs hc ih => simp only [URLTrace.run,hc,URLTrace.add,URLScan.extend,List.length_singleton]; omega
 | case6 b bs hc ih => simp only [URLTrace.run,hc,URLTrace.add,URLScan.extend,List.length_singleton]; omega
 | case7 b bs hc hn =>
   have he := bad_closed_count bs
   simp [URLTrace.run,hc,hn,URLTrace.add,URLScan.extend,URLTrace.bad]
   omega
 | case8 b bs hc hn e ih =>
   dsimp [e] at ih
   simp [URLTrace.run,hc,hn,URLTrace.add,URLScan.extend] at ih ⊢
   omega

theorem captured_source (before xs : List Byte) (s : State)
 (hp : s.position=before.length) (hv : TailValid xs) :
 captured (before++xs) (entry xs s)=
  if (URLScan.reference xs).kind=.bad then some (URLTrace.rawPayload (URLTrace.run xs)) else none := by
 have hb := URLScan.reference_bound xs
 have hc := closed_count xs
 have he := URLNativeBody.capture xs s hv
 simp only [captured,entry,state_handoff,he]
 rw [← URLTrace.value_reference] at hb
 rw [← URLTrace.value_reference]
 split
 · rename_i hk
   simp only [Option.map_some,URLNativeSlice.slice,hp,List.drop_left]
   have arithmetic : before.length+(URLTrace.run xs).value.count-
     (if (URLTrace.run xs).closed then 1 else 0)-before.length=
     (URLTrace.run xs).value.count-(if (URLTrace.run xs).closed then 1 else 0) := by omega
   rw [arithmetic]
   simp [URLTrace.rawPayload,URLTrace.trace_exact,List.length_take,Nat.min_eq_left hb,List.take_take]
 · simp

theorem captured_range (before xs : List Byte) (s : State)
 (hp : s.position=before.length) (hv : TailValid xs) (finish : Nat)
 (he : (entry xs s).result.rawEnd=some finish) :
 (entry xs s).startPosition≤finish ∧ finish≤(before++xs).length := by
 have hc := closed_count xs
 have hb := URLScan.reference_bound xs
 rw [← URLTrace.value_reference] at hb
 simp only [entry,state_handoff,URLNativeBody.capture xs s hv] at he
 split at he
 · simp only [Option.some.injEq] at he
   simp only [entry,hp,List.length_append]
   omega
 · contradiction
end URLNativeBorrowed
