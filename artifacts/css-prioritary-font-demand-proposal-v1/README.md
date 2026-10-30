# Preserve font computation demand in registered dependencies

This is a two-file, transport-first native prototype against the exact a6f4 selected-declaration candidate. It carries computation demand into the dependency-consumption path without changing the semantic CSS graph identity. It is not a complete scheduling repair, has not been compiled in Stylo or run in a browser, and is not a publication candidate. Native source, Git, index and application state were not changed.

`CANDIDATE-DELTA.patch` applies to a6f4 plus its published provider. `native.patch` applies to the published provider/cascade directly and therefore includes the earlier selected-declaration candidate as well as this prototype. The candidate postimages, both parents and hashes are retained. The preexisting candidate regressions are not claimed fixed.

## Implemented code

ReferenceFlags already used all eight bits. It is widened to u16 and gains metric/orientation flags for current and root font units. Existing low eight bits remain unchanged. em/rem demand computed size; ex/cap and their root counterparts demand font metrics; ch/ic and their root counterparts also demand orientation. lh/rlh conservatively request oriented metrics because line-height may require metrics. That last classification is a readiness upper bound, not a new semantic cycle rule.

`FontDependencyDemand` is an ordered four-value join: None, ComputedSize, FontMetrics, OrientedMetrics. `NonCustomDependency` pairs this demand with the unchanged SingleNonCustomReference. The semantic enum still has three entries, its map still has three slots, and FontUnits still maps to FontSize. `for_each_non_custom_dependency` decorates the existing semantic iterator; it does not create a Family, Weight or writing-mode cycle node.

Registered dependency consumption and the existing implicit LineHeight-to-FontSize link now share `visit_non_custom_dependency`. This records the stronger request on Cascade before following the same existing graph link. The aggregate survives graph-root resets and is initialized in both Cascade constructors. It is explicitly a requested-input record, not a completed-readiness marker. Later weaker requests cannot downgrade it.

Existing References flag unions carry the new flags through the same alias/attribute/reference paths. This deliberately preserves current inventory and fallback behavior, including existing overapproximation. It does not settle the unused-unit-fallback policy, remove fallback flags, or claim a complete selected-token dependency analysis. Root units only contribute own-element demand at the root; non-root root-unit dependencies remain external as before.

## Deliberate boundary

No ordinary or prepared ensure, substitution, computation, CSS-wide application, generated dependency list or SCC publication method is changed. The helper calls the original visit_link with the original identity and arguments. It never reports an unresolved prerequisite as ready and never adds a skip or early-publication escape. Consequently the prototype by itself does not prevent the existing ordinary ensure from reentering a graph-owned property. It retains information needed for that later repair instead of inventing a false readiness result from the ensured bit.

A real consumer must still distinguish requested from fulfilled state, preserve stronger demands that arrive after a size-only computation, and resolve active waits without turning every generated scheduling dependency into a CSS cycle. It must also share reached var/attr/rollback evaluation between ordinary and graph-owned application. None of those unfinished steps is hidden behind this aggregate field. Font-weight, width/style and used metric readiness are not guaranteed merely because FontSize has been ensured.

## Source authentication and current-element path

Read-only authentication 61ef4e compared the local provider/cascade byte-for-byte to their frozen published bodies before copying them. It separately retained a6f4 as the candidate parent. Seven prior Searchfox discovery snippets exactly occur in the current local font/length/context/gecko bodies. AUTHENTICATION.json records hashes and source identities; the root-reported HEAD is attributed, not a Git query made by this agent. New Searchfox has reorganized substitution code, so those newer locations were not silently substituted for these authenticated local bodies.

CONSUMER-BRIDGE.json records further exact local excerpts: ParserContext::with_property_declaration sets the parse property ID/random index; registered-value computation toggles canonical-unit scope; ordinary NoCalcLength conversion explicitly uses CurrentStyle; current metric queries pass the current whole font and used size. Registered font-relative conversion then removes effective zoom for canonical units. A registered 1ch value with a separate literal font weight therefore has a current-element metric read. This supports a discriminator, not an observed weight-related defect or proof that font metrics were read too early in a particular run.

The existing font-property-unit-cycles tentative WPT also has distinct cases: custom values consumed by font-* calc test parent-unit behavior, while no-cycle custom values compare to current-element units. It does not use a deterministic family with distinct weight-specific metrics. Historical unit-token/dependency fixes and the image fix are separate from the proposed selected-weight readiness test; the commit-description lookup is not an exhaustive absence proof.

## Validation

Rustfmt parsed and formatted both candidate files. Both base-relative and a6f4-relative patches replayed forward and backward with zero fuzz and exact hashes; all temporary patch directories were removed.

An isolated Rust harness compiles the exact changed flag/iterator/join methods with the real vendored bitflags crate. Only unavailable derive macros/import types are adapted; CSS parser strings and PrioritaryPropertyId are small stubs. Three tests cover unit/root classification, all 8192 flag/root combinations preserving the old semantic projection, and 64 join triples plus alias/later-demand cases. Four deliberately incorrect variants (metric collapse, orientation collapse, root leakage and downgrade) compile but fail those assertions. This is not native Stylo typechecking, DOM evaluation, actual cascade ownership or a browser result.

The two changed type names occur only in the local provider/cascade files in the bounded source census 681f8c. No explicit flag-bits numeric serialization use was found there; widening a field still requires real compilation and layout/performance review. The native graph lifetime, alias selection, old flag inventory and actual publication correspondence remain separate obligations.

The separately sealed FontDemand Lean model proves least-sufficient demand joins for abstract consumer inputs. Its readiness premises and fixed input states remain assumptions; this code only implements and transports the demand join, not those premises.
