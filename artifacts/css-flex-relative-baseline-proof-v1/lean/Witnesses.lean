import RelativeBaseline
namespace FlexRelativeWitnesses
open FlexRelativeBaseline

def fresh : Frame := visualShift ⟨0,20⟩ exampleFrame
def firstCorrect : Int := correctedDistance false .horizontal ⟨160,80⟩ fresh
def lastCorrect : Int := correctedDistance true .horizontal ⟨160,80⟩ fresh
def firstActual : Int := originalDistance false .horizontal ⟨160,80⟩ fresh
def lastActual : Int := originalDistance true .horizontal ⟨160,80⟩ fresh
def discardProperty : Int := correctedDistance false .horizontal ⟨160,80⟩ { fresh with normalProperty := none }
def noLastConversion : Int := logicalB .horizontal ⟨160,80⟩ fresh.size fresh.expectedNormal+fresh.lastAscent
def overwriteEstablished : Int := native false false .horizontal ⟨160,80⟩ unset [fresh]
def preserveEstablished : Int := native false false .horizontal ⟨160,80⟩ 23 [fresh]

theorem first_getter_mutant_discriminates : firstActual ≠ firstCorrect := by decide +kernel
theorem last_getter_mutant_discriminates : lastActual ≠ lastCorrect := by decide +kernel
theorem property_dispatch_mutant_discriminates : discardProperty ≠ firstCorrect := by decide +kernel
theorem last_orientation_mutant_discriminates : noLastConversion ≠ lastCorrect := by decide +kernel
theorem shared_ascent_guard_mutant_discriminates : overwriteEstablished ≠ preserveEstablished := by decide +kernel

end FlexRelativeWitnesses
