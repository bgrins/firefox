# Primary spec trace

Checked current Editor's Drafts with web tooling on 2026-10-19.

- https://drafts.csswg.org/css-values-5/#substitution-in-properties — a sole CSS-wide keyword after property replacement is interpreted as the specified keyword. The `var(--missing, inherit)` fallback therefore reaches explicit inheritance; no unusual revert interpretation is involved.
- https://drafts.csswg.org/css-cascade-5/#inherit — explicit inherit selects the inherited value, irrespective of the property's default inheritance setting.
- https://drafts.csswg.org/css-cascade-5/#inheriting — inherited value is the parent's computed value; the root uses initial. Shadow-tree and pseudo inheritance have their own parent rules, not universal DOM parenthood.
- https://drafts.csswg.org/css-cascade-5/#valdef-all-unset — unset selects initial for a noninherited property, explaining the 1px negative control.

Verdict: REACHED for the ordinary connected parent/child test. After the parent computes 20px, the child's explicit substituted inherit must compute 20px. Retaining 10px contradicts that value selection. This trace establishes the observable obligation; the internal flag and invalidation mechanism come from source inspection, not from normative text.
