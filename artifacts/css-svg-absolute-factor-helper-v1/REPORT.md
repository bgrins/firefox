# Compiled SVG absolute-unit factor audit

The exact retained `SVGLength::GetAbsUnitsPerAbsUnit` and `IsAbsoluteUnit` bodies compile and execute under Clang UBSan plus integer sanitizers. Compile and run exit0; stderr is empty. All49 factors are collected, with **46 close matches and three gross mismatches**. This confirms coefficient errors in actual compiled float evaluation, not browser/API reachability or a repaired implementation.

| Conversion | Compiled coefficient | Exact CSS coefficient | Actual / expected |
|---|---:|---:|---:|
| Q to inches | 0.02204860933125019 | 5/508 | 2.2401387081 |
| Q to picas | 16.933332443237305 | 15/254 | 286.7377627055 |
| Inches to Q | 45.35433578491211 | 508/5 | 0.4464009428 |

The independent oracle starts from CSS Values4 section6.2: inch96px, cm96/2.54px, mm one tenth of cm, Q one fortieth of cm, pica one sixth of inch, point one seventy-second of inch. For source S and target T the coefficient is px(S)/px(T). `ORACLE.json` retains all49 exact reduced numerator/denominator pairs. C++ evaluates each oracle as one double division of exactly represented small integers; it does not read the native table for expected values. Primary source reread23October2026: https://drafts.csswg.org/css-values-4/#absolute-lengths (draft24August2026).

The tolerance is4·FLT_EPSILON relative, about4.77e−7. This deliberately accepts existing abbreviated decimal literals, not an invented normative CSS precision rule. Among the46 close entries the maximum exact decimal discrepancy is7/60000000 (the px-per-mm literal); rounding these positive normal values to binary32 adds at most2^−24 relative error, and the double oracle division at most2^−53. Their envelope remains below the selected tolerance. The largest observed compiled close error is9.09e−8; the smallest of the three gross errors is0.553599. `NUMERICS.json` also independently reconstructs all49 binary32 literal values and matches the compiled output exactly.

`constants.inc` is generated directly from the pinned SVGLength WebIDL constant declarations plus the source’s internal Q=11 declaration. The compiled predicate is tested for all65536 uint16 values: NUMBER1 and the inclusive PX5…Q11 range are accepted; other values are rejected. Fifteen additional checks exercise NUMBER’s px alias, including NUMBER/NUMBER. The function’s original indexing lambda, float literals and assertion expressions remain byte-identical. A minimal class declaration supplies only the two static signatures; this is an extracted-function harness, not a full Gecko translation-unit or browser build. Actual Mozilla assertions/config headers come from the existing objdir, and dependency hashes are retained.

Source pins cover SVGLength.cpp/.h and SVGLength.webidl; before/after source checks pass. The authoritative preceding audit manifest was authenticated before extraction. No factor was rewritten. All owned executable, dependency and dSYM products were hashed and removed after terminal execution. Native files, canonical Lean library, parent index and browser state were not modified.

The separate API audit owns public reachability: Q may enter as parsed text even though public conversion target11 is rejected. Consequently the wrong Q→in and Q→pc coefficients are plausible public conversion defects, while this harness alone does not establish a public call to the wrong in→Q entry. Browser evidence and any native repair remain separate gates. Discovery was source/numeric inspection; no Lean discovery or accepted bug count is claimed.
