# Retained caller rebased over declaration capacity

The only change from sealed caller-v1 is `DeclarationIndex = u16` → `u32` in its cascade candidate. Provider and properties/mod.rs are byte-identical to v1. The captured published cascade base is `832d08549227e20f88f1bede253824b75b66a58b4adb2b7efc357cc52915f1f5`, matching the capacity change root reports signed as `e86b64866cdc5e2260ba9be08c45756fd96e21bb`. This package does not independently verify that commit or bind a future live checkout.

SOURCE-ROLES.json pins three captured preimages and three candidate bodies. CAPACITY-REBASE.patch contains the single alias change; native.patch contains the full three-file overlay against the captured published base. The saved check authenticates both patches and applies/reverses each with zero fuzz in owned temporary scratch. It does not modify live sources or run Git, Mach, Cargo or a browser.

The 11 positive tests and nine compiled behavioral false controls belong to **v1's extraction** (its saved CHECK and final result are referenced). They were not rerun here and are not a v2 native pass. All v1 integration limits remain: valid multi-URL typed-attribute publication still encounters an explicit invalidation guard; fixed-context provenance and native lifetimes need validation; unsupported scheduling waits and terminal assertions remain; dynamic/inherited/default size readiness is not repaired merely by installing this caller.

## Native check handoff

Root first runs the separate instrumented sizeforms diagnostic. Only after its owner has terminated and restoration is independently verified may root materialize a fresh three-role typecheck owner using the established overlay/restoration mechanism. Reject source preimage mismatches. Guard and restore **all three files**, including properties/mod.rs; the old two-role owner is insufficient unchanged. Bind the actual then-current HEAD, canonical controls, app/source/extras/binaries/flags and configured backend. Reauthenticate Mach routing and Cargo manifests rather than treating this package's historical plan pins as fresh admission.

Use the existing command, retaining its entire unfiltered output and actual process terminal:

```sh
/Users/bgrins/venvs/firefox/bin/python ./mach cargo check -p geckoservo -j 2 --message-format-json --locked --offline
```

Mach exit zero is insufficient. Require exactly one Cargo `build-finished` record with `success: true`, no error-level compiler diagnostics, and library compiler-artifact records for both style and geckoservo bound to the authenticated manifests, source paths and configuration. Fresh-cache artifacts are acceptable only under those exact input bindings. Missing JSON, interrupted output or compiler errors fail the check. Preserve warnings and actual helper logs.

Cargo/backend writes are expected; they do not certify a rebuilt browser. Restore all admitted source identities on success or failure, then perform the existing full app/extras/binaries/flags/HEAD/index/control checks. No browser result, scheduler correctness or acceptance follows from compilation alone. This package adds no executable owner or enabled policy.
