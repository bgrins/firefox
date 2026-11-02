# Expected values

Scenario: ordinary div, no zoom override, parent literal font-size20px then30px; unregistered --size independently equals those lengths; registered --len has <length> syntax and independent initial0px. Attribute data-length is var(--len). The independent controls must pass before numerical results are interpreted.

1. [Variables replacement](https://drafts.csswg.org/css-variables-1/#resolve-var) step2 obtains --size's computed value and step5 returns it. The variable-size FontSize therefore receives the phase's absolute length. It does not depend on --len.
2. [Fonts4 font-size](https://drafts.csswg.org/css-fonts-4/#font-size-prop) defines percentages against the parent's computed size and font-size as inherited. Thus100% and the omitted declaration on this div both use the phase's parent size; the literal control supplies the same value directly.
3. [PVAPI relative-unit dependencies](https://drafts.css-houdini.org/css-properties-values-api/#dependency-cycles) adds registered em→FontSize. The independent size routes above supply no reverse custom dependency on len. The registered1em computes to the phase size.
4. [Values5 attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution) step6 substitutes the raw attribute before parsing its requested <length> syntax. The resulting phase length succeeds at this step. It later fails the Appearance grammar, whose initial noninherited value is none; the attr fallback auto is not selected merely because the containing property rejects the successfully substituted length. This last branch reuses the sealed portable probe's primary trace.

Expected endpoint: len/fontSize20px then30px and appearance none for all four callbacks. This manual primary-prose trace supports these ordinary acyclic expectations; it is not a proof of native scheduling or genuine metric-feedback policy. PRIMARY.json records the current primary reads and webspec-index access limits. No new browser result is asserted.
