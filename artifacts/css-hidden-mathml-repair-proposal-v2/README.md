# Proposed MathML hidden-query repair, independent partition

The native proposal remains one MarkSubtreeDirty() call at the existing hidden-parent early return. The final landing WPT contains the four internal-mrow owner cases: row/leaf-first selection, each visible and hidden. Geometry reads and assertions are unchanged from the captured original eight-case diagnostic. No logging or unused global result publication remains.

The four root-block owner cases remain in the original diagnostic as interaction controls. nsBlockFrame can skip their MathML children before the new MathML guard runs; accepted block repair107 covers that separate path. Their passing result on the preserved working build does not prove standalone independence. This partition makes the native fix and its own regressions reviewable without assuming107.

Run committed HEAD versus only this MathML repair with the exact final four-case WPT. Expected two visible passes and two hidden failures should become four passes; report any deviation without changing expectations. Then check original-eight interaction and relevant existing controls with accepted block handling present. Already-dirty-root barriers, native lifecycle and provider correspondence remain explicit limits. This is an untested proposal, not acceptance.
