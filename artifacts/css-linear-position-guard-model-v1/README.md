# Optional linear() position guard

This small post-discovery model checks a guard over two optional positions. Each position is absent, known (present and context-free resolution succeeds), or deferred (present and context-free resolution fails). Four declarations are kernel checked over this three-state domain. They establish that the fixed guard accepts exactly when every present position resolves, exhibit the old first-present guard accepting a known/deferred pair, show that the fixed guard never expands old acceptance, and preserve all optional known inputs. Both absent positions are valid for this guard; they do not imply that the entire linear() grammar is valid.

The definitions cover all nine state pairs. Some pairs, such as absent first with present second, may be excluded by the actual parser's structural invariant; including them in the abstract contract does not assert native reachability. Two false controls must be rejected: old guard soundness and replacing the all-position conjunction with an any-position disjunction. No arbitrary numeric values, floating-point operations or CSS output calculations are modeled.

Source inspection found the masked second endpoint before this model. The root's subsequent isolated installed-release observation recorded START without RETURN, an explicit content-process crash/SIG11 log, and parent exit245 before cleanup; the literal control returned. There was no Rust panic text. That browser evidence is separately pinned and is consistent with, not a dynamic proof of, the unwrap source trace. Lean neither discovered the defect nor executed or explains the crash signal. No new bug count, security classification, native acceptance, compiler result or Rust refinement theorem is claimed.

The manual source correspondence and assumptions are in MAPPING.md. In particular, the abstraction assumes a stable classification between the guard and later use. It does not prove Percentage::resolve purity, grammar admission, preference/context gates, Rust iterator behavior, unwrap semantics, memory safety, process behavior or all easing consumers. It does not settle whether contextual easing must be accepted or how it obtains its computation context.

Replay from the repository root with an absent output directory:

```
python3 -I -S -B artifacts/css-linear-position-guard-model-v1/replay.py /private/tmp/linear-position-guard-replay-unique
```

The script authenticates the existing Lean 4.35.0-rc4 binary, uses private temporary scratch, audits all four declarations and requires both false controls to fail specifically because `decide` finds a false proposition. It refuses to overwrite output and removes scratch. validation/CHECK.json is the completed author replay; no canonical Lean library or native source was changed.
