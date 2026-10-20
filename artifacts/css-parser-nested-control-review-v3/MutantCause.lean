import LinkPaths
set_option autoImplicit false
theorem wrong_expected_result_refuted :
  LinkPaths.run [112,97,114,97,109,40,45,45,120,44,41,44,112,97,114,97,109,40,45,45,121,44,41] ≠
    (false,false,23,none,[],0) := by
  rw [LinkPaths.two_empty_values]
  decide
#print axioms wrong_expected_result_refuted
