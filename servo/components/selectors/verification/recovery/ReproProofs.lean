/- This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Model

open Aeneas Aeneas.Std Result BorrowedTrait

theorem invoke_exact (s : Borrowed) (value owned : Usize)
    (hv : s.value + 1#usize = ok value) (ho : s.owned + 1#usize = ok owned) :
    invoke s = ok ({ value, owned }, fun future => { s with value := future.value }) := by
  simp [invoke, generic, Step_inst6_impl6.step, hv, ho]

#print axioms invoke_exact
