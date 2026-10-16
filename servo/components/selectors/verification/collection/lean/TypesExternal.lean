/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Aeneas
@[expose] public section

@[rust_type "servo_arc::Arc"]
structure servo_arc.Arc (T : Type _) where
  value : T

@[rust_type "servo_arc::HeaderSlice"]
structure servo_arc.HeaderSlice (H : Type _) (T : Type _) where
  header : H
  entries : List T

@[rust_type "servo_arc::ArcUnion"]
inductive servo_arc.ArcUnion (A : Type _) (B : Type _) where
  | first : servo_arc.Arc A → servo_arc.ArcUnion A B
  | second : servo_arc.Arc B → servo_arc.ArcUnion A B
