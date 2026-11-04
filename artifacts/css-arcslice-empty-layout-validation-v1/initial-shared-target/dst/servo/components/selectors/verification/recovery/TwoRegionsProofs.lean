/- This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Model

open Aeneas Aeneas.Std Result BorrowedTrait

theorem invoke_exact (s : Borrowed) (first second owned : Usize)
    (hf : s.first + 1#usize = ok first) (hs : s.second + 1#usize = ok second)
    (ho : s.owned + 1#usize = ok owned) :
    invoke s = ok ({ first, second, owned },
      (fun future => { s with first := future.first }),
      (fun future => { s with second := future.second })) := by
  simp [invoke, generic, Step_inst6_impl6.step, hf, hs, ho]

#print axioms invoke_exact
