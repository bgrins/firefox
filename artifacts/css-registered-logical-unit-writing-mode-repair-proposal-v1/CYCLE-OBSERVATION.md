# Remaining cycle-policy boundary

The naive lexical flag addition creates a new false cycle for:

```css
@property --mode {
  syntax: "<length> | horizontal-tb | vertical-rl";
  inherits: false;
  initial-value: vertical-rl;
}
.target {
  --ready: horizontal-tb;
  --mode: var(--ready, 1cqi);
  writing-mode: var(--mode);
}
```

The selected admitted value is horizontal-tb; it has no contextual length dependency. The isolated candidate prepares only values carrying the new WRITING_MODE demand and removes that demand after actual substitution/admission says it is absent. It preserves all old font/line-height/color flags. The four additional WPT controls cover this unused-fallback case and selected invalid grammar, for cqi and vi. These four controls are unexecuted.

A distinct unresolved observation is `<length>` --n:100vi with writing-mode:var(--n) under a vertical parent. The writing-mode value is necessarily invalid after substitution, but the proposed graph has a real --n→WritingMode→--n cycle. The current Properties and Values API relative-unit cycle section explicitly lists font/line-height edges, not writing-mode. It does not itself establish that both nodes should default here. Do not invent a conformance oracle for this case or accept the new cycle policy based on the 16 simple tests. It needs a deliberate normative/interop decision or earlier longhand admission handling. A selected custom-property grammar check alone does not settle this longhand-grammar issue.

Additional genuine unit cycles are discussed in CSSWG issue 13189 for if()/style-query contexts; that issue is related context, not authorization to generalize the registered custom-property SCC policy.

Primary references:
- https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles
- https://github.com/w3c/csswg-drafts/issues/13189

The artifact has no source dependency on the held admission overlay, but remains experimental and is not yet independently landable as a fully validated fix.
