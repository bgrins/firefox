# Final sealed-source review

The provisional source review in `REPORT.md` is now confirmed against the producer's final capsule. **Approve the exact native proposal and WPT source for root integration/build/testing.** No source or WPT oracle blocker remains. This is not final browser/native-binary acceptance.

Authenticated identities:

- Producer FREEZE: `dc9453175d210471da6595fe189311d932a8011f4edd2c2265bd89112dd8d0a8`.
- Producer MANIFEST: `bff4e313ba82a721da30258b592de2b52a920a9ab7acabf0eaa76536331d27dc`, all 160 entries authenticated before invoking helpers.
- Complete candidate: `d38d0831d0e4acc68e0a7064f03674de81e0e6e6f35e0243ab349305015dd794`.
- Native patch: `05d56eb8a7aa831be1856db9b378d5116eb775216cf9f06f2555f8258bafef3c`.
- WPT: `7fac42de6c2b882d669f0806f613f0e1e454cdd2090723ad1d12237c9e6531f9`.

All seven files copied during initial review match the final authenticated bytes. The independent static replay regenerated the exact native candidate/patch and WPT, applied and reversed the patch in an artifact copy, matched the prior reviewed helper, checked exactly two new-constructor calls and byte identity of all other original code, checked JavaScript syntax, and observed 21 distinct test registrations without executing their callbacks.

The producer's retained scanner command receipt records exit 0, 49 fixed cases, and depth 300,000 on a requested 65,536-byte Rust thread stack. Its result authenticated 156 inputs before the four evidence files were added to the final 160-entry manifest. This review authenticates that retained evidence but does not relabel it as an independent rebuild. Root is separately replaying the final capsule and owns the Gecko build/browser pair. The precise harness adapters and feature differences remain documented in `REPORT.md` and `input/scanner/BOUNDARIES.json`.

The accepted claim remains reconstruction of unit dependency metadata for admitted valid, fully substituted output at the two sinks. Incomplete scan compatibility, allocator/compiler/provider trust, full lexical proof, graph correctness, browser semantics outside the tested cases, and performance remain explicitly bounded as discussed in the report. The selected-output Lean component is supporting conditional algebra, not a proof of this Rust tokenizer.

## Review replay

After authenticating this review's seal, run:

```sh
python3 artifacts/css-resolved-summary-native-independent-v1/check.py \
  --output /tmp/resolved-summary-native-review-fresh
```

Use a new output directory. This authenticates the review and imported producer closure, then performs only static generator/patch/JavaScript checks. It does not compile Rust, launch Firefox, run WPT callbacks, or touch the shared source tree. The producer's own `input/check.py --scanner --output NEWDIR` is the separate standalone Rust rebuild command.
