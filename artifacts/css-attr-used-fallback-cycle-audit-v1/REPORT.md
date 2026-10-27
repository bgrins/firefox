# Used non-type attribute fallback cycle audit

Status: new bug lead with installed-release reproduction and current-source correspondence. No native patch, WPT change, accepted bug count, security finding or branch-browser claim.

## Observation

Installed Firefox 158.0, build 20261007201254, source stamp eb9a6e3a736802c8e080a76c44dc81f409d99d54. The isolated standalone probe completed with exit 0. All 13 cases had identical repeated --x reads. Seven disagree with the current-spec prediction; six controls agree.

| Cases | Observed --x / color | Spec prediction |
|---|---|---|
| Missing bare attr, self fallback | red / red | invalid / green |
| Missing explicit raw-string attr, self fallback | red / red | invalid / green |
| Invalid number attr, self fallback | red / red | invalid / green |
| Invalid px attr, self fallback | red / red | invalid / green |
| Missing px attr, self fallback | red / red | invalid / green |
| Missing bare attr, mutual fallback | red / red; --y also red | both invalid / green |
| Same mutual case, reversed declaration order | red / red; --y also red | both invalid / green |

Controls: direct var self cycle and missing type(*) attr self fallback invalidate; missing bare attr with an acyclic literal or ready variable fallback succeeds; present raw and valid number attrs ignore unused cyclic fallbacks. The full expressions, computed values and colors are in release-runtime/RESULT.json.

## Source correspondence and prior fixes

The Searchfox upstream custom_properties.rs snapshot stores fallback names in a separate VariableFallback.references. It propagates summary flags, not a flat list of fallback names, to the enclosing reference list. In upstream and archived HEAD/local cascade.rs, visit_value_references skips a bare/unit attr in a custom-property node at `if !can_chain { continue; }` before examining fallback dependencies. Its fallback variable edge therefore has no alternate flat representation there.

The archived substitute_one_reference handles an unresolved universal reference recursively. Its seen-name check returns no primary and permits a var fallback; this can produce red unless cycle traversal has already marked the actual cycle. This explains the observed shape but does not prove the installed binary contains these exact source snapshots.

The adjacent raw-nested lead is the opposite edge error: treating raw attribute contents as evaluated dependencies can create a false cycle. Its separate sealed artifact is css-attr-raw-nested-cycle-audit-v1. A repair must classify both primary evaluation and used-fallback evaluation correctly.

| Existing commit | Exact scope | Why these probes are different |
|---|---|---|
| 7822bb6d17b1381cdb3e56deb20c5ec3e078adec | Prepares type() attribute providers throughout syntactic fallback trees in update_attributes_map | Does not add bare/unit attr fallback var edges to cycle traversal. Its WPT includes bare attr with a typed-attribute fallback, not the self/mutual var cases here. |
| e3ba54f6f826fe265eb5bc4731f66f64465dd47c | Uses occurrence-specific type() parsing to decide primary validity before following a fallback | Eligibility check is conditional on is_attr_with_type() and remains downstream of the earlier bare/unit skip. Its cyclic-fallback WPT uses type(<length>). |

Both complete native diffs and WPT diffs are archived here. Neither patch directly repairs this edge omission. This is a source-scope conclusion; release failure alone is not proof of failure in the current branch. A built-branch reproduction and candidate comparison remain acceptance gates.

## Execution and limits

probe/probe.html runs standalone. run_browser.py uses a newly created owned profile and an ephemeral loopback HTTP port, launches the installed application headlessly through LaunchServices, captures results, verifies pinned source/binary identities, terminates only parents matched to the exact binary/profile, reaps the launcher, closes its server and removes the profile. RESULT records stable=true, errors=[], profile_removed=true and launcher_exit=0. It does not establish independent exit observations for every browser child process.

No Mach, WPT harness, shared objdir, user profile, native source, metadata, index, HEAD or bug ledger was modified. Native snapshots may differ because the parent owns an active typed-demand proposal; their hashes preserve what was inspected. Parent work is not a mutation by this audit.

Next gate: replay these cases on the branch build after the parent releases it, keeping direct-var, typed-fallback and unused-fallback controls. If confirmed, add a standalone native/WPT fix that also preserves existing fallback-preparation, typed-eligibility, namespace and attribute-order regressions. Do not weaken the existing attr-cycle WPT oracle on the strength of the adjacent raw-nested lead alone.
