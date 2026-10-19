import ParseFlags
namespace WinnerWitnesses
open AllOrder PublicStorage ParseWinners ParseFlags
abbrev E := Entry Nat Nat

def source : List E := [⟨0,1,false⟩,⟨1,2,false⟩,⟨0,3,true⟩,⟨2,4,false⟩,⟨0,5,false⟩,⟨1,6,true⟩,⟨0,7,true⟩]

theorem interleaved_priorities : winners source = [⟨2,4,false⟩,⟨1,6,true⟩,⟨0,7,true⟩] := by decide

theorem interleaved_positions :
    (winners (tagged source)).map (fun e => e.value.1) = [3,5,6] := by decide

theorem last_important_beats_later_normal :
    winners [⟨0,1,true⟩,⟨1,2,false⟩,⟨0,3,false⟩] = ([⟨0,1,true⟩,⟨1,2,false⟩] : List E) := by decide

theorem importance_irrelevant_control : lastOnly source = winners source := by decide

theorem ignoring_importance_reduced_witness :
    lastOnly [⟨0,1,true⟩,⟨1,2,false⟩,⟨0,3,false⟩] ≠
      winners ([⟨0,1,true⟩,⟨1,2,false⟩,⟨0,3,false⟩] : List E) := by decide

theorem equal_accepted_value_can_return_true :
    extendResult [⟨0,1,false⟩] [⟨0,1,false⟩] = (([⟨0,1,false⟩] : List E),true) := by decide

theorem all_rejected_returns_false :
    extendResult [⟨0,1,true⟩] [⟨0,2,false⟩,⟨0,3,false⟩] = (([⟨0,1,true⟩] : List E),false) := by decide

theorem stopping_after_first_true_loses_declarations :
    parseExtend [] ([⟨0,1,false⟩,⟨1,2,false⟩] : List E) ≠ parseSet [] ⟨0,1,false⟩ := by decide

theorem initial_prefix_priority :
    parseExtend [⟨0,1,true⟩,⟨1,2,false⟩] [⟨0,3,false⟩,⟨1,4,true⟩,⟨0,5,true⟩] =
      ([⟨1,4,true⟩,⟨0,5,true⟩] : List E) := by decide

end WinnerWitnesses
