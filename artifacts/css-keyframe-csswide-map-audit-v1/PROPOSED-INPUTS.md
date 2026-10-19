# Proposed browser inputs (not executed)

Use an attached fresh div per case, registrations as shown, default replace composition, duration1000, fill both. Pause and set currentTime500. Read computed source before asserting sink. Cancel and remove each animation/element afterward. Use numeric assertions after parsing the computed value; all chosen results are exact integers.

## A: computed dependency versus endpoint-local maps

Register `--source`: `<number>`, inherits:false, initial10; `--sink`: `<number>`, inherits:false, initial0. Target base `--source:42`. Run:

```js
target.animate({
  "--source": [sourceStart, "90"],
  "--sink": ["var(--source)", "calc(2 * var(--source))"]
}, {duration: 1000, fill: "both"});
```

| sourceStart | Source priority | Expected computed source | Expected computed sink |
|---|---|---:|---:|
| `10` | normal | 50 | 75 |
| `initial` | normal | 50 | 75 |
| `10` | important (`42 !important`) | 42 | 63 |
| `initial` | important (`42 !important`) | 42 | 63 |

The first pair makes literal10 and initial10 equivalent as source endpoints. The important pair prevents either endpoint's source declaration from replacing the dependency's actual computed42. Do not expect sink95 merely because source endpoints are10 and90: that is the endpoint-local interpretation this diagnostic distinguishes. Base-only substitution would instead give63 even without important; the current mixed map can give111 in the initial case if the supplied seed is42.

Optional independent no-source-animation control: animate only the sink, retain source42, expected63. This validates var/calc endpoint typing without source animation ordering. Do not count it as testing CSS-wide map skips.

## B: initial wrapper

Register `--n`: `<number>`, inherits:false, initial10. Set target base42. Animate `--n` from14 to each endpoint:

| Endpoint | Expected midpoint |
|---|---:|
| `10` | 12 |
| `initial` | 12 |
| `var(--missing, initial)` | 12 |
| `var(--missing, 10)` | 12 |
| `var(--missing)` | 12 |

Ensure --missing is absent. No source animation is needed. If fallback-initial alone differs from its direct/literal controls, that supports the Universal initial wrapper mechanism. Sample endpoints0/1000 only as needed: equal endpoint serialization alone does not establish equal interpolation representation.
