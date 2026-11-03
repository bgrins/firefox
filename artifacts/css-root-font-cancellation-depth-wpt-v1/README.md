# Supplemental cancellation depth fixture

Four pending WPT callbacks extend the exact existing eight-case fixture without changing it: an existing child using rem keyframes below one or four fixed-font, unanimated wrappers, each with no intervening read or an explicit root read. Depth counts only the inserted `.fixed` wrappers between body and target, not html/body.

The whole nested subtree is created in iframe srcdoc before load. Every wrapper is checked for its fixed 13px font, 19px line height, lack of animations, and actual ancestry before the disturbance. The existing child's 11px style, root's 23px/37px style, existing pseudo, and initial-rem/root-em calibration remain checked. No wrapper is inserted or read between cancellation and the target animation. The root-read control intentionally reads before target animation construction.

The paused helper, disturbance/cancel/barrier block, and target first-read/ready/two-RAF/settled block are byte-identical to the parent fixture. Both samples are recorded before their numerical assertions. Each callback expects 46px from the restored root's 23px rem basis, but neither baseline nor candidate has run these new cases. They are supplemental proposed conformance checks, not demonstrated regressions or new accepted bugs. A baseline failure is required before calling a case a regression test; initial native eight-case/full34 validation proceeds independently.

`INPUTS.json` pins the new page and the two existing sealed harness resources. No WPT runner, browser owner, metadata override, native source, or installed WPT tree is supplied or changed. The source check parses and registers four callbacks with an inert Node VM, verifies exact critical parent blocks and input hashes, and never executes callback bodies or a browser. Genuine WPT lint/manifest preparation and both browser runs remain pending.

Actual source check: `05662e / exit 0`, saved in CHECK.log. PARENT-DELTA.patch records the complete fixture adaptation. References include the sealed source proposal solely as the exact fixture origin; this fixture does not assert that its unbuilt native candidate is correct.
