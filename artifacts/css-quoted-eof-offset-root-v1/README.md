# Quoted EOF endpoint repair

The repair records the existing final-backslash deletion while consuming the
quoted token and subtracts it when constructing enclosing reference endpoints.
The final serializer uses that same decision. Earlier completed sibling
references keep their offsets. Serialized CSS bytes remain unchanged; parity
and escaped-terminal-quote content defects are deliberately separate repairs.

Root inspected the complete changed recursive parser and final serializer,
the source extraction/generator and facade boundary, all ten Lean lemmas,
checker and mutation, and the final WPT oracle. Fresh replay reproduces
22 original panics versus 40 successful candidate cases; removing the endpoint
correction restores those 22 panics. Root independently checked the exact
formatter-only transformation to the source compiled by Gecko.

The browser pair changes the 38-case endpoint WPT from a content-process crash
to 38 passes. All 34 other outcomes remain identical. The aggregate test command
still returns 1 for eight separately tracked semantic failures. WPT lint passes.
The exact two-file patch applies and reverses at both the current stack parent
and upstream base 976279105b2e78b8666a959eb3f25c9176cefaf8. Browser execution
uses the shared local tree, not an isolated upstream build.

The kernel result is an endpoint-arithmetic component under terminal-token,
cumulative-recovery-suffix and source-boundary premises. Native admission is
manual source review plus finite extracted execution. UTF-8/usize validity,
parser and provider behavior, allocation and compilation remain explicit
assumptions. This does not prove all of VariableValue parsing or CSS substitution.
Discovery came from source review during formal-provider work, followed by
browser reproduction. The Lean lemmas explain the correction; they did not
independently discover this defect.

Evidence: producer source capsule, formatted-source binding, fresh root replay,
independent review, browser PAIR-RESULT.json and PATCH-CHECK.json. The native/WPT
commit contains only custom_properties.rs and quoted-eof-fallback-endpoints.html;
this evidence belongs in its preceding companion commit.
