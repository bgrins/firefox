# Numeric width for exact rectangle traversal

Nine Lean kernel results establish a bound needed by the traversal redesign.
If the rectangle-relative origin and every cumulative coordinate fit signed 32 bits,
then each translation (coordinate minus origin) lies between −4,294,967,295 and
4,294,967,295. The same bound holds for an ancestor-only sum obtained by
subtracting the first cumulative coordinate. Both fit signed 64 bits, independently
of the number of frames. The trace theorem quantifies over arbitrary finite
bounded traces; it does not assume a frame-count bound.

Two concrete witnesses explain why the first proposal was insufficient:

- Leaf −2,000,000,000 and ancestors +1,400,000,000,+1,400,000,000 have valid total
  prefixes and final 800,000,000, but ancestor sum 2,800,000,000 exceeds signed 32 bits.
- Rectangle origin −2,000,000,000 with positions +1,500,000,000,+1,000,000,000 has
  valid prefixes and final 500,000,000, but translation 2,500,000,000 exceeds nsPoint.

The retained v1 helper uses checked rectangle-relative accumulation. Its complete
body and the manual mapping are in SOURCE-BRIDGE.json/V1-HELPER.cpp.txt. This
component proves integer inequalities. It does not establish native frame paths,
heap lifetime, CheckedInt representation, cross-document scaling, graphics
clipping, IEEE behavior, browser reachability, or a successor implementation.
The original full safe-origin and allocation obligations remain open.

Two early source drafts failed parser/elaboration checks; a third compiled with
an unused-premise warning. The final reconstruction statement relates translation
to the cumulative coordinate, and all nine audits compile without warnings.
All development sources/logs remain; only final compile.stdout is accepted.

Replay with isolated Python verify.py, the external FILES.json SHA256, and
--output pointing to a fresh external directory. Installed Lean libraries are
admitted; this is not a compiler or standard-library reproduction proof.
