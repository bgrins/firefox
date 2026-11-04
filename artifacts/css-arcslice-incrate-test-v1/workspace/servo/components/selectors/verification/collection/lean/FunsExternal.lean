/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Aeneas
public import Normalized.Types
@[expose] public section
open Aeneas Aeneas.Std
set_option linter.dupNamespace false

@[rust_fun "core::borrow::{core::borrow::Borrow<@T, @T>}::borrow"]
def core.borrow.Borrow.Blanket.borrow {T : Type _} (value : T) : Result T :=
  .ok value
