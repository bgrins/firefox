# Possible stale attr-cycle expectation

Source identity: `css/css-values/attr-cycle.html`, section “Multiple attributes cycling simultaneously in bare attr() form”. The four-file roster includes the byte-identical upstream/local body.

```css
--x: attr(data-foo type(*), abc);
```

Attributes:

```text
data-foo = attr(data-bar type(*), fallback)
data-bar = attr(data-foo) attr(data-bar)
```

The existing test expects `abc`. Under the captured [27 October 2026 attr substitution algorithm](https://drafts.csswg.org/css-values-5/#attr-substitution), step 5 returns a CSS string for bare/raw-string attr() before step 6 enters guarded typed substitution. Starting from `--x`, the typed data-foo lookup enters its attribute context; its typed data-bar lookup enters a different context. Both bare lookups within data-bar return literal strings. Neither re-enters typed substitution for the already active attributes. Type `*` accepts that resolved token sequence, so neither outer fallback is selected.

The resulting sequence is two strings containing the original attribute texts:

```css
"attr(data-bar type(*), fallback)" "attr(data-foo) attr(data-bar)"
```

This is a manual normative prediction, not a browser observation or a formal/native proof. The guard and post-substitution checks remain effective for genuinely taken typed cycles. The generic explanatory note about resolving attr(foo) must be read with the normative raw-string return branch. A separate reduced probe and cross-engine/spec review should adjudicate this row before changing its oracle or counting a bug. The prototype regression run should retain and report its actual behavior without silently rewriting the fixture.

The primary Values 5 HTML is retained by the completed fallback-version trace; REFERENCES.json pins that source and its manifest. No source or metadata changes were made for this caveat.
