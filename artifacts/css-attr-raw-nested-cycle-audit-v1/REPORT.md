# Raw nested attr() audit

The installed Firefox 158 browser returns the outer fallback for five inputs whose current-spec trace predicts literal strings. Eight controls pass. The smallest case needs one attribute:

```html
<div data-foo="attr(data-foo)" style="--x: attr(data-foo type(*), abc)"></div>
```

Observed `getComputedStyle(element).getPropertyValue("--x")`: `abc`. The scoped draft prediction is `"attr(data-foo)"`. [SPEC-TRACE.md](SPEC-TRACE.md) follows the full property/substitution/attribute/guard/parsing chain and records its tooling limitation. This is a concrete conformance lead supported by release behavior and source correspondence; no fix is accepted, no security impact is asserted, and the existing regression oracle remains unchanged.

## Release observations

Actual outer session 52832 exited 0 (launch 9005d6, terminal 6d155b). The pinned installation is Firefox 158.0, build 20261007201254, release source stamp eb9a6e3a736802c8e080a76c44dc81f409d99d54. Its executable, XUL and application.ini hashes are unchanged across the run. Each case uses a fresh element, one `--x` declaration and two identical computed-value reads. No shared WPT fixture state is involved.

| Case | Observed | Draft prediction |
|---|---|---|
| Typed universal outer, bare self read | `abc` | Quoted original attribute text |
| Typed universal outer, explicit raw-string self read | `abc` | Quoted original attribute text |
| Typed string outer, bare self read | `abc` | Quoted original attribute text |
| Original two-attribute WPT case | `abc` | Two literal strings |
| Same two-attribute case with explicit raw-string | `abc` | Two literal strings |

The eight controls cover raw and typed literals, a genuine typed self-cycle, an acyclic bare read, a missing bare attribute, taken/unused bare fallbacks containing typed cycles, and already quoted function-looking text. All match their recorded predictions. `release-runtime/RESULT.json` preserves exact input and output strings rather than only these classifications. The standalone page is `probe/probe.html` with `probe/probe.js`; it displays the observations without WPT dependencies.

The runner adapts the existing project LaunchServices helper. It creates a fresh profile, owns an ephemeral loopback server, launches a separate headless/no-remote installed Firefox, and identifies cleanup targets by exact executable plus full profile path. It rechecks ownership before signaling and separately reaps the launcher/server. The owned parent was PID 80362; launcher exit was 0; cleanup reported no errors and removed the profile. No user profile, shared objdir, Mach command, WPT runner, live native/test/metadata file, index or HEAD was modified. The loopback probe requires process/network permission; the actual run received it.

## Native correspondence

The current upstream source fetched through Searchfox, committed HEAD snapshot and current local snapshot all contain the same `can_chain` condition in `visit_value_references`:

```rust
let can_chain = next.is_attr_with_type() || matches!(var, VarType::Attr(..));
```

Inside an attribute node, that admits a bare/raw-string reference into `visit_link`, which can set `self_ref` or update a lowlink. A typed attribute containing `attr(data-foo)` therefore acquires a same-attribute graph edge even though the primitive raw substitution reads literal DOM text. `get_attr_value_for_cycle_resolution` parses attribute text as a VariableValue; the resulting SCC processing can invalidate the attribute before normal `substitute_one_reference` reaches its raw-string return.

The candidate animation work changed pending/context plumbing, but did not introduce this condition. HEAD/local differ elsewhere; this audit does not claim byte equivalence of entire source files or that installed release was built from these snapshots. The independently installed release reproduction establishes that the behavior is not dependent on the current uncommitted animation prototype.

Removing the `matches!(var, VarType::Attr(..))` term is an investigation direction, not a reviewed repair. A correct change must still resolve typed dependencies and **used fallbacks of missing raw attributes**, while preserving the existing hash-order regression and namespace behavior. Skipping all bare references and their fallbacks would need separate scrutiny. No native patch was applied here.

## Why the WPT disagrees

The disputed row was introduced by [WebKit bug 310641](https://bugs.webkit.org/show_bug.cgi?id=310641), through [WebKit PR 61321](https://github.com/WebKit/WebKit/pull/61321), committed as 205b80c8b56b on 25 March 2026 and exported in [WPT commit 7a585ef3249c](https://github.com/web-platform-tests/wpt/commit/7a585ef3249c5c385edeb3738526efa54d9cc0bd) on 16 April 2026. The captured patch checks/marks an in-progress attribute before dispatching its raw-string case. That implementation ordering explains the test's expectation; it is not normative evidence that bare reads must create a cycle. Retrieved review comments contain no substantive discussion adjudicating this particular raw-string branch. No claim of exhaustive issue search is made.

[Mozilla bug 2049009](https://bugzilla.mozilla.org/show_bug.cgi?id=2049009) later fixed attribute-map hash iteration order and added a variable-order control. Its comments distinguish eager type-less attribute seeding from nested reference traversal; its patch's latter behavior needs care in this narrower raw case. The WPT `abc` row already existed before that Mozilla change. The captured upstream WPT matches our archived local and HEAD test bodies.

The latest published Values 5 Working Draft retrieved from W3C is dated 11 November 2024; it predates the current guarded-context machinery and has a different algorithm structure. The current Editor's Draft route is the oracle used here, not an attribution of all modern cycle rules to that old snapshot. [CSSWG issue 11500](https://github.com/w3c/csswg-drafts/issues/11500) and merged [PR 12165](https://github.com/w3c/csswg-drafts/pull/12165) explain lazy fallback evaluation and guarded contexts. They do not supply an exception making the raw return recursively substitute its attribute text.

## Next gate

Obtain an independent review of the raw-return trace against the historical WPT expectation, then prepare a separate candidate repair and WPT covering all five observed variants plus the eight controls. Retain the genuine typed-cycle and missing-attribute fallback checks. Compare original/candidate locally only after the root releases the native tree. This audit alone neither changes the regression oracle nor increments the accepted-fix ledger.
