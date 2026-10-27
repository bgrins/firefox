import CssSemantics.CssUnitFactor

set_option maxRecDepth 10000
set_option maxHeartbeats 10000000
namespace AbsoluteFactorCertificate

def names : List String := ["px", "cm", "mm", "in", "pt", "pc", "q"]
def pairs : List (String × String) := names.flatMap fun target => names.map (target, ·)
def pixels (unit : String) : Rat :=
  ((CssSemantics.CssUnitFactor.lookup unit).getD ⟨.length, 0⟩).multiplier
def oracle (pair : String × String) : Rat := pixels pair.2 / pixels pair.1
def tolerance : Rat := 4 / (2^23 : Nat)
def decode (bits : Nat) : Rat :=
  let significand : Rat := (bits % 2^23 + 2^23 : Nat)
  let exponent := bits / 2^23 % 256
  if exponent ≥ 150 then significand * ((2 : Nat)^(exponent - 150) : Nat)
  else significand / ((2 : Nat)^(150 - exponent) : Nat)
def normalPositive (bits : Nat) : Prop :=
  bits < 2^31 ∧ 0 < bits / 2^23 % 256 ∧ bits / 2^23 % 256 < 255

instance (bits : Nat) : Decidable (normalPositive bits) := by
  unfold normalPositive
  infer_instance

def originalBits : List Nat := [
  1065353216, 1108815453, 1081205705, 1119879168, 1068149419, 1098907648, 1064428488, 1020837670, 1065353216, 1036831949, 1076006748, 1024491374, 1054392102, 1020054733, 1049065335, 1092616192, 1065353216, 1103835955, 1052024650, 1082619767, 1048576000, 1009429163, 1053397798, 1025589893, 1065353216, 1013157433, 1042983595, 1018470217, 1061158912, 1105380747, 1077242582, 1116733440, 1065353216, 1094713344, 1060465366, 1031798784, 1075261021, 1047651272, 1086324736, 1034594987, 1065353216, 1099396983, 1065842551, 1109393408, 1082130432, 1110797015, 1068801866, 1099396983, 1065353216]

def candidateBits : List Nat := [
  1065353216, 1108815453, 1081205705, 1119879168, 1068149419, 1098907648, 1064428488, 1020837670, 1065353216, 1036831949, 1076006748, 1024491374, 1054392102, 1020054733, 1049065335, 1092616192, 1065353216, 1103835955, 1052024650, 1082619767, 1048576000, 1009429163, 1053397798, 1025589893, 1065353216, 1013157433, 1042983595, 1008812677, 1061158912, 1105380747, 1077242582, 1116733440, 1065353216, 1094713344, 1060465366, 1031798784, 1075261021, 1047651272, 1086324736, 1034594987, 1065353216, 1030874056, 1065842551, 1109393408, 1082130432, 1120613171, 1068801866, 1099396983, 1065353216]

def original := pairs.zip originalBits
def candidate := pairs.zip candidateBits
def close (row : (String × String) × Nat) : Prop :=
  let expected := oracle row.1
  expected * (1 - tolerance) ≤ decode row.2 ∧
  decode row.2 ≤ expected * (1 + tolerance)
instance (row : (String × String) × Nat) : Decidable (close row) := by
  unfold close
  infer_instance

def badPairs (rows : List ((String × String) × Nat)) : List (String × String) :=
  (rows.filter (fun row => !decide (close row))).map Prod.fst

theorem roster_and_oracle :
    pairs.length = 49 ∧ originalBits.length = 49 ∧ candidateBits.length = 49 ∧
    ∀ unit ∈ names, ∃ factor,
      CssSemantics.CssUnitFactor.lookup unit = some factor ∧
      factor.dimension = .length ∧ 0 < factor.multiplier := by decide +kernel

theorem binary32_domain :
    (∀ bits ∈ originalBits, normalPositive bits) ∧
    (∀ bits ∈ candidateBits, normalPositive bits) := by decide +kernel

theorem original_exact_three :
    badPairs original = [("in", "q"), ("pc", "q"), ("q", "in")] ∧
    ((original.filter fun row => decide
      (decode row.2 < oracle row.1 / 2 ∨ oracle row.1 * (3/2 : Rat) < decode row.2)).map Prod.fst)
      = [("in", "q"), ("pc", "q"), ("q", "in")] := by decide +kernel

theorem candidate_all_within_bound : ∀ row ∈ candidate, close row := by decide +kernel

#print axioms roster_and_oracle
#print axioms binary32_domain
#print axioms original_exact_three
#print axioms candidate_all_within_bound
end AbsoluteFactorCertificate
