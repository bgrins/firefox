# Discovery and exact-source provenance

Read-only Searchfox discovery identified the following current functions/templates. Searchfox revision differs from e86; the exact evidence is the pinned e86 snapshots and new `git show` captures in this package.

- [Context](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/computed/mod.rs#193), query receipt 418b01.
- [Generated cascade_property](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/properties/helpers.mako.rs#132), discovery 9aeb2a/eaf40c.
- [AnimationValue::from_declaration](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/properties/helpers/animated_properties.mako.rs#288), discovery 9aeb2a.
- [FontSettings conversion](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/computed/font.rs#1048), discovery 69809b.
- [Numeric leaf conversion](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/specified/calc.rs#151), discovery 76ec53; tree mapping at #1462.
- [StyleBuilder::calc_line_height](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/properties/properties.mako.rs#2624), discovery c41879.

The three initial e86 template/cascade captures were obtained by actual a59429/0; the fourth properties.mako.rs capture by 09059b/0. Each command used `git --no-optional-locks -c core.fsmonitor=false show e86b64866cdc5e2260ba9be08c45756fd96e21bb:PATH`, writing only new artifact files. No active native source was read as the baseline, edited, or executed. Native length/number/calc/Context source comes from the already sealed snapshots referenced in SOURCE.json, including the exact length file in the sealed probe.

Two narrow Searchfox searches for direct variation descriptor/computation callers returned no matches (487189/9753e2). They are not evidence of absence; the positive generic conversion and generated callers above are the report's basis. This is not an exhaustive caller graph proof.
