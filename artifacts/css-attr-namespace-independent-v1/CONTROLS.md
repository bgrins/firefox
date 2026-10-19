# Proposed WPT additions — UNEXECUTED

Common setup: `@namespace a "urn:a"; @namespace b "urn:b"; @namespace c "urn:a";`. Construct attributes with setAttributeNS and check their namespace reads. Put qualified CSS expressions in that stylesheet, not element.style (which has no namespace map). Let `A = attr(a|x type(<length>), 5px)` and `B = attr(b|x type(<length>), 7px)`. Unless specified use width:A;height:B, then an independent reversed-declaration-order element. No font or pixel tolerance is required for computed absolute lengths.

| Case | Attributes and declarations | Expected width / height | Obligation |
| --- | --- | --- | --- |
| Qualified var chains | a:x=`var(--av)`, b:x=`var(--bv)`, --av:13px; --bv:37px | 13px / 37px | Preserve namespace through graph traversal and successful apply |
| Qualified to null same-local edge | a:x=`attr(x type(<length>))`, null x=13px, b:x=37px | 13px / 37px | Do not collapse distinct nodes into false self-cycle |
| Real cyclic A, valid B | a:x=`var(--loop)`, --loop:`attr(a|x type(<length>))`, b:x=37px | 5px / 37px | SCC removal cannot invalidate B |
| Invalid A, valid B | a:x=`var(--missing)`, b:x=37px; --missing absent | 5px / 37px | Failed substitution removes only A |
| URI alias | a:x=13px; width:A; height:`attr(c|x type(<length>),7px)` | 13px / 13px | URI identity independent of prefix |
| Null versus named same local | null x=13px; b:x=37px; width:`attr(x type(<length>),5px)`; height:B | 13px / 37px | Null namespace is a valid distinct bucket |
| Unknown prefix | null x=23px; a:x=37px; --good:13px; width:`attr(unknown|x type(<length>),var(--good))`; height:`attr(a|x type(<length>))` | 13px / 37px | Unknown must not alias null or suppress fallback |
| Dynamic B then A | Start a:x13px,b:x37px; set b:x53px; remove a:x; restore a:x19px | 13/53 then 5/53 then 19/53 (px) | Qualified cache reconstruction and missing-attribute fallback |

For the null-chain case, also test an independent all-null acyclic chain with distinct names and a truly self-cyclic null attr as controls. For cycle isolation, compare both namespaces swapped (valid A, cyclic B →13px/7px) if the first pair exposes ordering sensitivity. Do not expand into a large matrix without a concrete remaining failure.

To test Unknown's *dependency* fallback rather than only a literal/var value, use `--loop: attr(unknown|x type(<length>), var(--loop)); width:var(--loop,5px)`. Expected width5px: the unknown primary fails and the fallback creates a real custom-property self-cycle. A wrong early continue can miss that edge. This is separate from the simple unknown-prefix value test.

These expectations follow independent qualified attribute lookup, typed substitution and cycle failure/fallback semantics. No nested attribute text contains a prefixed attr name; bug 2021110's missing namespace context is not used as an oracle. All fixtures require parse/readback calibration; a rejected declaration is a failure, not an optional support exit.
