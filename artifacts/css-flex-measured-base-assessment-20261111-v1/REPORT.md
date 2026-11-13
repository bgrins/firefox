# Measured flex bases lose large shrink cancellation

Reproduced on the current local browser with all three preceding pending flex repairs applied. The new 24-case WPT has 18 failures and six passing small controls. No native repair is applied yet, and this is not an additional accepted or committed fix.

The test uses a 1000px block-size column flex container, one flex:1 1 auto item with min-block-size:0, and two ordinary block children. Each child's block size is 1000px, 10000000px, 15000000px or 17000000px. It covers horizontal-tb, vertical-lr and vertical-rl, in both column directions. All six 1000px controls pass. Each larger case retains millions of pixels of item block size instead of shrinking to 1000px. For two 15000000px children the observed item size is 12104302.93333435px. The expected final size is small; this is not a test requesting an unrepresentable final rectangle.

Root cold WPT session50742 terminated at81b0ac exit1, with harness OK, 18 FAIL and six PASS subtests. BuildID20261111174437 matches the preceding validated build. BEFORE-INPUTS.json authenticates the unchanged native source, Firefox launcher, XUL, application.ini and new WPT. The first sandboxed attempt stopped at the mach environment lock before dispatching tests; its error is retained separately. Full command output and WPT reports are retained.

The initial twelve-case probe in release Firefox158 also demonstrates measured sizes beyond the preferred coordinate bound. That probe includes negative-margin cases affected by older arithmetic behavior, so those rows are not independent evidence for a new margin defect. The final local WPT uses no margins, borders, padding or gaps. The owned probe tab was closed; the original about:blank tab was preserved.

## Source cause and formal boundary

ResolveFlexibleLengths resets each unfrozen main size to its flex base, computes sizeDelta in AuCoord64, then currently adds nscoord(sizeDelta.ToMinMaxClamped()) to the base. ToMinMaxClamped limits the delta itself to the preferred coordinate interval. A measured content base can exceed that interval. Clipping the negative adjustment before adding it loses the cancellation even when the intended final size is easily representable.

The accepted caller target's DeltaAdmissionTarget explicitly assumes base <= preferredMax. Its conditional theorem may be valid while this native producer violates that premise. This is evidence against promoting that conditional result to universal native coverage, not a counterexample to the stated Lean theorem. Root requested a separate exact mathematical counterexample from the caller proof worker. The arithmetic counterexample must not be described as a machine-code proof of this browser execution.

For example, in exact mathematical app units, base1800000000 and desired60000 require delta=-1799940000. Clipping delta to -1073741823 produces726258177 rather than60000. Small pixel/app-unit conversion differences explain why these exact illustrative integers are not claimed as an instrumented native trace.

The repair must retain the wide base-plus-adjustment calculation until a justified narrowing point. It must also account for the optional aLineInfo diagnostic difference, full min/max semantics including sentinel values, and existing large growth and negative-margin controls. Simply assuming every measured base is at most preferredMax would exclude the reproduced caller. No chosen final narrowing policy or diagnostic storage repair has been validated yet. Searchfox discovery of the additional mMainDeltaSize consumers timed out; no consumer absence is inferred from those failures.

Tentative priority P3: extreme-size layout correctness with a small expected final item. No memory-safety, security or measured performance claim. Discovery came from auditing a formal theorem's native premise and browser reproduction, before a new proof or repair.
