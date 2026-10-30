# Completion is separate from semantic size cycles

The existing CSS dependency identity for an `em` value can remain FontSize while a `ch` consumer additionally requires final font metrics. This is a per-consumer distinction, not an upgrade of the semantic FontSize SCC to include every metric prerequisite.

```css
@property --size { syntax: '<length>'; inherits: false; initial-value: 0px; }
@property --metric { syntax: '<length>'; inherits: false; initial-value: 0px; }
.target {
  font-size: 20px;
  --size: 1em;
  --metric: 1ch;
  font-weight: calc(var(--size) / 20px * 700);
}
```

Size can complete independently, allowing `--size` to compute and Weight to become 700 before `--metric` reads the selected font. Folding Weight's selected reads into the FontSize node instead produces FontSize → Weight → `--size` → FontSize. That extra cycle is an implementation error, not a reason to default `--size`. The separate root-authored deterministic-font fixture will supply the observable discriminator; no browser result for this example is claimed here.

There is a different unresolved case:

```css
.target { --metric: 1ch; font-weight: calc(var(--metric) / 1px * 20); }
```

The registered value requires current metrics and Weight requests that same registered computed value. [PVAPI substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) specifies computed registered values; [PVAPI unit cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) explicitly lists FontSize/LineHeight edges. The [Values4 font-affecting parent-metric exception](https://drafts.csswg.org/css-values-4/#font-relative-lengths) does not by itself establish that an already-computed registered substitution may be recomputed against the parent. [Houdini issue 1080](https://github.com/w3c/css-houdini-drafts/issues/1080) identifies the missing registered-unit/Weight edge, and [CSSWG issue 9517](https://github.com/w3c/csswg-drafts/issues/9517) remains a design issue in the retrieved primary sources. The cycle policy is INCONCLUSIVE here. The native seam intentionally chooses none.

A scheduler must also propagate waits through generated computation prerequisites. For example, when resolving a selected Weight reference to registered `--lh: 1lh`, the LineHeight node may invoke ordinary ensure(Weight) through its generated dependencies. An active metric-preparation guard outside ordinary ensure does not protect that path. Conversely, if `line-height: 20px`, automatically treating all of LineHeight's conservative generated dependencies as semantic graph edges can reject an acyclic computation. Actual selected value/default readiness or a separate completion protocol is required.

The implementation checkpoint supplies a resumable declaration-selection part of that protocol. It does not supply a resolver for the returned reference request, a semantic-closed/computation-pending node representation, or scheduler liveness. Integration must preserve evaluated rollback reads and skip unreachable lower declarations; retain staged substitutions across waits; certify skipped-prefix stability; publish each property only when its actual inputs are final; and preserve independent size completion while metrics wait. It must not import ordinary generated links wholesale into semantic SCCs.

The proposed DFS-metadata snapshot shortcut was not implemented. Removing a temporary DFS suffix alone would not roll back computed custom/attribute publications, random/cache effects, or property application. Every retained result would require an actual closed-input proof. Likewise, clearing final Appearance flags, setting ensured while active, and treating an unresolved map entry as a final fallback are not repairs.

The earlier installed typed-attribute 8px observation remains a required baseline control. The published provider already re-scans resolved universal token dependencies in `VariableValue::new_resolved`, unlike assumptions one might make from a release result alone. No claim that the current published native branch fixes that case is made without its fresh baseline run.
