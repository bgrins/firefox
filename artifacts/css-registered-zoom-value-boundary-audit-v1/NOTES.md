# Registered-value computation and copy boundaries

Source-only audit, no native patch or new browser result. The outer registered `Value<Component>` conversion is a promising common boundary for fresh values; a helper-only change to `SpecifiedValue::compute` would miss direct calls on parsed/retained ASTs.

| Path | Captured behavior | Canonical-storage obligation |
| --- | --- | --- |
| Registration initial cache | Stylist::rebuild_initial_values_for_custom_properties calls PropertyRegistration::compute_initial_value; typed initial calls SpecifiedRegisteredValue::compute | Fresh conversion must be canonical; universal stays raw |
| Ordinary/substituted values | SpecifiedValue::compute parses and invokes outer to_computed_value | Canonicalize exactly once |
| A retained admitted AST | Prepared value calls to_computed_value after SCC settlement | Same outer conversion, preserve readiness/taint |
| Parsed animation declaration | CustomAnimatedValue::from_declaration calls v.to_computed_value directly | Same outer conversion; compute helper alone is insufficient |
| Unparsed animation declaration | Calls SpecifiedValue::compute for typed registration | Same boundary |
| Animation from existing style | CustomAnimatedValue::from_computed clones | Already canonical, no second removal |
| Animation CSS-wide initial/inherit/unset | Clones initial or inherited custom value | Already canonical, no second removal |
| Applying animated custom property | AnimationValue::Custom inserts value.clone into custom properties | Preserve canonical value; unlike ordinary longhand path, no ToAnimatedValue unzoom here |
| Animation interpolation | CustomAnimatedValue delegates Animate to stored optional registered Value | Keep canonical operands/results; nested matrix behavior still needs audit |
| Recascade | to_declared_value converts computed registered Value back via from_computed_value | Canonical px must remain canonical specified px before next fresh computation |
| var export | Value::to_variable_value serializes stored value directly | Requires canonical storage |
| CSSOM export | Custom property getter recursively resolves stored value | Preserve other resolution, do not unzoom canonical lengths again |
| Style range query | QueryStyleRange::resolve_value clones stored registered Component for Custom, but directly computes Component::Length for a literal query operand | Literal/universal/function operands must use the same canonical length mode/normalization before comparison |

The style-query path is a concrete additional consumer: compare_values compares stored Component::Length and independently computed Component::Length directly. It does not pass the literal operand through outer registered Value. A canonical-storage implementation must adjust that path or establish equivalent operand scaling; a storage-only change is not complete. This is an unrun potential regression boundary, not a separately counted bug.

Two implementation strategies remain under review. An explicit outer Value conversion can call a pure recursive length mapper afterward, using the computation's actual scale. A potentially smaller strategy is an explicit outer conversion entering a scoped canonical-length computation mode; existing inner derives recurse and specified length leaves remove the actual zoom without replacing font/root/style context. The latter requires a complete audit of length conversion bypasses, nested scope restoration, mixed calc operations and existing dependency/effect behavior. Counter comparison agent owns that audit. Neither strategy is implemented or proved here.

Fresh initial/direct/deferred/prepared/animation conversion and canonical copying can share one invariant. A full source proof of every producer, transforms, image semantics, numerical rounding, query behavior or CSS conformance is not claimed. The upstream fetches pin the inspected bodies; current checkout equivalence is not independently established for these captures. The locally captured registered Value source and sealed A proposal provide branch context.
