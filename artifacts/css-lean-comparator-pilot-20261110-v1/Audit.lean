import Challenge

open NumericDigits

example : ((scan [⟨48, by decide⟩, ⟨57, by decide⟩, ⟨65, by decide⟩]).digits.map Fin.val,
    (scan [⟨48, by decide⟩, ⟨57, by decide⟩, ⟨65, by decide⟩]).rest.map Fin.val) = ([48, 57], [65]) := by decide

#print axioms NumericDigits.scan_reference
