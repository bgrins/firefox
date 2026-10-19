# Independent normative check

Retrieved the current primary editors’ drafts on 2026-10-19 through the web tool; webspec-index is unavailable in this workspace.

- [Properties and Values computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time-behavior): registered dimensions are computed in canonical units; universal syntax preserves token-value behavior. Together with [absolute lengths](https://drafts.csswg.org/css-values-4/#absolute-lengths), the typed 1in oracle is 96px. This is independent of the patched implementation.
- [Values 5 substitution in properties](https://drafts.csswg.org/css-values-5/#substitution-in-properties): a sole CSS-wide keyword after replacement acts as the originally specified keyword. Missing var fallback to initial therefore uses the same registration initial value as direct initial.
- [Determining registration](https://drafts.css-houdini.org/css-properties-values-api-1/#determining-registration): script registration takes precedence over active stylesheet registration. [CSSPropertyRule](https://drafts.css-houdini.org/css-properties-values-api-1/#the-csspropertyrule-interface) exposes descriptor state separately from element computed style.

REACHED for the three ordinary failing cases. Universal initial 1in remains 1in; an omitted universal initial is guaranteed-invalid and serializes as the empty string. The parent 192px distinguishes inheritance from initial defaulting. No specification conclusion about same-effect keyframe dependency ordering is needed.
