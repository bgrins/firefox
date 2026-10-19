# Timeline proof source commit

Commit the 40 source-manifest inputs and SOURCE-MANIFEST-v1.json under
css-timeline-pseudo-axis-proof-v1, plus this guide, before the separate three-file
Gecko/WPT repair. Generated programs, browser profiles and historical logs are
not replay prerequisites and do not belong in the source-only companion.

Within this checkout, use the interpreter pinned in TOOLCHAINS-v1.json:

```sh
/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S artifacts/css-timeline-pseudo-axis-proof-v1/verify.py --expected-manifest 239760bee07c24b078c67a42531595e7c4ac1e6fd85b3ce42b88875ccc99d155 --clean /private/tmp/timeline-proof-new-replay
```

Choose a fresh output path. The child sandbox denies network and checkout reads
apart from the pinned Lean toolchain. The toolchain/dependency paths are explicit
local prerequisites, not a vendored hermetic compiler distribution. The source
manifest also supports --replay with a fresh output directory when independently
packaged; --clean additionally locates this checkout to deny its contents.

Root source-only replay5268 and independent16045 each passed all50commands,
72exported theorems,2228scenarios/2876rows pervariant and11semantic native/Lean
mutants. Independent raw checking covered5752rows and1580preservation scenarios;
12additional concrete Lean witnesses check admission/noninterference nonvacuity.
Root authenticated and replayed the independent checks successfully.

The claim is typed resolved-source/snapshot/cache consistency over finite
admitted sampling sequences, connected to bounded complete native extraction.
Ranked acyclic ancestry, provider ownership and numeric domain are explicit.
Real layout/refresh/lifetime/APZ, root/fieldset mappings, arbitrary named
view-transition lookup and IEEE/TimeDuration implementation are not proved.
Native trace agreement is bounded. Preserve these limits from the producer and
independent reports when presenting the result.

The repair contains ScrollTimeline.cpp/.h and
scroll-timeline-pseudo-writing-mode.html only. Exact original/candidate WPT:
16failures become40passes;24existing passes,1expected failure and1reftest pass
remain unchanged. Orthogonal root controls give128equal times pervariant.
Four recreation/opacity diagnostic failures remain separate.
