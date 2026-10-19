# Reproduce the narrow predicate companion

From any directory, using the pinned Lean 4.35.0-rc4 macOS ARM64 executable:

```sh
python3 /absolute/path/to/css-tokenizer-escaped-newline-repair-v1/check.py \
  --lean /absolute/path/to/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /private/tmp/escaped-newline-fresh
```

The output directory must not exist. Python 3, the `patch` utility and that Lean distribution are required. No network, Rust build, Firefox build, browser or mutable checkout input is used. The checker authenticates all local inputs before invoking retained helpers, reapplies/reverses the exact native patch on copies, checks checksum semantics, freshly replays the signed dispatch component and its mutants, admits the candidate's unchanged dispatch patterns, compiles eight predicate theorem audits and rejects two semantic mutants. It independently recounts the retained browser raw statuses.

Commit inventory: all paths in MANIFEST.json plus MANIFEST.json and FREEZE.json are the complete source/evidence companion. Exclude replay output directories, generated .olean files and the separate ongoing name/escape directory. The subsequent repair commit consists of third_party/rust/cssparser/src/tokenizer.rs, third_party/rust/cssparser/.cargo-checksum.json and testing/web-platform/tests/css/css-syntax/identifier-start-escaped-newline.html. The first two are native.patch; the last is the exact retained WPT. Root performs final build/browser gates and signing.
