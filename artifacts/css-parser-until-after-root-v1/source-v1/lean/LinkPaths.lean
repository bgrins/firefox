import LinkEmpty
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace LinkPaths
open PublicCache

def provider (family : ByteLex.Family) (xs : List Byte) : Nat :=
  match family with
  | .whitespace => (xs.takeWhile URLScan.nativeWhitespace).length
  | .punctuation => if [33,44,59].contains (xs.head?.getD 0) then 1 else 0
  | _ => 0

def run (bytes : List Byte) : Bool × Bool × Nat × Option Block × List Byte × Nat :=
  let names := [[118,97,114]]
  let start : NestedControl.State := ⟨PublicHistory.begin names (constructor ⟨none,none⟩),[],0,75⟩
  let result := LinkEmpty.parse bytes (ByteLex.read provider bytes) names start
  (result.1,(PublicHistory.query result.2.core).1,result.2.core.cursor.position,
    result.2.core.cursor.pending,result.2.stops,result.2.depth.val)

theorem two_empty_values : run [112,97,114,97,109,40,45,45,120,44,41,44,112,97,114,97,109,40,45,45,121,44,41] = (true,false,23,none,[],0) := by decide +kernel

theorem failed_function_recovers_var : run [112,97,114,97,109,40,45,45,120,44,41,44,98,97,100,40,118,97,114,40,45,45,121,41,41] = (false,true,25,none,[],0) := by decide +kernel

theorem failed_comma_recovers_var : run [112,97,114,97,109,40,45,45,120,44,41,44,112,97,114,97,109,40,45,45,121,32,118,97,114,40,45,45,122,41,41] = (false,true,31,none,[],0) := by decide +kernel

theorem none_value : run [110,111,110,101] = (true,false,4,none,[],0) := by decide +kernel

theorem one_empty_value : run [112,97,114,97,109,40,45,45,120,44,41] = (true,false,11,none,[],0) := by decide +kernel

theorem trailing_comma_fails : run [112,97,114,97,109,40,45,45,120,44,41,44] = (false,false,12,none,[],0) := by decide +kernel

end LinkPaths
