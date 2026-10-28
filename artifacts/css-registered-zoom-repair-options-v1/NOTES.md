# Zoom repair options: bounded source audit

No native patch or validation claim. This note supplements the sealed normalization contract and its explicit factoring hypothesis.

The captured specified length implementation has materially different paths: `FontBaseSize::CurrentStyle` copies already computed font size; `InheritedStyle` applies `effective_zoom_for_inheritance`; `Lh` reads `StyleBuilder::calc_line_height`; nonroot `Rem` and root metric units apply builder effective zoom to device values; container-relative lengths use the queried container size directly. Therefore temporarily setting only `builder.effective_zoom` to one does not establish uniformly unscaled computed inputs. It can leave em/lh references scaled while changing absolute/rem conversions.

The fetched upstream `Context` has no existing general unscaled-registration computation mode. Its contextual services also carry rule-cache, container-query and element effects. Replacing it with a default/dummy context would lose those services. A new scoped mode would need every length-producing path audited and would still require producer/consumer and CSSOM boundary work.

A pure post-computation length normalization traversal is a plausible implementation boundary because it preserves the established evaluation context. It is not yet a complete patch: prove which scale each length result carries, preserve percentage terms, inspect nested images/transforms (including numeric matrix representations), and cover retained AST, parsed declarations, initial cache, inherited/CSS-wide copies and animation/recascade. General `ToResolvedValue` cannot be reused blindly because it also resolves currentColor. These limitations remain from the sealed model; none is discharged by merely fetching more source.

Next native work should start with exact scalar absolute-length producers and both export paths, with paired narrow WPTs for literal, selected fallback, initial/inherit/unset and cross-zoom copies. Broader syntax cannot silently retain a different storage convention. No accepted fix increment or claim about upstream/release reproduction is made.
