# Selected-color candidate V4: lifetime declaration failure

Actual owner 50372/cbc269/d0eb31 exited 1. The native build exited 2 with Rust E0106: the new SubstitutionInput enum omitted the lifetime parameter of dom::AttributeTracker. No browser ran. The isolated V4 borrow analogue used a simplified tracker and did not exercise that real type requirement. This is a candidate compile error, not a new browser defect.

Independent reviewer 46693/056f06/973d76/0 verified all source preimages and identities, the original application, semantic index/staging, process cleanup and retained backup. Root rechecked source/application and backup inventory, removed 1,008,605,176 backup bytes and refreshed only raw-index bookkeeping (40887/ed3462/78616f/0). Native acceptance remains false; HEAD and 149 accepted fixes are unchanged.

The actual tracker definition was located with Searchfox and captured from local dom.rs after verifying equality to HEAD. The next minimal correction gives the enum separate input-borrow and tracker-context lifetimes. All42 browser cases remain unchanged and unexecuted for this candidate.
