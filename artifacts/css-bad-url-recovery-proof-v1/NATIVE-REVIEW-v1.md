# Independent review: bad-URL whitespace recovery

18 October 2026. **Accepted for the bounded native correction and its WPT.**
The paired rebuilt browser run repairs all 28 failing cases and preserves the
36 new passing controls and eight adjacent outcomes. This review does not
accept a formal companion: no Lean proof or Rust refinement was reviewed here.
Root retains responsibility for final packaging, lint and independent landing.

## Specification trace

Scenario: an ordinary unregistered custom property is parsed from inline
`style.cssText` or a stylesheet block. Its value begins with unquoted `url(a`,
then whitespace, a backslash and `)`, followed by apparent declarations and a
second unescaped `)`. There is no image-loading dependency.

1. [CSSOM cssText setting](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-csstext)
   parses the supplied declaration block after clearing previous declarations.
   [Declaration-block parsing](https://drafts.csswg.org/cssom/#parse-a-css-declaration-block)
   invokes Syntax's list-of-declarations parser and validates declarations.
   The stylesheet entry reaches the same tokenizer while consuming its block.
2. [Ident-like token consumption](https://drafts.csswg.org/css-syntax-3/#consume-an-ident-like-token)
   recognizes `url(`. The next content starts with `a`, not a quote, so the
   unquoted URL algorithm applies. The escaped `_a` WPT prefix takes that same
   path after consuming an escape.
3. In [URL consumption](https://drafts.csswg.org/css-syntax-3/#consume-url-token),
   the whitespace branch consumes whitespace, then inspects the next point.
   Since it is neither `)` nor EOF, it transfers control to bad-URL recovery
   without consuming that next backslash.
4. [Bad-URL recovery](https://drafts.csswg.org/css-syntax-3/#consume-remnants-of-bad-url)
   recognizes the valid escape and consumes the escaped `)` as data. The
   following apparent green declaration stays inside the bad URL. Recovery
   terminates at the later unescaped `)`.
5. The bad URL invalidates its custom-property declaration. The original red
   declaration remains; the final `--after:present` declaration is parsed.
   With two backslashes instead, they form one escaped backslash and the first
   `)` terminates recovery; the later green declaration survives.

**Verdict: REACHED.** The next non-whitespace backslash belongs to the recovery
scanner. Consuming it in the caller changes which declarations survive.

Rejected interpretations: this is not a quoted `url()` function; initial `a`
excludes that branch. An escaped `)` is not a terminator. A hexadecimal escape
whose decoded value is `)` likewise is data, not a delimiter. The final custom
property sentinel alone cannot distinguish correct recovery from the defect;
the surviving color supplies that distinction.

The authoritative CSS Syntax editor draft is dated 16 October 2026. I read
the retained current HTML and deciding algorithms and checked the live primary
URL. CSSOM and Syntax HTML plus fetch headers are retained. Anchors used above
exist in those documents. The spec-trace and frontend skills were read;
webspec-index and a Read tool were unavailable in this agent environment, so
the trace uses directly inspected algorithms rather than a claimed graph-tool
enumeration.

## Native correction and callers

The exact diff in `third_party/rust/cssparser/src/tokenizer.rs` replaces the
fallback binding `b` with `_` and removes its `parser.consume_known_byte(b)`.
It preserves the call to `consume_bad_url(parser, start_pos)`. The independently
checked original snapshot matches the syntax scout's original source.

Both branches of `consume_unquoted_url_internal` call `consume_url_end` at
whitespace: the borrowed fast path and the owned buffer path after an escape
or null. The WPT's `a` and escaped `_a` prefixes exercise these distinct paths.
The whitespace scanner itself still consumes space, tab and normalized
newlines, consumes a literal closer, and handles EOF. Only its fallback
handoff changes.

For ordinary bytes, deferring consumption is equivalent: the recovery helper
immediately consumes them. For a backslash, the helper must inspect its next
byte and skip an escaped backslash or right parenthesis. Pre-consuming the
backslash changes parity and explains both premature and delayed recovery.
No additional payload, parse-state or style-invalidation change is needed.

The inspected provider chain is `nsDOMCSSDeclaration::SetCssText` through
`Servo_ParseStyleAttribute`, style declaration parsing, `RuleBodyParser`, custom
property parsing, and cssparser token access. The stylesheet path shares the
tokenizer while its declaration/rule retry policy differs. The minimal witness
is ASCII, so it does not rely on a disputed UTF-16-to-UTF-8 conversion. The
Rust scanner receives valid UTF-8 `&str`; universal provider correctness is
outside this review.

The companion `.cargo-checksum.json` modification changes exactly the
`src/tokenizer.rs` digest and agrees with the candidate bytes. This is a
vendored dependency repair. Upstream submission/version updating remains a
separate maintenance action; none was performed or authorized by this review.

## Why the optimized recovery helper remains valid

`consume_bad_url` need not decode every escape to find its terminating suffix.
Only raw `)` and backslash can change termination. Hex digits and their optional
trailing whitespace cannot contain an unescaped `)`; scanning their bytes
individually reaches the same recovery boundary. A decoded U+0029 or U+005C
does not become a new syntactic delimiter or escape introducer.

- Backslash followed by `)` or backslash must consume both bytes together.
- Backslash before LF is not a valid escape; scanning backslash then newline
  is correct. CR, CRLF and FF are normalized newline forms, and the existing
  `consume_newline` updates their positions consistently.
- Backslash before EOF reaches EOF in either algorithm.
- Valid UTF-8 multibyte sequences contain no ASCII `)` or backslash bytes.
  The byte scanner consumes them with `consume_known_byte`; the raw slice ends
  at EOF or after an ASCII closer, a code-point boundary. The patch moves the
  first byte's consumption into that same helper; it does not introduce an
  unsafe intermediate string slice.
- Null preprocessing changes a data scalar, not a recovery delimiter.

An independently written checker uses regex escape units for the scalar
reference and a separate byte scanner matching the optimized endpoint policy.
It checks **271,453** strings of length zero through five over twelve symbols,
including UTF-8, null and newline forms, plus eleven targeted six-digit hex,
CRLF, non-ASCII escape and EOF cases. There are no endpoint mismatches. These
are finite Python model comparisons, not extracted Rust execution, a proof of
line/column arithmetic, or an arbitrary-input theorem.

## Browser evidence

The initial artifact page records 32 observations through two API entry
points. Its literal strings, scalar values and UTF-8 bytes are consistent.
My independently computed URL suffixes agree with all expected colors.
Fourteen candidates mismatch, eighteen controls match, all final sentinels
survive, and CSSOM specified colors agree with computed colors. Both mismatch
directions follow backslash parity. The receipt's five input pins remain
stable; the historical browser identities are retained rather than compared
to the now rebuilt browser.

The 64-case WPT expands that matrix with both borrowed and owned prefixes.
It asserts the final sentinel, CSSOM color and computed color. The assertions
are sufficient to distinguish the proposed defect from total parse loss,
missing stylesheet application or merely different bad-URL serialization.
No asynchronous image or timing oracle is involved. Test cleanup removes both
the target and stylesheet between cases. I found **no necessary additional
browser cases** for this two-line repair. EOF, UTF-8 and wider hex cases belong
in the scanner/formal companion; the current neighboring WPTs also exercise
EOF behavior.

| Capture | New WPT | Adjacent subtests | Meaning |
| --- | --- | --- | --- |
| baseline-v1, exit 1 | 28 FAIL, 36 PASS | 5 PASS, 3 expected FAIL | Original behavior reproduced |
| patched-v1, exit 1 | 28 FAIL, 36 PASS | Identical | Ineffective rebuild; not fix validation |
| patched-v2, exit 0 | 64 PASS | Identical | Recompiled and relinked candidate |

The three existing failures are the ident, dimension and URL escaped-EOF
serialization expectations already present in `escaped-eof.html.ini`.
All four harness files finish OK. The paired identity comparison has 28
FAIL→PASS, 41 PASS→PASS, 3 FAIL→FAIL and 4 OK→OK outcomes; no missing identities
or regressions. I recomputed statuses directly from each raw JSONL and compared
them to the corresponding receipt.

Twelve common nonbinary inputs, including the new test, adjacent tests,
metadata and testharness resources, have identical hashes across baseline and
paired runs. The common changing pins are only tokenizer, Firefox executable
and XUL. Every nonbinary pinned source copy is authenticated. The paired runner
diff adds checksum pinning and changes the accepted phase name; its test
command and test list are unchanged. That runner difference is explicitly
retained rather than called byte-identical.

The first forced Cargo log still showed no cssparser compile. The second
explicitly records compiling cssparser v0.38.0, followed by a successful
relink/build. The build log retains an export-monitor KeyError despite its
successful footer; root confirms actual terminal exit 0. The rebuilt binary
hashes differ and the expected behavioral transition occurs. This is practical
source/build/run evidence, not cryptographic proof of the complete compiler
pipeline. Root reports paired process 79528 exited 0, forced Cargo 9783 exited
0, and relink 99606 exited 0.

## Acceptance and reproducibility

Accepted: the demonstrated recovery family, minimal native handoff correction,
matching vendor checksum and 64-case WPT. No novelty, release-version impact,
security, performance or all-CSS correctness claim follows. There is one bug
family, not 28 separate defects. Formal scanner proof/capsule acceptance and
root's packaging gates remain separate.

`INPUTS-v1.json` maps 82 retained inputs to complete local snapshots. The
authoritative replay is:

```
python3 artifacts/css-bad-url-recovery-independent-v1/check.py --paired --out /tmp/bad-url-independent-check.json
```

Compare it byte-for-byte with `CHECK-paired-v1.json`. `CHECK-v1.json` is the
earlier baseline-only receipt before additional paired evidence was retained;
it is historical, not the final replay target. `FREEZE-v1.json` authenticates
this report, checker, evidence and receipts. The checker verifies the freeze
when present. No native/WPT edits, builds, browser runs or git operations were
performed by this reviewer.
