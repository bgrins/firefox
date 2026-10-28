# Random indices at typed numeric parsing boundaries

This successor retains the registered whole-alternative transaction and expands the same Result transaction to all seven current CalcNode typed convenience entry points: length-or-percentage, percentage, length, number, angle, time, and resolution. The three changed native paths remain parser.rs, properties_and_values/value.rs, and values/specified/calc.rs. The first two candidate bodies are byte-identical to v1.

Each boundary parses an owned numeric tree and consumes it through its matching `into_*` conversion. An Err returns no retained AST. Both parse failures and final type rejection restore the random counter to that call's entry value; success retains every index consumed within that successful branch. Nested failure therefore preserves indices already assigned by an enclosing successful branch instead of resetting to zero. Pure flag setup for length-or-percentage is now inside the transaction too; it has no counter effect.

The source audit identifies additional speculative callers beyond the earlier opacity/line-height union: radial-gradient percentage input first attempts a length, and rotate's vector input first attempts an angle. The parent separately reports both wrong-index outcomes from its fresh local observer, with six matching controls; that runtime record is not authored or certified by this package. Source review motivates covering the uniform typed finalizer family, without claiming all seven have independently reproduced failures.

Successful typed parsing can still be rejected later by its caller. That is why the registered whole-alternative transaction remains necessary for trailing tokens and later repetition-member failure. This patch does not establish that every speculative parser boundary, parser side effect, panic path, or caller-level rejection is transactional.

The independent contextual numeric line-height zero repair remains a separate one-file proposal and is not included here. Existing ordinary eleven-case tests retain their numeric-line-height specified-key-only assertion, so its unrelated computed-zero defect cannot make a false calibration claim.

Exact three-path forward/reverse/reapply and Rust formatting passed in 3670f5/0; private scratch was removed. No native typecheck, linked build, WPT execution, acceptance, or production source mutation was performed for this successor.
